from services.ui_helpers import compute_status, _adjust_hex_brightness


def test_compute_status_ok():
    assert compute_status(10, 5, 2) == 'OK'


def test_compute_status_low():
    assert compute_status(3, 5, 1) == 'LOW'


def test_compute_status_critical():
    assert compute_status(1, 5, 1) == 'CRITICAL'


def test_adjust_hex_brightness():
    # darken by 0.5
    result = _adjust_hex_brightness('#808080', 0.5)
    assert result.startswith('#') and len(result) == 7
