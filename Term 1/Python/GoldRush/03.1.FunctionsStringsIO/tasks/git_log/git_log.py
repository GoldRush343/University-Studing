import typing as tp

def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    strs = inp.read().split('\n')
    for str in strs:
        if len(str) != 0:
            end = str.rfind('\t')+1
            n = len(str) - end + 7
            res = str[:7] + "." * (80 - n) + str[end:]
            out.write(res + '\n')

