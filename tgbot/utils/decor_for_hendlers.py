def need_admin():
    def decorator(func):
        setattr(func, 'need_admins', True)
        return func
    return decorator