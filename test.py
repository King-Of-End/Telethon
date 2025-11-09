with open('pip.txt', encoding='utf16') as f:
    a = f.readlines()
print(a)
with open('pip.txt', 'w', encoding='utf16') as f:
    for x in a:
        f.write(x.split('==')[0] + '\n')