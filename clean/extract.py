import pathlib
import re


def find_files(where):
    rv = []
    for p in pathlib.Path(where).glob("*.log"):
        try:
            m = re.fullmatch(r'(?P<algo>.*)-(?P<n>[0-9]+)[.]log', p.name)
            rv.append((m["algo"], m["n"], p))
        except Exception as e: print(p.name, e)
    return rv

def process_file(path, n):
    starttime = None
    rv = []
    for line in path.read_text().split("\n"):
        if "Reset" in line: continue
        m = re.search(fr' (?P<time>\d{{2}}:\d{{2}}:\d{{2}}) .* \[(?P<board>[01.]{{{n}}})\]', line)
        if not m: continue
        # Unit tests collapse relation events, the board is filled all at once
        if "WARNING" not in line and "." in m["board"]: continue
        hh,mm,ss = map(int, m["time"].split(":"))
        abstime = hh*3600 + mm*60 + ss
        if starttime is None: starttime = abstime
        time = abstime - starttime
        rv.append((time, m["board"]))
    return rv

def expand_contract(data):
    try:
        it = iter(data)
        ct, cb = next(it)
        yield ct, cb
        while True:
            t, b = next(it)
            # 0, cat; 0, dog --> 0, cat
            if t == ct: continue
            # 0, cat; 2, dog --> 0, cat; 1, cat; 2, dog
            for i in range(ct + 1, t):
                yield i, cb
            yield t, b
            ct, cb = t, b
    except StopIteration:
        return


if __name__ == "__main__":
    for k, n, p in find_files("../data"):
        print("fyi", k, n)
        for t, b in expand_contract(process_file(p, n)):
            print(t, b)
