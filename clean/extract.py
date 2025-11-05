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
    rv = []
    for line in path.read_text().split("\n"):
        m = re.search(fr' (?P<time>\d{{2}}:\d{{2}}:\d{{2}}) .* \[(?P<board>[01]{{{n}}})\]', line)
        if not m: continue
        rv.append((m["time"], m["board"]))
    return rv

if __name__ == "__main__":
    for k, n, p in find_files("../data"):
        print("fyi", k, n)
        for t, b in process_file(p, n):
            print(t, b)
