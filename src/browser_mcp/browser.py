from invisible_playwright.async_api import InvisiblePlaywright
from playwright.async_api import BrowserContext


class BrowserManager:
    _instance = None
    _browser = None
    _contexts: dict[str, BrowserContext] = {}
    _args = None

    @classmethod
    def init(cls, args):
        cls._args = args

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            if cls._args is None:
                raise RuntimeError("BrowserManager not initialized. Call init(args) first.")
            cls._instance = cls()
            await cls._instance._start()
        return cls._instance

    async def _start(self):
        self._browser = await InvisiblePlaywright().start()

    async def get_context(self, session_id: str) -> BrowserContext:
        if session_id not in self._contexts:
            ctx = await self._browser.new_context(
                viewport={"width": self._args.viewport_width, "height": self._args.viewport_height},
            )
            self._contexts[session_id] = ctx
        return self._contexts[session_id]

    async def close_context(self, session_id: str):
        ctx = self._contexts.pop(session_id, None)
        if ctx:
            await ctx.close()

    async def shutdown(self):
        for ctx in self._contexts.values():
            await ctx.close()
        self._contexts.clear()
        if self._browser:
            await self._browser.close()
