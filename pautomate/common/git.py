"""
Run Git commands in separate processes
"""
import shlex
import subprocess
from os import path
from typing import Dict

from .printing import print_green
from .printing import print_yellow


def shell(command: str) -> str:
    """Execute shell command

    Arguments:
        command {str} -- to execute in shell

    Returns:
        str -- output of the shell
    """
    print(command)
    cmd = shlex.split(command)
    out, err = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).communicate()
    stdout, stderr = out.decode('utf-8'), err.decode('utf-8')
    output_lines = f'{stdout}\n{stderr}'.split('\n')
    for index, line in enumerate(output_lines):
        if '*' in line:
            output_lines[index] = f'\033[93m{line}\033[0m'
    return '\n'.join(output_lines)


def shell_first(command: str) -> str:
    """Execute in shell

    Arguments:
        command {str} -- to execute in shell

    Returns:
        str -- first line of stdout
    """
    print(command)
    cmd = shlex.split(command)
    out, _ = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).communicate()
    return out.decode('utf-8').split('\n')[0]


def hard_reset(repo_path: str) -> str:
    """reset --hard

    Arguments:
        repo_path {str} -- path to repo to reset
    """
    return shell(f'git -C {repo_path} reset --hard')


def reset_to_origin_develop(repo_path: str) -> str:
    """checkout develop && reset --hard origin/$(git rev-parse --abbrev-ref HEAD)

    Arguments:
        repo_path {str} -- path to repo to reset
    """
    shell(f'git -C {repo_path} fetch --prune')
    shell(f'git -C {repo_path} checkout develop')
    current_branch = shell_first(
        f'git -C {repo_path} rev-parse --abbrev-ref HEAD --',
    )
    return shell(f'git -C {repo_path} reset --hard origin/{current_branch}')


def get_branches_info(repo_path: str) -> str:
    """git branch -a

    Arguments:
        repo_path {str} -- path to repo
    """
    return shell(f'git -C {repo_path} branch -a')


def fetch_repo(
    working_directory: str,
    repo_path: str,
    url: str,
    summery_info: Dict[str, str],
) -> None:
    """Clone / Fetch repo

    Arguments:
        working_directory {str} -- target directory
        repo_path {str} -- repo repo_path
        url {str} -- repo url in gitlab
        summery_info {Dict[str, str]} -- the result of the cloning/fetching
    """
    repo_path = path.join(working_directory, repo_path)
    if path.isdir(repo_path):
        print_green(f'Fetching {repo_path}')
        shell_first(f'git -C {repo_path} fetch --prune')
        remote_banches = shell(f'git -C {repo_path} ls-remote --heads')
        current_branch = shell_first(
            f'git -C {repo_path} rev-parse --abbrev-ref HEAD --',
        )
        if f'refs/heads/{current_branch}' in remote_banches:
            shell_first(
                f'git -C {repo_path} fetch --prune -u '
                f'origin {current_branch}:{current_branch}',
            )
        else:
            print_yellow(f'{current_branch} does not exist on remote')

        if ('refs/heads/develop' in remote_banches and current_branch != 'develop'):  # noqa E501
            shell_first(
                f'git -C {repo_path} fetch --prune origin develop:develop',
            )
    else:
        print_green(f'Cloning {repo_path}')
        shell_first(f'git clone {url} {repo_path}')
        current_branch = shell_first(
            f'git -C {repo_path} rev-parse --abbrev-ref HEAD --',
        )
    summery_info.update({repo_path: current_branch})
