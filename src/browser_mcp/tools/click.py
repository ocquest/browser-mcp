from mcp.types import Tool, TextContent
from ..diff import compute_diff


tool = Tool(
    name="click",
    description="Click on an element using real mouse movement",
    inputSchema={
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector of the element to click",
            }
        },
        "required": ["selector"],
    },
)


async def handle(ctx, selector: str):
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
    after = await page.content()
    diff = compute_diff(before, after)
    return [TextContent(type="text", text=f"Clicked {selector}\n\nDiff:\n{diff}" if diff else f"Clicked {selector}")]
