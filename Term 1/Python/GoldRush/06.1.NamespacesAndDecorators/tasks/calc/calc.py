import math
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace using input() and print()"""
    if context is None:
        env = {}
    else:
        env = context.copy()
    env['__builtins__'] = {}

    while True:
        try:
            expression = input(PROMPT)
            result = eval(expression, env)
            print(result)
        except EOFError:
            print()
            break

if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
