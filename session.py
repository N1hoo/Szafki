_current_user = None


def set_current_user(user: dict | None):
    global _current_user
    _current_user = user


def get_current_user() -> dict | None:
    return _current_user


def clear_current_user():
    set_current_user(None)


def is_admin() -> bool:
    u = get_current_user()
    return bool(u and u.get('role') == 'admin')
