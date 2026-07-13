from browser_mcp.diff import compute_diff


def test_no_changes():
    html = "<html><body><p>hello</p></body></html>"
    assert compute_diff(html, html) == ""


def test_addition():
    before = "<html><body><p>hello</p></body></html>"
    after = "<html><body><p>hello world</p></body></html>"
    diff = compute_diff(before, after)
    assert diff != ""
    assert "world" in diff


def test_removal():
    before = "<html><body><p>hello world</p></body></html>"
    after = "<html><body><p>hello</p></body></html>"
    diff = compute_diff(before, after)
    assert diff != ""
    assert "world" in diff


def test_completely_different():
    before = "<html><body>old</body></html>"
    after = "<html><body>new</body></html>"
    diff = compute_diff(before, after)
    assert diff != ""
    assert "old" in diff
    assert "new" in diff
