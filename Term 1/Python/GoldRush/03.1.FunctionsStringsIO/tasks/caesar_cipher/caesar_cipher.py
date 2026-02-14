from string import ascii_lowercase, ascii_uppercase

from plotly.data import medals_wide


def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    ans = ''
    size  = len(message)
    for i in range(size):
        if message[i].islower():
            tmp = ord(message[i]) - ord('a')
            ans += ascii_lowercase[(tmp + n) % 26]
        elif message[i].isupper():
            tmp = ord(message[i]) - ord('A')
            ans += ascii_uppercase[(tmp + n) % 26]
        else:
            ans += message[i]
    return ans
