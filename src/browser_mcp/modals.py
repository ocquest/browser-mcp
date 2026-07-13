MODAL_DETECTOR_JS = """
() => {
    const modals = [];

    // 1. ARIA dialogs and alertdialogs
    document.querySelectorAll('[role="dialog"], [role="alertdialog"]').forEach(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        modals.push({
            type: 'role-dialog',
            role: el.getAttribute('role'),
            aria_modal: el.getAttribute('aria-modal'),
            visible: rect.width > 0 && rect.height > 0,
            text: (el.textContent || '').trim().substring(0, 300),
            id: el.id || null,
            classes: Array.from(el.classList),
            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
            z_index: style.zIndex
        });
    });

    // 2. Native <dialog> elements
    document.querySelectorAll('dialog').forEach(el => {
        if (el.open) {
            const rect = el.getBoundingClientRect();
            modals.push({
                type: 'native-dialog',
                open: el.open,
                text: (el.textContent || '').trim().substring(0, 300),
                id: el.id || null,
                classes: Array.from(el.classList),
                rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
            });
        }
    });

    // 3. Fixed/absolute overlays that cover > 50% viewport
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const viewportArea = vw * vh;
    document.querySelectorAll('div, section, aside').forEach(el => {
        const style = window.getComputedStyle(el);
        const pos = style.position;
        if (pos !== 'fixed' && pos !== 'absolute') return;
        const rect = el.getBoundingClientRect();
        const area = rect.width * rect.height;
        if (area < viewportArea * 0.3) return;
        if (rect.left < 0 || rect.top < 0) return;
        const bg = style.backgroundColor;
        const opacity = style.opacity;
        const hasOverlayClasses = Array.from(el.classList).some(cls =>
            /modal|overlay|popup|backdrop|cookie|banner|drawer|sidebar|notification|popover|dialog|lightbox/i.test(cls)
        );
        if (!hasOverlayClasses && (bg === 'transparent' || bg === 'rgba(0, 0, 0, 0)' || parseFloat(opacity) < 0.1)) return;
        modals.push({
            type: 'overlay',
            position: pos,
            visible: rect.width > 0 && rect.height > 0,
            text: (el.textContent || '').trim().substring(0, 200),
            id: el.id || null,
            classes: Array.from(el.classList),
            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
            z_index: style.zIndex,
            background: bg,
            opacity: opacity
        });
    });

    // Deduplicate by text and position
    const seen = new Set();
    return modals.filter(m => {
        const key = m.text.substring(0, 50) + m.rect.top + m.rect.left;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}
"""


async def detect_modals(page):
    try:
        result = await page.evaluate(MODAL_DETECTOR_JS)
        if not result:
            return ""
        lines = ["\n📦 Modals/overlays detected:"]
        for m in result:
            info = f"  [{m['type']}]"
            if m.get('id'):
                info += f" #{m['id']}"
            if m.get('classes') and len(m['classes']) > 0:
                info += f" .{m['classes'][0]}"
            if m.get('aria_modal'):
                info += f" aria-modal={m['aria_modal']}"
            info += f" visible={m.get('visible', True)}"
            if m.get('text'):
                txt = m['text'].replace('\n', ' ').strip()
                info += f" text=\"{txt[:150]}\""
            lines.append(info)
        return "\n".join(lines)
    except Exception:
        return ""
