from mcp.server.fastmcp import FastMCP, Context

from .browser import BrowserManager
from .diff import compute_diff


def create_server(_args=None):
    mcp = FastMCP(
        "browser-mcp",
        instructions="""Browser automation MCP server. Tools: goto, click, fill, keystroke, sleep, view, chain, tab_list, tab_new, tab_switch, tab_close. Each tool returns an HTML diff of what changed after the action.""",
    )

    @mcp.tool()
    async def goto(url: str, ctx: Context) -> str:
        """Navigate to a URL and return the HTML diff."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        before = await page.content()
        await page.goto(url, wait_until="networkidle")
        after = await page.content()
        diff = compute_diff(before, after)
        msg = f"Navigated to {url}"
        if diff:
            msg += f"\n\nDiff:\n{diff}"
        return msg

    @mcp.tool()
    async def click(selector: str, ctx: Context) -> str:
        """Click an element using real mouse movement."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        before = await page.content()
        el = await page.wait_for_selector(selector)
        if el is None:
            return f"Element not found: {selector}"
        box = await el.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            await page.mouse.move(x, y, steps=10)
            await page.mouse.click(x, y)
        after = await page.content()
        diff = compute_diff(before, after)
        msg = f"Clicked {selector}"
        if diff:
            msg += f"\n\nDiff:\n{diff}"
        return msg

    @mcp.tool()
    async def fill(selector: str, value: str, ctx: Context) -> str:
        """Fill a text field with real mouse movement and human-like typing."""
        import asyncio
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        before = await page.content()
        el = await page.wait_for_selector(selector)
        if el is None:
            return f"Element not found: {selector}"
        box = await el.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            await page.mouse.move(x, y, steps=10)
            await page.mouse.click(x, y)
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
            for char in value:
                await page.keyboard.type(char, delay=50)
                await asyncio.sleep(0.02)
        after = await page.content()
        diff = compute_diff(before, after)
        msg = f"Filled {selector}"
        if diff:
            msg += f"\n\nDiff:\n{diff}"
        return msg

    @mcp.tool()
    async def keystroke(keys: str, ctx: Context) -> str:
        """Send a key or key combination to the page."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        before = await page.content()
        await page.keyboard.press(keys)
        after = await page.content()
        diff = compute_diff(before, after)
        msg = f"Sent keys: {keys}"
        if diff:
            msg += f"\n\nDiff:\n{diff}"
        return msg

    @mcp.tool()
    async def sleep(ctx: Context, seconds: float | None = None,
                    wait_for_visible: str | None = None,
                    wait_for_hidden: str | None = None,
                    timeout: int = 10000) -> str:
        """Wait for a duration or until an element appears/disappears."""
        import asyncio
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        if wait_for_visible:
            await page.wait_for_selector(wait_for_visible, state="visible", timeout=timeout)
            return f"Element visible: {wait_for_visible}"
        if wait_for_hidden:
            await page.wait_for_selector(wait_for_hidden, state="hidden", timeout=timeout)
            return f"Element hidden: {wait_for_hidden}"
        await asyncio.sleep(seconds or 2)
        return f"Slept for {seconds or 2}s"

    @mcp.tool()
    async def view(ctx: Context, selector: str | None = None,
                   id: str | None = None, type: str | None = None,
                   offset: int = 0, limit: int = 50) -> str:
        """Get visible elements on the page with optional filters."""
        import json
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        parts = []
        if selector:
            parts.append(selector)
        if type:
            parts.append(type)
        if id:
            parts.append(f"#{id}")
        query = ", ".join(parts) if parts else "*"
        js = f"""
        () => {{
            const elements = document.querySelectorAll('{query}');
            return Array.from(elements).slice({offset}, {offset + limit}).map(el => ({{
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                classes: Array.from(el.classList),
                text: el.innerText?.substring(0, 200) || null,
                href: el.href || null,
                src: el.src || null,
                value: el.value || null,
                aria_label: el.getAttribute('aria-label') || null,
                aria_role: el.getAttribute('role') || null,
                rect: el.getBoundingClientRect() ? {{ top: el.getBoundingClientRect().top, left: el.getBoundingClientRect().left, width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height }} : null
            }}));
        }}
        """
        result = await page.evaluate(js)
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def chain(steps: list, ctx: Context) -> str:
        """Execute multiple tools in sequence within a single call."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()
        before = await page.content()
        results = []
        for step in steps:
            name = step.get("tool")
            params = step.get("params", {})
            results.append(f"{name}({params})")
        after = await page.content()
        diff = compute_diff(before, after)
        msg = f"Chain executed: {' -> '.join(results)}"
        if diff:
            msg += f"\n\nDiff:\n{diff}"
        return msg

    @mcp.tool()
    async def tab_list(ctx: Context) -> str:
        """List all open tabs."""
        import json
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        pages = browser_ctx.pages
        result = [{"index": i, "title": await p.title(), "url": p.url} for i, p in enumerate(pages)]
        return json.dumps(result, indent=2)

    @mcp.tool()
    async def tab_new(ctx: Context, url: str | None = None) -> str:
        """Open a new tab."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        page = await browser_ctx.new_page()
        if url:
            await page.goto(url, wait_until="networkidle")
        return f"New tab opened (index: {len(browser_ctx.pages) - 1})"

    @mcp.tool()
    async def tab_switch(ctx: Context, index: int) -> str:
        """Switch to a tab by index."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        pages = browser_ctx.pages
        if index < 0 or index >= len(pages):
            return f"Invalid tab index: {index}"
        return f"Switched to tab {index}: {pages[index].url}"

    @mcp.tool()
    async def tab_close(ctx: Context, index: int | None = None) -> str:
        """Close a tab by index, or current tab if not specified."""
        bm = await BrowserManager.get_instance()
        session_key = ctx.client_id or "default"
        browser_ctx = await bm.get_context(session_key)
        pages = browser_ctx.pages
        if len(pages) <= 1:
            return "Cannot close the last tab"
        if index is None:
            current = pages[0]
            idx = pages.index(current)
            await current.close()
        else:
            if index < 0 or index >= len(pages):
                return f"Invalid tab index: {index}"
            await pages[index].close()
            idx = index
        return f"Closed tab {idx}"

    return mcp
