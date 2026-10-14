import importlib

# Hỗ trợ truy cập cả credentials và module pass (vì 'pass' là từ khóa trong Python)
try:
    from data.credentials import LOGIN_ACCOUNT, PASSWORD
except ImportError:
    pass_mod = importlib.import_module("data.pass")
    LOGIN_ACCOUNT = pass_mod.LOGIN_ACCOUNT
    PASSWORD = pass_mod.PASSWORD

__all__ = ["LOGIN_ACCOUNT", "PASSWORD"]
