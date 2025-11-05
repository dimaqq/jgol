import re

def time(fname, n):
    lines = open(fname).readlines()
    frob = [m.groups() for m in filter(None, [re.search(fr"(?P<time>\d\d:\d\d:\d\d).*\[[01]{{{n}}}\] --> (?P<round>\d+)", l) for l in lines])]
    if not frob: return
    hh,mm,ss = map(int, frob[0][0].split(":"))
    start = hh * 3600 + mm * 60 + ss
    startr = int(frob[0][1])
    hh,mm,ss = map(int, frob[-1][0].split(":"))
    end = hh * 3600 + mm * 60 + ss
    endr = int(frob[-1][1])
    # print(frob[0])
    # print(frob[-1])
    # print((end - start) / (endr - startr))
    return (end - start) / (endr - startr)

if __name__ == "__main__":
    import sys
    fname = sys.argv[1]
    for i in range(21):
        t = time(fname, i**2)
        if t is None: continue
        print(i**2, t)

