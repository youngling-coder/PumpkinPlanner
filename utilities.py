import re

def password_valid(psw: str) -> str | bool:

    valid = ""
    if len(psw) < 8:
        valid += "\n⚠ Password must be at least 8 symbols long!"
    if not bool(re.search(r'\d', psw)):
        valid += "\n⚠ Password must contain numbers!"
    if not bool(re.search(r'[a-zA-Z]', psw)):
        valid += "\n⚠ Password must contain any letters!"

    return not valid if not valid else valid

def username_valid(username: str) -> str | bool:
    valid = ""
    if len(username) < 4:
        valid += "\n⚠ Username must be at least 4 symbols long!"
    if not bool(re.match(r'^[a-zA-Z0-9-._]+(?:[a-zA-Z-._]+?[a-zA-Z0-9-._])*$', username)):
        valid += "\n⚠ Username must contain only nubers, uppercase and lovercase letters and '-', '_', '*' signs!"
    if not bool(re.search(r'[a-zA-Z]', username)):
        valid += "\n⚠ Username must contain any letters!"

    return not valid if not valid else valid
