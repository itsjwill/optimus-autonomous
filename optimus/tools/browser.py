"""
Browser Tool - Web automation for agents
Integrates with Playwright for headless browser control.
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .registry import Tool, ToolResult, ToolCategory


@dataclass
class BrowserSession:
    """A browser session."""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    pages: int = 0
    current_url: Optional[str] = None


class BrowserTool:
    """
    Browser automation tool for agents.

    Provides:
    - Headless browser control via Playwright
    - Page navigation and interaction
    - Screenshot capture
    - Content extraction
    - Form filling and submission

    Falls back to httpx for simple requests if Playwright unavailable.
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.sessions: Dict[str, BrowserSession] = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the browser."""
        if self._initialized:
            return True

        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self.page = await self.context.new_page()
            self._initialized = True
            print("[BROWSER] Playwright initialized")
            return True
        except ImportError:
            print("[BROWSER] Playwright not installed. Using httpx fallback.")
            return False
        except Exception as e:
            print(f"[BROWSER] Initialization failed: {e}")
            return False

    async def close(self) -> None:
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._initialized = False
        print("[BROWSER] Closed")

    async def navigate(self, url: str, wait_until: str = "load") -> ToolResult:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete (load, domcontentloaded, networkidle)

        Returns:
            ToolResult with page title
        """
        start_time = datetime.now()

        if not self._initialized:
            await self.initialize()

        if self.page:
            try:
                response = await self.page.goto(url, wait_until=wait_until)
                title = await self.page.title()
                duration = (datetime.now() - start_time).total_seconds() * 1000

                return ToolResult(
                    success=True,
                    output={
                        "url": url,
                        "title": title,
                        "status": response.status if response else None
                    },
                    duration_ms=duration
                )
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                return ToolResult(
                    success=False,
                    output=None,
                    error=str(e),
                    duration_ms=duration
                )
        else:
            # Fallback to httpx
            return await self._httpx_get(url)

    async def get_content(self, selector: Optional[str] = None) -> ToolResult:
        """
        Get page content or element content.

        Args:
            selector: Optional CSS selector to get specific element

        Returns:
            ToolResult with content
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            if selector:
                element = await self.page.query_selector(selector)
                if element:
                    content = await element.inner_text()
                else:
                    content = None
            else:
                content = await self.page.content()

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=content,
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def get_text(self) -> ToolResult:
        """Get all visible text from the page."""
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            # Get text content, stripping scripts and styles
            text = await self.page.evaluate("""
                () => {
                    const clone = document.body.cloneNode(true);
                    const scripts = clone.querySelectorAll('script, style, noscript');
                    scripts.forEach(el => el.remove());
                    return clone.innerText;
                }
            """)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=text,
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def click(self, selector: str) -> ToolResult:
        """
        Click an element.

        Args:
            selector: CSS selector for the element to click

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            await self.page.click(selector)
            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Clicked: {selector}",
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def fill(self, selector: str, value: str) -> ToolResult:
        """
        Fill a form field.

        Args:
            selector: CSS selector for the input element
            value: Value to fill

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            await self.page.fill(selector, value)
            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Filled {selector} with value",
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> ToolResult:
        """
        Take a screenshot.

        Args:
            path: Path to save screenshot (returns base64 if not provided)
            full_page: Whether to capture the full scrollable page

        Returns:
            ToolResult with screenshot path or base64 data
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            if path:
                await self.page.screenshot(path=path, full_page=full_page)
                output = path
            else:
                import base64
                screenshot_bytes = await self.page.screenshot(full_page=full_page)
                output = base64.b64encode(screenshot_bytes).decode()

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=output,
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def evaluate(self, script: str) -> ToolResult:
        """
        Execute JavaScript on the page.

        Args:
            script: JavaScript code to execute

        Returns:
            ToolResult with the script result
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            result = await self.page.evaluate(script)
            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=result,
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> ToolResult:
        """
        Wait for an element to appear.

        Args:
            selector: CSS selector to wait for
            timeout: Maximum wait time in milliseconds

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Element found: {selector}",
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def get_links(self) -> ToolResult:
        """Get all links from the current page."""
        start_time = datetime.now()

        if not self._initialized or not self.page:
            return ToolResult(
                success=False,
                output=None,
                error="Browser not initialized"
            )

        try:
            links = await self.page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                        href: a.href,
                        text: a.innerText.trim().substring(0, 100)
                    })).filter(l => l.href.startsWith('http'));
                }
            """)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=links,
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def _httpx_get(self, url: str) -> ToolResult:
        """Fallback HTTP GET using httpx."""
        start_time = datetime.now()

        try:
            import httpx

            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=30.0)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                return ToolResult(
                    success=True,
                    output={
                        "url": str(response.url),
                        "status": response.status_code,
                        "content": response.text[:10000]  # Limit content size
                    },
                    duration_ms=duration
                )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    def get_tools(self) -> List[Tool]:
        """Get browser tools for registration."""
        return [
            Tool(
                name="browser_navigate",
                description="Navigate to a URL in the browser",
                func=self.navigate,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to navigate to", "required": True},
                    "wait_until": {"type": "string", "description": "Wait condition: load, domcontentloaded, networkidle"}
                }
            ),
            Tool(
                name="browser_get_content",
                description="Get page content or specific element content",
                func=self.get_content,
                category=ToolCategory.WEB,
                parameters={
                    "selector": {"type": "string", "description": "Optional CSS selector"}
                }
            ),
            Tool(
                name="browser_get_text",
                description="Get all visible text from the current page",
                func=self.get_text,
                category=ToolCategory.WEB,
                parameters={}
            ),
            Tool(
                name="browser_click",
                description="Click an element on the page",
                func=self.click,
                category=ToolCategory.WEB,
                parameters={
                    "selector": {"type": "string", "description": "CSS selector for element to click", "required": True}
                }
            ),
            Tool(
                name="browser_fill",
                description="Fill a form field with a value",
                func=self.fill,
                category=ToolCategory.WEB,
                parameters={
                    "selector": {"type": "string", "description": "CSS selector for input element", "required": True},
                    "value": {"type": "string", "description": "Value to fill", "required": True}
                }
            ),
            Tool(
                name="browser_screenshot",
                description="Take a screenshot of the current page",
                func=self.screenshot,
                category=ToolCategory.WEB,
                parameters={
                    "path": {"type": "string", "description": "Path to save screenshot"},
                    "full_page": {"type": "boolean", "description": "Capture full scrollable page"}
                }
            ),
            Tool(
                name="browser_get_links",
                description="Get all links from the current page",
                func=self.get_links,
                category=ToolCategory.WEB,
                parameters={}
            ),
        ]
