import os


def is_github_actions():
    return os.getenv('GITHUB_ACTIONS', '').lower() == 'true'


def is_local():
    return not is_github_actions()


def get_run_mode():
    return 'github_actions' if is_github_actions() else 'local'
