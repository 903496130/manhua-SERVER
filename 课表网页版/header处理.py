header = {}
while 1:
    line = input()
    if line == "end":
        break
    if ":" not in line:
        continue

    else:
        arr = line.split(": ")
        header[arr[0]] = arr[1]

print(header)