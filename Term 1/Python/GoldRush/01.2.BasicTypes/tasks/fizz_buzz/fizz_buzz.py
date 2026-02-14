def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    answer = [x for x in range(0,n+1)]
    for i in range(0,n+1,3):#replace every 3rd argument
        answer[i] = 'Fizz'
    for i in range(0,n+1, 5):#replace every 5th argument
        answer[i] = "Buzz"
    for i in range(0,n+1,15):#replace every 15th argument
        answer[i] = "FizzBuzz"
    return answer[1:]

