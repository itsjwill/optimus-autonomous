#!/usr/bin/env python3
"""
Optimus Trading Brain - Autonomous AI-Powered Trading Intelligence

This is the main entry point for the autonomous trading brain.
Runs every hour via cron to:
1. Read trade data from brain.db
2. Run the TradingTeam AI agents (Analyst, Optimizer, RiskGuard, Executor)
3. Make autonomous parameter decisions
4. Apply approved changes to bot configs
5. Log everything back to brain.db

Usage:
    python run_trading_brain.py              # Run one cycle
    python run_trading_brain.py --daemon     # Run continuously
    python run_trading_brain.py --dry-run    # Analyze but don't apply
"""

import os
import sys
import json
import asyncio
import sqlite3
import argparse
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add optimus to path
sys.path.insert(0, str(Path(__file__).parent))

from optimus.agents import TradingTeam

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [OPTIMUS-BRAIN] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
BRAIN_DB = Path("/root/data/brain.db")
DECISIONS_FILE = Path("/root/data/optimus_decisions.json")
BOT_CONFIGS = {
    "billy": Path("/root/src/strategies/billy_coder_v4.py"),
    "blood": Path("/root/src/strategies/liquidation_bounce_v5_1.py"),
    "reaper": Path("/root/src/strategies/reaper.py"),
    "phantom": Path("/root/src/strategies/phantom_v2.py"),
}

# Slack webhook for notifications
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_DEV")


