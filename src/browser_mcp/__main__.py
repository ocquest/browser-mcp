import sys
import asyncio
from .cli import parse_args
from .server import create_server
from .browser import BrowserManager


def main():
    args = parse_args()
    server = create_server(args)

    # Initialize the browser manager with args
    # It will be lazily started on first tool call
    BrowserManager.init(args)

    server.run(transport="stdio")


if __name__ == "__main__":
    main()
