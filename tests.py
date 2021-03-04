lists={'b': '2020-01-02', 'a': '0029-09-22', 'c': '3456-03-12'}
print(lists.keys())
print(lists.values())
num=0
for key in lists.keys():
    print(key)
    print(lists[key])
    if num > 2:
        num = num %3
    color = ['primary', 'success', 'danger'][num]
    print(color)
    num+=1