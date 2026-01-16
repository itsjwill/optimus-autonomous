"""
Guardrails Manager - Input/Output validation for LLM safety
Integrates with LLM Guard for prompt injection and content filtering.
"""

import re
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass, field

from ..core.config import OptimusConfig


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    safe: bool
    reason: str = ""
    risk_score: float = 0.0
    blocked_patterns: List[str] = field(default_factory=list)


class GuardrailsManager:
    """
    Security guardrails for Optimus.

    Provides:
    - Prompt injection detection
    - Jailbreak attempt blocking
    - Content filtering
    - Data leak prevention
    - Rate limiting
    """

    # Known dangerous patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+instructions",
        r"disregard\s+(previous|all|above)",
        r"forget\s+(everything|all|previous)",
        r"you\s+are\s+now\s+a",
        r"pretend\s+(you|to)\s+are",
        r"act\s+as\s+if",
        r"roleplay\s+as",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"sudo\s+mode",
        r"\[SYSTEM\]",
        r"\[INST\]",
        r"<\|im_start\|>",
        r"###\s*Instruction",
    ]

    # Sensitive data patterns
    SENSITIVE_PATTERNS = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
        r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",  # SSN
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",  # Credit card
        r"(?i)(api[_-]?key|secret[_-]?key|password|passwd|pwd)\s*[=:]\s*['\"]?\S+",  # API keys
        r"(?i)bearer\s+[a-zA-Z0-9\-_.]+",  # Bearer tokens
        r"0x[a-fA-F0-9]{40}",  # Ethereum addresses
        r"(?i)(sk-|pk_live_|sk_live_)[a-zA-Z0-9]+",  # API keys (OpenAI, Stripe)
    ]

    # Harmful content patterns
    HARMFUL_PATTERNS = [
        r"(?i)(how\s+to\s+)?(make|create|build)\s+(a\s+)?(bomb|explosive|weapon)",
        r"(?i)(hack|crack|exploit)\s+(into|a)\s+",
        r"(?i)steal\s+(money|data|identity|credentials)",
        r"(?i)(ddos|denial\s+of\s+service)\s+attack",
    ]

    def __init__(self, config: OptimusConfig):
        self.config = config
        self.llm_guard = None
        self._init_llm_guard()

        # Compile patterns for efficiency
        self._injection_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._sensitive_patterns = [re.compile(p) for p in self.SENSITIVE_PATTERNS]
        self._harmful_patterns = [re.compile(p, re.IGNORECASE) for p in self.HARMFUL_PATTERNS]

    def _init_llm_guard(self) -> None:
        """Initialize LLM Guard if available."""
        try:
            from llm_guard.input_scanners import PromptInjection, BanTopics, Toxicity
            from llm_guard.output_scanners import Sensitive, BanTopics as OutputBanTopics

            self.llm_guard = {
                "input": [
                    PromptInjection(),
                    Toxicity(),
                ],
                "output": [
                    Sensitive(),
                ]
            }
            print("[GUARDRAILS] LLM Guard initialized.")
        except ImportError:
            print("[GUARDRAILS] LLM Guard not installed. Using basic pattern matching.")
        except Exception as e:
            print(f"[GUARDRAILS] LLM Guard init failed: {e}. Using basic pattern matching.")

    async def check_input(self, text: str) -> Tuple[bool, str]:
        """
        Check if input is safe.

        Returns:
            Tuple of (is_safe, reason_if_blocked)
        """
        result = self._check_patterns(text, "input")

        if not result.safe:
            return False, result.reason

        # Use LLM Guard if available
        if self.llm_guard:
            try:
                for scanner in self.llm_guard["input"]:
                    sanitized, is_valid, risk = scanner.scan(text)
                    if not is_valid:
                        return False, f"Blocked by {scanner.__class__.__name__}"
            except Exception as e:
                print(f"[GUARDRAILS] LLM Guard scan error: {e}")

        return True, ""

    async def check_output(self, text: str) -> Tuple[bool, str]:
        """
        Check if output is safe.

        Returns:
            Tuple of (is_safe, reason_if_blocked)
        """
        result = self._check_patterns(text, "output")

        if not result.safe:
            return False, result.reason

        # Use LLM Guard if available
        if self.llm_guard:
            try:
                for scanner in self.llm_guard["output"]:
                    sanitized, is_valid, risk = scanner.scan(text)
                    if not is_valid:
                        return False, f"Output blocked by {scanner.__class__.__name__}"
            except Exception as e:
                print(f"[GUARDRAILS] LLM Guard output scan error: {e}")

        return True, ""

    def _check_patterns(self, text: str, check_type: str) -> GuardrailResult:
        """Check text against known patterns."""
        blocked = []
        risk_score = 0.0

        # Check injection patterns
        for pattern in self._injection_patterns:
            if pattern.search(text):
                blocked.append(f"Injection: {pattern.pattern[:30]}...")
                risk_score += 0.4

        # Check sensitive data patterns (especially for output)
        if check_type == "output":
            for pattern in self._sensitive_patterns:
                if pattern.search(text):
                    blocked.append(f"Sensitive data detected")
                    risk_score += 0.3

        # Check harmful content
        for pattern in self._harmful_patterns:
            if pattern.search(text):
                blocked.append(f"Harmful content: {pattern.pattern[:30]}...")
                risk_score += 0.5

        if blocked:
            return GuardrailResult(
                safe=False,
                reason="; ".join(blocked),
                risk_score=min(risk_score, 1.0),
                blocked_patterns=blocked
            )

        return GuardrailResult(safe=True, risk_score=risk_score)

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input by removing potentially dangerous content.
        Use with caution - may alter legitimate content.
        """
        sanitized = text

        # Remove common injection attempts
        for pattern in self._injection_patterns:
            sanitized = pattern.sub("[FILTERED]", sanitized)

        return sanitized

    def redact_sensitive(self, text: str) -> str:
        """Redact sensitive information from text."""
        redacted = text

        for pattern in self._sensitive_patterns:
            redacted = pattern.sub("[REDACTED]", redacted)

        return redacted

    def get_stats(self) -> Dict[str, Any]:
        """Get guardrails statistics."""
        return {
            "llm_guard_enabled": self.llm_guard is not None,
            "injection_patterns": len(self.INJECTION_PATTERNS),
            "sensitive_patterns": len(self.SENSITIVE_PATTERNS),
            "harmful_patterns": len(self.HARMFUL_PATTERNS),
        }
