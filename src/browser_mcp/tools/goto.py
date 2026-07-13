from mcp.types import Tool, TextContent
from ..diff import compute_diff


tool = Tool(
    name="goto",
    description="Navigate to a URL",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL to navigate to"}
        },
        "required": ["url"],
    },
)


async def handle(ctx, url: str):
    page = await ctx.get_page()
    before = await page.content()
    await page.goto(url, wait_until="networkidle")
    after = await page.content()
    diff = compute_diff(before, after)
    return [TextContent(type="text", text=f"Navigated to {url}\n\nDiff:\n{diff}" if diff else f"Navigated to {url}")]
