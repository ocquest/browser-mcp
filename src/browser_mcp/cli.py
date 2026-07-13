import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="browser-mcp server")
    parser.add_argument("--port", type=int, default=None, help="MCP server port (SSE). Default: stdio transport")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (default: visible)")
    parser.add_argument("--profile", type=str, default=None, help="path to Chromium profile")
    parser.add_argument("--viewport-width", type=int, default=1280, help="viewport width")
    parser.add_argument("--viewport-height", type=int, default=720, help="viewport height")
    parser.add_argument("--2captcha-api-key", type=str, default=None, dest="captcha_api_key", help="2captcha API key")
    parser.add_argument("--orbit-sk", type=str, default=None, help="OrbitLLM secret key (enables screenshot AI analysis)")
    parser.add_argument("--orbit-url", type=str, default="http://51.91.78.242:15000", help="OrbitLLM base URL")
    return parser.parse_args(argv)
