import pathlib
import re

import numpy as np
from PIL import Image


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
    interpolated = [rv[-1][0] * i * 10 // len(rv) for i in range(len(rv))]
    return [(i, b) for i, (_, b) in zip(interpolated, rv)]

CONV = {
    (".", "0"): 0,
    (".", "."): tuple,  # not allowed
    (".", "1"): 255,
    ("0", "0"): 0,
    ("0", "."): 100,
    ("0", "1"): 255,
    ("1", "0"): 0,
    ("1", "."): 155,
    ("1", "1"): 255,
}

def grayblack(data):
    last = None
    for d in data:
        if last is None:
            assert "." not in d
            last = d
        yield bytes(255 - CONV[it] for it in zip(last, d))


def expand_contract(data):
    try:
        it = iter(data)
        ct, cb = next(it)
        yield cb
        while True:
            t, b = next(it)
            # 0, cat; 0, dog --> 0, cat
            if t == ct: continue
            # 0, cat; 2, dog --> 0, cat; 1, cat; 2, dog
            for i in range(ct + 1, t):
                yield cb
            yield b
            ct, cb = t, b
    except StopIteration:
        return


def save_gif(data, path):
    side = int(len(data[0]) ** 0.5)
    frames = [Image.frombytes("L", (side, side), frame).resize((side*10, side*10), resample=0) for frame in data]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

if __name__ == "__main__":
    for k, n, p in find_files("../data"):
        print("fyi", k, n)
        frames = tuple(grayblack(expand_contract(process_file(p, n))))
        save_gif(frames, f"{k}-{n}.gif")
        for b in frames:
            print(b)
