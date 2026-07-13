import asyncio
from mcp.types import Tool, TextContent


tool = Tool(
    name="sleep",
    description="Wait for a duration or until an element appears/disappears",
    inputSchema={
        "type": "object",
        "properties": {
            "seconds": {"type": "number", "description": "Seconds to wait"},
            "wait_for_visible": {"type": "string", "description": "CSS selector to wait for visibility"},
            "wait_for_hidden": {"type": "string", "description": "CSS selector to wait for hidden"},
            "timeout": {"type": "number", "description": "Maximum timeout in ms (default 10000)"},
        },
    },
)


async def handle(ctx, seconds: float | None = None, wait_for_visible: str | None = None,
                 wait_for_hidden: str | None = None, timeout: int = 10000):
    page = await ctx.get_page()
    if wait_for_visible:
        await page.wait_for_selector(wait_for_visible, state="visible", timeout=timeout)
        return [TextContent(type="text", text=f"Element visible: {wait_for_visible}")]
    if wait_for_hidden:
        await page.wait_for_selector(wait_for_hidden, state="hidden", timeout=timeout)
        return [TextContent(type="text", text=f"Element hidden: {wait_for_hidden}")]
    await asyncio.sleep(seconds or 2)
    return [TextContent(type="text", text=f"Slept for {seconds or 2}s")]
