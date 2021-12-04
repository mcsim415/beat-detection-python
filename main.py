import beatAnalyze

outFile = open("data.txt", 'w')


def callback(passing, arrow_type, direction, pattern, seed):
    out = str(seed)+" "
    if not passing == 0:
        out += "pass"
    else:
        if arrow_type == 0:
            out += "wall "
        else:
            out += "block "

        if direction == 1:
            out += "left "
        elif direction == 2:
            out += "right "
        elif direction == 3:
            out += "up "
        elif direction == 4:
            out += "down "

        out += str(pattern)
    print(out)
    outFile.write(out+'\n')


if __name__ == '__main__':
    try:
        beatAnalyze.analyze("https://www.youtube.com/watch?v=", callback)
    except:
        pass
    outFile.close()
