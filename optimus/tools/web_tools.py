"""
Web Tools - HTTP and web scraping tools for agents
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from .registry import Tool, ToolResult, ToolCategory


class WebTools:
    """
    Web tools for agents.

    Provides:
    - HTTP requests (GET, POST, PUT, DELETE)
    - JSON API interactions
    - Web scraping
    - Content extraction
    """

    def __init__(self, default_timeout: float = 30.0, max_response_size: int = 5 * 1024 * 1024):
        """
        Initialize web tools.

        Args:
            default_timeout: Default request timeout in seconds
            max_response_size: Maximum response size in bytes (default 5MB)
        """
        self.default_timeout = default_timeout
        self.max_response_size = max_response_size
        self._session = None

    async def _get_client(self):
        """Get or create httpx client."""
        try:
            import httpx
            return httpx.AsyncClient(
                timeout=self.default_timeout,
                follow_redirects=True,
                headers={"User-Agent": "Optimus-Autonomous/0.1.0"}
            )
        except ImportError:
            raise ImportError("httpx is required for web tools. Install with: pip install httpx")

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None) -> ToolResult:
        """
        Make an HTTP GET request.

        Args:
            url: URL to request
            headers: Optional headers
            params: Optional query parameters

        Returns:
            ToolResult with response
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.get(url, headers=headers, params=params)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                # Try to parse as JSON
                try:
                    content = response.json()
                except:
                    content = response.text[:self.max_response_size]

                return ToolResult(
                    success=response.is_success,
                    output={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content": content,
                        "url": str(response.url)
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

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> ToolResult:
        """
        Make an HTTP POST request.

        Args:
            url: URL to request
            data: Form data to send
            json_data: JSON data to send
            headers: Optional headers

        Returns:
            ToolResult with response
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.post(url, data=data, json=json_data, headers=headers)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                try:
                    content = response.json()
                except:
                    content = response.text[:self.max_response_size]

                return ToolResult(
                    success=response.is_success,
                    output={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content": content,
                        "url": str(response.url)
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

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> ToolResult:
        """
        Make an HTTP PUT request.

        Args:
            url: URL to request
            data: Form data to send
            json_data: JSON data to send
            headers: Optional headers

        Returns:
            ToolResult with response
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.put(url, data=data, json=json_data, headers=headers)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                try:
                    content = response.json()
                except:
                    content = response.text[:self.max_response_size]

                return ToolResult(
                    success=response.is_success,
                    output={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content": content
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

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> ToolResult:
        """
        Make an HTTP DELETE request.

        Args:
            url: URL to request
            headers: Optional headers

        Returns:
            ToolResult with response
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.delete(url, headers=headers)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                try:
                    content = response.json()
                except:
                    content = response.text[:self.max_response_size]

                return ToolResult(
                    success=response.is_success,
                    output={
                        "status_code": response.status_code,
                        "content": content
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

    async def fetch_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> ToolResult:
        """
        Fetch JSON from a URL.

        Args:
            url: URL to fetch
            headers: Optional headers

        Returns:
            ToolResult with JSON data
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.get(url, headers=headers)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if not response.is_success:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"HTTP {response.status_code}",
                        duration_ms=duration
                    )

                data = response.json()

                return ToolResult(
                    success=True,
                    output=data,
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

    async def scrape_text(self, url: str) -> ToolResult:
        """
        Scrape text content from a webpage.

        Args:
            url: URL to scrape

        Returns:
            ToolResult with extracted text
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.get(url)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if not response.is_success:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"HTTP {response.status_code}",
                        duration_ms=duration
                    )

                html = response.text

                # Try BeautifulSoup if available
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')

                    # Remove scripts and styles
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    text = soup.get_text(separator='\n', strip=True)
                except ImportError:
                    # Fallback: basic regex extraction
                    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()

                return ToolResult(
                    success=True,
                    output=text[:50000],  # Limit text length
                    duration_ms=duration,
                    metadata={"url": str(response.url)}
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def extract_links(self, url: str) -> ToolResult:
        """
        Extract all links from a webpage.

        Args:
            url: URL to extract links from

        Returns:
            ToolResult with list of links
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.get(url)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if not response.is_success:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"HTTP {response.status_code}",
                        duration_ms=duration
                    )

                html = response.text
                base_url = str(response.url)

                # Try BeautifulSoup
                try:
                    from bs4 import BeautifulSoup
                    from urllib.parse import urljoin

                    soup = BeautifulSoup(html, 'html.parser')
                    links = []

                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        full_url = urljoin(base_url, href)
                        text = a.get_text(strip=True)[:100]
                        links.append({"url": full_url, "text": text})

                except ImportError:
                    # Fallback: regex extraction
                    pattern = r'href=["\']([^"\']+)["\']'
                    matches = re.findall(pattern, html)
                    links = [{"url": m, "text": ""} for m in matches if m.startswith('http')]

                return ToolResult(
                    success=True,
                    output=links[:500],  # Limit number of links
                    duration_ms=duration,
                    metadata={"count": len(links)}
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def download_file(self, url: str, save_path: str) -> ToolResult:
        """
        Download a file from a URL.

        Args:
            url: URL to download
            save_path: Path to save the file

        Returns:
            ToolResult with download info
        """
        start_time = datetime.now()

        try:
            async with await self._get_client() as client:
                response = await client.get(url)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if not response.is_success:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"HTTP {response.status_code}",
                        duration_ms=duration
                    )

                content = response.content
                if len(content) > self.max_response_size:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"File too large: {len(content)} bytes",
                        duration_ms=duration
                    )

                from pathlib import Path
                path = Path(save_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)

                return ToolResult(
                    success=True,
                    output={
                        "path": str(path),
                        "size": len(content),
                        "content_type": response.headers.get("content-type")
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
        """Get web tools for registration."""
        return [
            Tool(
                name="web_get",
                description="Make an HTTP GET request",
                func=self.get,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to request", "required": True},
                    "headers": {"type": "object", "description": "Optional headers"},
                    "params": {"type": "object", "description": "Optional query parameters"}
                }
            ),
            Tool(
                name="web_post",
                description="Make an HTTP POST request",
                func=self.post,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to request", "required": True},
                    "data": {"type": "object", "description": "Form data to send"},
                    "json_data": {"type": "object", "description": "JSON data to send"},
                    "headers": {"type": "object", "description": "Optional headers"}
                }
            ),
            Tool(
                name="web_put",
                description="Make an HTTP PUT request",
                func=self.put,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to request", "required": True},
                    "data": {"type": "object", "description": "Form data to send"},
                    "json_data": {"type": "object", "description": "JSON data to send"},
                    "headers": {"type": "object", "description": "Optional headers"}
                }
            ),
            Tool(
                name="web_delete",
                description="Make an HTTP DELETE request",
                func=self.delete,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to request", "required": True},
                    "headers": {"type": "object", "description": "Optional headers"}
                }
            ),
            Tool(
                name="web_fetch_json",
                description="Fetch JSON data from a URL",
                func=self.fetch_json,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to fetch", "required": True},
                    "headers": {"type": "object", "description": "Optional headers"}
                }
            ),
            Tool(
                name="web_scrape_text",
                description="Scrape text content from a webpage",
                func=self.scrape_text,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to scrape", "required": True}
                }
            ),
            Tool(
                name="web_extract_links",
                description="Extract all links from a webpage",
                func=self.extract_links,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to extract links from", "required": True}
                }
            ),
            Tool(
                name="web_download",
                description="Download a file from a URL",
                func=self.download_file,
                category=ToolCategory.WEB,
                parameters={
                    "url": {"type": "string", "description": "URL to download", "required": True},
                    "save_path": {"type": "string", "description": "Path to save the file", "required": True}
                }
            ),
        ]
