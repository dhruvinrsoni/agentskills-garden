#!/usr/bin/env python3
import argparse
import os
from scripts.orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(description='Local Skill Runner (minimal)')
    parser.add_argument('--model-endpoint', help='Optional model HTTP endpoint (JSON), e.g. TGI', default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    orch = Orchestrator(repo_root=repo_root, model_endpoint=args.model_endpoint)

    print('Local Skill Runner (minimal). Type your task or "exit".')
    while True:
        try:
            user = input('\nTask> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nbye')
            break
        if not user:
            continue
        if user.lower() in ('exit', 'quit'):
            break
        res = orch.run_task(user)
        if 'error' in res:
            print('Error:', res['error'])
            continue
        print('\n--- Skill Used:', res['skill'])
        print('\n--- Prompt (truncated):\n')
        print(res['prompt'][:2000])
        print('\n--- Output:\n')
        print(res['output'])


if __name__ == '__main__':
    main()
