from mcp.types import Tool, TextContent
import json


tool = Tool(
    name="view",
    description="Get visible elements on the page with optional filters",
    inputSchema={
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector filter"},
            "id": {"type": "string", "description": "Element ID filter"},
            "type": {"type": "string", "description": "Element type filter (button, input, a, img, etc.)"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
            "limit": {"type": "integer", "description": "Max elements to return (default 50)"},
        },
    },
)


async def handle(ctx, selector: str | None = None, id: str | None = None,
                 type: str | None = None, offset: int = 0, limit: int = 50):
    page = await ctx.get_page()
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
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
