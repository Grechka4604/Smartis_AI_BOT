




with open('promt.txt', 'r', encoding='utf-8') as file:
    lines = file.read()
content = ''.join(lines)
print(content)