class TradingBrain:
    """
    Autonomous trading intelligence powered by Optimus AI agents.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        # Use multi-model mode for optimized agent performance:
        # - TradeAnalyst & Optimizer: Claude Sonnet 4 (reasoning)
        # - RiskGuard: Claude 3 Haiku (fast, cheap)
        # - Executor: Claude Sonnet 4 (important decisions)
        self.team = TradingTeam(
            use_multi_model=True,  # Each agent uses its optimal model
            verbose=True
        )
        self.decisions_today = 0
        self.max_decisions_per_day = 3

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(BRAIN_DB))
        conn.row_factory = sqlite3.Row
        return conn

    def get_trade_data(self, hours: int = 24) -> str:
        """Get recent trade data from brain.db."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

        # Get recent trades
        cursor.execute("""
            SELECT bot, symbol, direction, entry_price, exit_price,
                   pnl, pnl_pct, peak_roe, hold_time_minutes,
                   param_rsi, param_z_score, param_regime,
                   hour_of_day, day_of_week, notes
            FROM trades
            WHERE exit_time > ? AND bot NOT LIKE 'backfill%'
            ORDER BY exit_time DESC
            LIMIT 100
        """, (cutoff,))

        trades = [dict(row) for row in cursor.fetchall()]

        # Get shadow trades (what-if scenarios)
        cursor.execute("""
            SELECT symbol, direction, skip_reason,
                   hypothetical_pnl_pct as potential_pnl
            FROM shadow_trades
            WHERE created_at > ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (cutoff,))

        shadow_trades = [dict(row) for row in cursor.fetchall()]

        # Get whale signals
        cursor.execute("""
            SELECT symbol, bias, long_pct, whale_count, timestamp
            FROM whale_signals
            ORDER BY timestamp DESC
            LIMIT 10
        """)

        whale_signals = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return json.dumps({
            "real_trades": trades,
            "shadow_trades": shadow_trades,
            "whale_signals": whale_signals,
            "period_hours": hours
        }, indent=2, default=str)

    def get_current_params(self) -> Dict[str, Any]:
        """Get current bot parameters from config files."""
        params = {}

        # Read from budget files for quick access
        for bot in ["billy", "blood", "reaper"]:
            budget_file = Path(f"/root/{bot}_budget.json")
            if budget_file.exists():
                try:
                    with open(budget_file) as f:
                        data = json.load(f)
                        params[bot] = {
                            "current_budget": data.get("current_budget"),
                            "pnl_pct": data.get("pnl_pct"),
                            "daily_pnl_pct": data.get("daily_pnl_pct"),
                        }
                except:
                    pass

        # Add static params from memory
        params["billy"]["rsi_buy"] = 30
        params["billy"]["rsi_sell"] = 70
        params["billy"]["direction"] = "BIDIRECTIONAL"  # MANTIS changed this

        params["blood"] = params.get("blood", {})
        params["blood"]["z_threshold_long"] = 2.5
        params["blood"]["z_threshold_short"] = 4.0
        params["blood"]["direction"] = "BIDIRECTIONAL"

        params["reaper"] = params.get("reaper", {})
        params["reaper"]["leverage"] = 15
        params["reaper"]["stop_loss"] = 1.0
        params["reaper"]["take_profit"] = 10.0

        params["phantom"] = {
            "leverage": 10,
            "min_signals": 2,
            "stop_loss": 1.0,
            "take_profit": 15.0
        }

        return params

    def get_current_positions(self) -> str:
        """Get current open positions from Hyperliquid."""
        try:
            import ccxt
            hl = ccxt.hyperliquid({
                'walletAddress': os.getenv('HYPERLIQUID_WALLET_ADDRESS')
            })
            positions = hl.fetch_positions()

            active = []
            for p in positions:
                if p['contracts'] > 0:
                    active.append({
                        "symbol": p['symbol'].split('/')[0],
                        "side": p['side'],
                        "size": p['contracts'],
                        "entry": p['entryPrice'],
                        "pnl": p['unrealizedPnl'],
                        "roe": p['percentage']
                    })

            return json.dumps(active, indent=2)
        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return "[]"

    def get_market_conditions(self) -> str:
        """Get current market conditions."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Get recent alpha signals summary
        cursor.execute("""
            SELECT source, symbol, direction, AVG(strength) as avg_strength, COUNT(*) as count
            FROM alpha_signals
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY source, symbol, direction
        """)

        alpha = [dict(row) for row in cursor.fetchall()]

        # Get hive consensus
        hive_file = Path("/tmp/alpha_hive_signals.json")
        hive = {}
        if hive_file.exists():
            try:
                with open(hive_file) as f:
                    hive = json.load(f)
            except:
                pass

        conn.close()

        return json.dumps({
            "alpha_signals": alpha,
            "hive_consensus": hive,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, indent=2)

    def get_previous_decisions(self) -> str:
        """Get previous Optimus decisions."""
        if not DECISIONS_FILE.exists():
            return "No previous decisions."

        try:
            with open(DECISIONS_FILE) as f:
                decisions = json.load(f)
                # Return last 5 decisions
                recent = decisions.get("decisions", [])[-5:]
                return json.dumps(recent, indent=2)
        except:
            return "No previous decisions."

    def save_decision(self, decision: Dict[str, Any]) -> None:
        """Save decision to file and database."""
        # Load existing
        all_decisions = {"decisions": []}
        if DECISIONS_FILE.exists():
            try:
                with open(DECISIONS_FILE) as f:
                    all_decisions = json.load(f)
            except:
                pass

        # Add new
        all_decisions["decisions"].append({
            **decision,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Save
        with open(DECISIONS_FILE, 'w') as f:
            json.dump(all_decisions, f, indent=2)

        # Also save to brain.db
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            for d in decision.get("decision", {}).get("decisions", []):
                cursor.execute("""
                    INSERT INTO decisions (
                        decision_id, decision_type, target_bot, target_param,
                        old_value, new_value, confidence, applied, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"optimus_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "parameter_change",
                    d.get("bot", "unknown"),
                    d.get("parameter", "unknown"),
                    d.get("old_value", ""),
                    d.get("new_value", ""),
                    d.get("confidence", 0) / 100.0,
                    1 if d.get("action") == "APPLY" and not self.dry_run else 0,
                    datetime.now(timezone.utc).isoformat()
                ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save to brain.db: {e}")

    def apply_decision(self, decision: Dict[str, Any]) -> bool:
        """Apply an approved decision to bot config."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would apply: {decision}")
            return True

        bot = decision.get("bot", "").lower()
        param = decision.get("parameter", "")
        new_value = decision.get("new_value", "")

        if bot not in BOT_CONFIGS:
            logger.error(f"Unknown bot: {bot}")
            return False

        config_file = BOT_CONFIGS[bot]
        if not config_file.exists():
            logger.error(f"Config file not found: {config_file}")
            return False

        # TODO: Implement actual config file modification
        # For now, log the change
        logger.info(f"APPLYING: {bot}.{param} = {new_value}")

        # Send Slack notification
        self.send_slack_notification(
            f"🤖 *Optimus Decision Applied*\n"
            f"Bot: `{bot}`\n"
            f"Parameter: `{param}`\n"
            f"New Value: `{new_value}`\n"
            f"Confidence: {decision.get('confidence', 0)}%\n"
            f"Reason: {decision.get('reason', 'N/A')}"
        )

        return True

    def send_slack_notification(self, message: str) -> None:
        """Send notification to Slack."""
        if not SLACK_WEBHOOK:
            return

        try:
            import requests
            requests.post(
                SLACK_WEBHOOK,
                json={"text": message},
                timeout=10
            )
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")

    async def run_cycle(self) -> Dict[str, Any]:
        """Run one autonomous learning cycle."""
        logger.info("=" * 60)
        logger.info("OPTIMUS AUTONOMOUS BRAIN - Starting Cycle")
        logger.info("=" * 60)

        # Gather all data
        logger.info("Gathering data from brain.db...")
        trade_data = self.get_trade_data(hours=24)
        current_params = self.get_current_params()
        current_positions = self.get_current_positions()
        market_conditions = self.get_market_conditions()
        previous_decisions = self.get_previous_decisions()

        logger.info(f"Trade data: {len(json.loads(trade_data).get('real_trades', []))} trades")
        logger.info(f"Positions: {current_positions}")

        # Run the AI team
        logger.info("Running TradingTeam AI agents...")
        result = await self.team.run_autonomous_cycle(
            trade_data=trade_data,
            current_params=current_params,
            current_positions=current_positions,
            market_conditions=market_conditions,
            previous_decisions=previous_decisions
        )

        # Process decisions
        decisions = result.get("decision", {}).get("decisions", [])
        applied_count = 0

        for d in decisions:
            if d.get("action") == "APPLY":
                if self.decisions_today < self.max_decisions_per_day:
                    if self.apply_decision(d):
                        applied_count += 1
                        self.decisions_today += 1
                else:
                    logger.warning("Daily decision limit reached")

        # Save everything
        self.save_decision(result)

        logger.info("=" * 60)
        logger.info(f"Cycle complete. Applied {applied_count} decisions.")
        logger.info("=" * 60)

        return result


async def main():
    parser = argparse.ArgumentParser(description="Optimus Trading Brain")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without applying")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=3600, help="Daemon interval (seconds)")
    args = parser.parse_args()

    brain = TradingBrain(dry_run=args.dry_run)

    if args.daemon:
        logger.info(f"Starting daemon mode (interval: {args.interval}s)")
        while True:
            try:
                await brain.run_cycle()
            except Exception as e:
                logger.error(f"Cycle failed: {e}")

            await asyncio.sleep(args.interval)
    else:
        await brain.run_cycle()


if __name__ == "__main__":
    asyncio.run(main())
