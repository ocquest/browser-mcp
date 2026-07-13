import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="browser-mcp server")
    parser.add_argument("--port", type=int, default=None, help="MCP server port (SSE). Default: stdio transport")
    parser.add_argument("--profile", type=str, default=None, help="path to Chromium profile")
    parser.add_argument("--viewport-width", type=int, default=1280, help="viewport width")
    parser.add_argument("--viewport-height", type=int, default=720, help="viewport height")
    parser.add_argument("--2captcha-api-key", type=str, default=None, dest="captcha_api_key", help="2captcha API key")
    return parser.parse_args(argv)
