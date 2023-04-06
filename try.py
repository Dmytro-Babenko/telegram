from functools import reduce

k = {
    'a': 'q',
    'b': 'f',
    'c': 1
}

text = reduce(lambda x, y: '\n'.join((x, y)), (f'{a}:{b}' for a, b in k.items()))
text = '\n'.join((f'{a}:{b}' for a, b in k.items()))
print(text)