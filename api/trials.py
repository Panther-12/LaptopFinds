items = [9,4,6]


def last_item(array):
    last_item = ''
    for item in enumerate(items):
        if item[0] == len(items) - 1:
            last_item = item[1]
    return last_item

result = last_item(items)
print(result)