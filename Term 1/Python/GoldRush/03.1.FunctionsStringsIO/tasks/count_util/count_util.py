from pygments.lexer import words
import argparse

parser = argparse.ArgumentParser()
# nargs=3
parser.add_argument('-l', '--lines', action='store_true')
parser.add_argument('-m', '--chars', action='store_true')
parser.add_argument('-L', '--longest_line', action='store_true')
parser.add_argument('-w', "--words", action="store_true")


def count_util(text: str, flags: str | None = None) -> dict[str, int]:
    """
    :param text: text to count entities
    :param flags: flags in command-like format - can be:
        * -m stands for counting characters
        * -l stands for counting lines
        * -L stands for getting length of the longest line
        * -w stands for counting words
    More than one flag can be passed at the same time, for example:
        * "-l -m"
        * "-lLw"
    Ommiting flags or passing empty string is equivalent to "-mlLw"
    :return: mapping from string keys to corresponding counter, where
    keys are selected according to the received flags:
        * "chars" - amount of characters
        * "lines" - amount of lines
        * "longest_line" - the longest line length
        * "words" - amount of words
    """

    data = {'lines': 0, 'words': 0, 'chars': 0, 'longest_line': 0}
    data['lines'] = text.count('\n')
    data['chars'] = len(text)
    data['longest_line'] = max(map(len, text.split('\n')))
    data['words'] = len([w for w in text.replace(' ', '*').replace('\n', '*').split('*') if w != ""])
    # for string in text.split('\n'):
    #     if string != '':
    #         data['lines'] += 1;
    #         data['chars'] += len(string) + 1
    #         data['longest_line'] = max(len(string), data['longest_line'])
    #         data['words'] += len([i for i in string.split(' ') if i != ''])

    if flags is None:
        return data
    args_dict = vars(parser.parse_args(flags.split()))
    if True not in args_dict.values():
        return data
    ans = {}
    for key, val in args_dict.items():
        if val:
            ans[key] = data[key]
    return ans
