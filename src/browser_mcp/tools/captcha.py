"""
Optional captcha tool. Only available if 2captcha-api-key is provided.
"""
from mcp.types import Tool, TextContent

captcha_solve_tool = Tool(
    name="captcha_solve",
    description="Solve a captcha using the 2Captcha service",
    inputSchema={
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["normal", "text", "recaptcha_v2", "recaptcha_v3", "funcaptcha",
                         "geetest", "keycaptcha", "capy", "grid", "canvas", "click", "rotate"],
                "description": "Type of captcha",
            },
            "sitekey": {"type": "string", "description": "Site key for reCAPTCHA/FunCaptcha"},
            "url": {"type": "string", "description": "Page URL where captcha appears"},
            "image": {"type": "string", "description": "Captcha image in base64"},
            "text": {"type": "string", "description": "Text captcha question"},
            "challenge": {"type": "string", "description": "GeeTest challenge"},
            "gt": {"type": "string", "description": "GeeTest gt"},
            "version": {"type": "string", "enum": ["v2", "v3"], "description": "reCAPTCHA version"},
            "action": {"type": "string", "description": "reCAPTCHA v3 action"},
            "min_score": {"type": "number", "description": "reCAPTCHA v3 min score"},
        },
        "required": ["type"],
    },
)

captcha_report_tool = Tool(
    name="captcha_report",
    description="Report captcha result as good or bad",
    inputSchema={
        "type": "object",
        "properties": {
            "captcha_id": {"type": "string", "description": "Captcha ID from captcha_solve"},
            "correct": {"type": "boolean", "description": "True if solved correctly, False otherwise"},
        },
        "required": ["captcha_id", "correct"],
    },
)

_solver = None


def init_solver(api_key: str):
    from twocaptcha import TwoCaptcha
    global _solver
    _solver = TwoCaptcha(api_key)


async def handle_solve(type: str, **kwargs):
    if _solver is None:
        return [TextContent(type="text", text="2Captcha not configured. Provide --2captcha-api-key")]
    try:
        method = getattr(_solver, type)
        result = method(**kwargs)
        return [TextContent(type="text",
                           text=f"Captcha solved\nResult: {result.get('code', result)}\nCaptcha ID: {result.get('captchaId', 'N/A')}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Captcha error: {e}")]


async def handle_report(captcha_id: str, correct: bool):
    if _solver is None:
        return [TextContent(type="text", text="2Captcha not configured")]
    try:
        _solver.report(captcha_id, correct)
        return [TextContent(type="text", text=f"Reported captcha {captcha_id} as {'good' if correct else 'bad'}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Report error: {e}")]
