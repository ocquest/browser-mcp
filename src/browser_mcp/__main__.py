import sys
import asyncio
from .cli import parse_args
from .server import create_server


def main():
    args = parse_args()
    server = create_server(args)
    if args.port:
        from mcp.server import sse_server
        server.run(sse_server("localhost", args.port))
    else:
        from mcp.server import stdio_server
        server.run(stdio_server())


if __name__ == "__main__":
    main()
