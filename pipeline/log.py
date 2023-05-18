def log(text):
    f = open("logs.txt", "a")
    f.write(text + '\n')
    f.close()
    print(text)