from . import goto, click, fill, keystroke, sleep, view, chain, tabs

BASE_TOOLS = [
    (goto.tool, goto.handle),
    (click.tool, click.handle),
    (fill.tool, fill.handle),
    (keystroke.tool, keystroke.handle),
    (sleep.tool, sleep.handle),
    (view.tool, view.handle),
    (chain.tool, chain.handle),
    (tabs.tab_list_tool, tabs.handle_list),
    (tabs.tab_new_tool, tabs.handle_new),
    (tabs.tab_switch_tool, tabs.handle_switch),
    (tabs.tab_close_tool, tabs.handle_close),
]
