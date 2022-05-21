def test():
    result = []

    text = ['A', 'B', 'C']
    text1 = ['C', 'D', 'E']
    text2 = ['F', 'G', 'H']
    D = 5
    E = 6
    F = 7
    if E < D:
        result.extend(text)
    elif E > D:
        result.extend(text1)
    elif E < 7:
        result.extend(text2)
    print(result[0])


test()