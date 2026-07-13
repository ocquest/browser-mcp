CURSOR_JS = """
() => {
    if (window._browserCursor) return;
    const cursor = document.createElement('div');
    cursor.id = '__browser_cursor';
    cursor.style.cssText = `
        position: fixed;
        pointer-events: none;
        z-index: 9999999;
        width: 20px;
        height: 20px;
        border: 3px solid red;
        border-radius: 50%;
        background: rgba(255, 0, 0, 0.2);
        transform: translate(-50%, -50%);
        transition: none;
        display: none;
    `;
    document.body.appendChild(cursor);

    const trail = document.createElement('div');
    trail.id = '__browser_cursor_trail';
    trail.style.cssText = `
        position: fixed;
        pointer-events: none;
        z-index: 9999998;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: red;
        transform: translate(-50%, -50%);
        transition: none;
        display: none;
    `;
    document.body.appendChild(trail);

    document.addEventListener('mousemove', e => {
        cursor.style.display = 'block';
        trail.style.display = 'block';
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        setTimeout(() => {
            trail.style.left = e.clientX + 'px';
            trail.style.top = e.clientY + 'px';
        }, 30);
    });

    window._browserCursor = true;
}
"""


async def inject_cursor(page):
    try:
        await page.evaluate(CURSOR_JS)
    except Exception:
        pass
