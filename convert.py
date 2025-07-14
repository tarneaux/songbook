import re,sys,os
from typing import List, Optional

import testers, converters, chords

from enums import *

def sanitize_ug(text: str):
    text = text.replace('\xa0', ' ').replace("\u2005", " ")
    text = "\n".join([
        line.replace("|", " | ").replace(" |  ", " | ").replace("  | ", " | ")
        for line in text.splitlines()
    ])
    return text

def get_song_start(title: str, artist: str) -> str:
    return r"\beginsong{" + title +"}[by={" + artist + "}]"

# print("\n\n\\zbar\n\n".join([
#     convert_staff(transpose_staff(group))
#     for group in groups
# ]))

def convert(text: str, title: str, artist: str):
    CTX_SONG = Context(get_song_start(title, artist), r"\endsong")
    tf = sanitize_ug(text)
    tl = tf.splitlines()
    line_types = [testers.get_line_type(line) for line in tl]
    out = []
    context: List[Context] = []
    def out_add(s: str):
        for line in s.splitlines():
            if line != "":
                out.append(" "*len(context) + line)
            else:
                out.append("")
    def start_ctx(ctx: Context):
        out_add("\n")
        out_add(ctx.begin)
        context.append(ctx)
    def end_ctx() -> bool:
        if len(context) > 0:
            out_add(context.pop().end)
            out_add("")
            return True
        else:
            return False
    def ensure_ctx(ctx: Context, new: bool):
        if len(context) == 2 and (new or context[1] != ctx):
            end_ctx()
        if len(context) != 2:
            start_ctx(ctx)
    start_ctx(CTX_SONG)
    skip = 0
    for i, t in enumerate(line_types):
        if t == LineType.LT_CHORD and (
            i == len(tl) - 1
            or (line_types[i+1] not in (LineType.LT_LYRIC, LineType.LT_TAB))
        ):
            line_types[i] = LineType.LT_SOLO
    for i in range(len(tl)):
        if skip:
            skip -= 1
            continue
        match line_types[i]:
            case LineType.LT_CAPO:
                out_add(converters.convert_capo(tl[i]))
            case LineType.LT_CHORD: pass
            case LineType.LT_EMPTY: pass
            case LineType.LT_LYRIC:
                # assert line_types[i-1] in {LineType.LT_CHORD, LineType.LT_EMPTY}
                if line_types[i-1] == LineType.LT_CHORD:
                    out_add(converters.merge_lines(tl[i-1], tl[i]))
                else:
                    out_add(tl[i])
            case LineType.LT_SOLO:
                if context[-1] != CTX_SOLO:
                    print(f"WARNING: Automatically switching to solo context at line {i}")
                    ensure_ctx(CTX_SOLO, False)
                out_add(converters.convert_solo_line(tl[i]))
            case LineType.LT_PART_INDICATION:
                ctx = converters.convert_indication_line(tl[i])
                ensure_ctx(ctx, new=True)
            case LineType.LT_CHORD_SPEC:
                cs = converters.convert_chord_spec(tl[i])
                if cs is None:
                    print(i)
                    raise Exception("Not a chord spec line. This indicates a bug.")
                out_add(cs)
            case LineType.LT_NOTE:
                out_add(r"\musicnote{" + tl[i][1:-1] + r"}")
            case LineType.LT_TAB:
                above = tl[i-1] if line_types[i-1] != LineType.LT_EMPTY else None
                below = tl[i+6] if line_types[i+6] != LineType.LT_EMPTY else None
                ensure_ctx(CTX_TABLATURE, new=False)
                assert [t == LineType.LT_TAB for t in line_types[i:i+6]] == [True] * 6
                for line in converters.convert_staff(tl[i:i+6], above, below):
                    out_add(line)
                skip = 5 if below is None else 6
    while end_ctx(): pass
    out_str = "\n".join(out)
    return out_str

def main():
    if len(sys.argv) != 2:
        print("needed arg: <filename>")
        exit(1)
    path = sys.argv[1]

    if not path.startswith(os.path.expanduser("~/ug-tabs")):
        print(f"{path} is not part of ~/ug-tabs.")
        exit(1)
    
    stripped_path = path.removeprefix(os.path.expanduser("~/ug-tabs/"))
    match = re.fullmatch(r"(.*)/(.*)_([^_]*)_[0-9]+.txt", stripped_path)
    if match is None:
        print("Invalid format, missing _[0-9]+.txt at the end")
        exit(1)
    artist = match.group(1)
    title = match.group(2)

    text = open(path, encoding="utf-8").read()

    out_str = convert(text, title, artist.replace("_", " "))

    os.makedirs(os.path.join("songs", artist), exist_ok=True)
    out_path = os.path.join("songs", artist, f"{title}.tex")

    if not os.path.exists(out_path):
        open(os.path.join("songs", "index.tex"), "a").write(f"\\input{{{out_path}}}\n")
    else:
        # TODO: Better handle this
        print(f"WARNING: \"{out_path}\" already exists, overwriting and not adding to index")

    open(out_path, "w").write(out_str)

if __name__ == "__main__":
    main()
