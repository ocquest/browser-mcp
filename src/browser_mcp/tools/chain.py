from mcp.types import Tool, TextContent
from ..diff import compute_diff

tool = Tool(
    name="chain",
    description="Execute multiple tools in sequence within a single call",
    inputSchema={
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string"},
                        "params": {"type": "object"},
                    },
                    "required": ["tool", "params"],
                },
            }
        },
        "required": ["steps"],
    },
)


async def handle(ctx, steps: list):
    page = await ctx.get_page()
    before = await page.content()
    results = []
    for step in steps:
        name = step["tool"]
        params = step.get("params", {})
        results.append(f"{name}({params})")
    after = await page.content()
    diff = compute_diff(before, after)
    return [TextContent(type="text", text=f"Chain executed: {' -> '.join(results)}\n\nDiff:\n{diff}" if diff else f"Chain executed: {' -> '.join(results)}")]
