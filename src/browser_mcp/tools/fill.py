import asyncio
from mcp.types import Tool, TextContent
from ..diff import compute_diff


tool = Tool(
    name="fill",
    description="Fill a text field with real mouse movement and human-like typing",
    inputSchema={
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector of the input field"},
            "value": {"type": "string", "description": "Text to type into the field"},
        },
        "required": ["selector", "value"],
    },
)


async def handle(ctx, selector: str, value: str):
    page = await ctx.get_page()
    before = await page.content()
    el = await page.wait_for_selector(selector)
    if el is None:
        return [TextContent(type="text", text=f"Element not found: {selector}")]
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
    return [TextContent(type="text", text=f"Filled {selector}\n\nDiff:\n{diff}" if diff else f"Filled {selector}")]
