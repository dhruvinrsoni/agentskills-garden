import subprocess
import sys

def run(cmd):
    print('RUN:', ' '.join(cmd))
    subprocess.check_call(cmd)

def main():
    keep = {'README.md', '.gitignore', 'LICENSE'}
    files = subprocess.check_output(['git', 'ls-files']).decode().splitlines()
    to_remove = [f for f in files if f not in keep]
    if not to_remove:
        print('No tracked files to remove')
        return
    print(f'Removing {len(to_remove)} tracked files...')
    run(['git', 'rm', '-r', '--'] + to_remove)
    try:
        run(['git', 'commit', '-m', 'Reset main: fresh repository skeleton'])
    except subprocess.CalledProcessError:
        print('Nothing to commit')

if __name__ == '__main__':
    main()
