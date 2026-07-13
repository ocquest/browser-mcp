from mcp.types import Tool, TextContent
from ..diff import compute_diff


tool = Tool(
    name="keystroke",
    description="Send a key or key combination to the page",
    inputSchema={
        "type": "object",
        "properties": {
            "keys": {"type": "string", "description": "Key(s) to press (e.g. Enter, Tab, Control+A)"}
        },
        "required": ["keys"],
    },
)


async def handle(ctx, keys: str):
    page = await ctx.get_page()
    before = await page.content()
    await page.keyboard.press(keys)
    after = await page.content()
    diff = compute_diff(before, after)
    return [TextContent(type="text", text=f"Sent keys: {keys}\n\nDiff:\n{diff}" if diff else f"Sent keys: {keys}")]
