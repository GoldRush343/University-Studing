c: int = int(input())

i, j = 1, 1
cnt = 0
last: int = 1
while True:
    a: int = i ** 2
    b: int = j ** 3
    if cnt == c:
        print(last)
        break
    cnt += 1
    if a == b:
        i += 1
        j += 1
    elif i ** 2 <= j ** 3:
        last = i ** 2
        i += 1
    else:
        last = j ** 3
        j += 1
