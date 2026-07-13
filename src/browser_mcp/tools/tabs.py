from mcp.types import Tool, TextContent
import json


tab_list_tool = Tool(
    name="tab_list",
    description="List all open tabs",
    inputSchema={"type": "object", "properties": {}},
)

tab_new_tool = Tool(
    name="tab_new",
    description="Open a new tab",
    inputSchema={
        "type": "object",
        "properties": {"url": {"type": "string", "description": "Optional URL to open in the new tab"}},
    },
)

tab_switch_tool = Tool(
    name="tab_switch",
    description="Switch to a tab by index",
    inputSchema={
        "type": "object",
        "properties": {"index": {"type": "integer", "description": "Tab index to switch to"}},
        "required": ["index"],
    },
)

tab_close_tool = Tool(
    name="tab_close",
    description="Close a tab by index, or current tab if not specified",
    inputSchema={
        "type": "object",
        "properties": {"index": {"type": "integer", "description": "Tab index to close"}},
    },
)

tools = [tab_list_tool, tab_new_tool, tab_switch_tool, tab_close_tool]


async def handle_list(ctx):
    pages = ctx.context.pages
    result = [{"index": i, "title": await p.title(), "url": p.url} for i, p in enumerate(pages)]
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_new(ctx, url: str | None = None):
    page = await ctx.context.new_page()
    if url:
        await page.goto(url, wait_until="networkidle")
    ctx._current_page = page
    return [TextContent(type="text", text=f"New tab opened (index: {len(ctx.context.pages) - 1})")]


async def handle_switch(ctx, index: int):
    pages = ctx.context.pages
    if index < 0 or index >= len(pages):
        return [TextContent(type="text", text=f"Invalid tab index: {index}")]
    ctx._current_page = pages[index]
    return [TextContent(type="text", text=f"Switched to tab {index}: {pages[index].url}")]


async def handle_close(ctx, index: int | None = None):
    pages = ctx.context.pages
    if len(pages) <= 1:
        return [TextContent(type="text", text="Cannot close the last tab")]
    if index is None:
        current = ctx._current_page
        idx = pages.index(current)
        await current.close()
    else:
        if index < 0 or index >= len(pages):
            return [TextContent(type="text", text=f"Invalid tab index: {index}")]
        await pages[index].close()
        idx = index
    remaining = ctx.context.pages
    if remaining:
        ctx._current_page = remaining[0]
    return [TextContent(type="text", text=f"Closed tab {idx}")]
