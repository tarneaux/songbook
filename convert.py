import json,re,sys
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

chords = json.load(open("chords.complete.json"))
chords_set = set(chords.keys())

class LineType(Enum):
    LT_SOLO = 1
    LT_CHORD = 2
    LT_LYRIC = 3
    LT_CAPO = 4
    LT_INDICATION = 5
    LT_EMPTY = 6

def get_line_type(line: str) -> LineType:
    if parse_capo(line):
        return LineType.LT_CAPO
    if is_part_indication(line):
        return LineType.LT_INDICATION

    if line == "":
        return LineType.LT_EMPTY
    words = line.split(" ")
    for w in words:
        if w == "" or re.match(r"x[0-9]*", w):
            continue
        if w not in chords_set:
            if w == "|":
                return LineType.LT_SOLO
            return LineType.LT_LYRIC
    return LineType.LT_CHORD

def get_chords_in_line(chordline: str) -> list:
    return list(zip(
        [
            chord
            for chord in chordline.split(" ")
            if chord != ""
        ],
        [
            i
            for i in range(len(chordline))
            if chordline[i] != " " and (" "+chordline)[i] == " "
        ]
    ))

def merge_lines(chordline: str, lyricline: str) -> str:
    chords = get_chords_in_line(chordline)
    chords.reverse() # To prevent adding all except 1st chord at the wrong position
    for c, i in chords:
        if i < len(lyricline):
            lyricline = lyricline[:i] + f"\\[{c}]" + lyricline[i:]
        else:
            lyricline += f"\\[{c}]"
    return lyricline


def make_solo_line(chordline: str) -> str:
    chordline = chordline.strip()
    def convert_word(w: str):
        if w in chords_set: return f"\\[{w}]"
        elif re.match(r"x[0-9]*", w): return f"\\rep{{{w[1:]}}}"
        else: return w
    chordline = " ".join([
        convert_word(word)
        for word in chordline.split(" ")
    ])
    return "{\\nolyrics " + chordline + "}"


def sanitize_ug(text: str):
    text = text.replace('\xa0', ' ').replace("\u2005", " ")
    text = "\n".join([
        line.replace("|", " | ").replace(" |  ", " | ").replace("  | ", " | ")
        for line in text.splitlines()
    ])
    return text

def is_part_indication(line: str) -> bool:
    return bool(re.fullmatch(r"\[.*\]", line.strip()))

def get_song_start(title: str, artist: str) -> str:
    return r"\beginsong{" + title +"}[by={" + artist + "}]"

def parse_capo(line: str) -> Optional[int]:
    if re.fullmatch(r"Capo [0-9]*", line):
        return int(line[5:])

@dataclass
class Context:
    begin: str
    end: str

CTX_VERSE = Context(r"\beginverse", r"\endverse")
CTX_CHORUS = Context(r"\beginchorus", r"\endchorus")
CTX_SOLO = Context(r"\ifchorded \beginverse*", r"\endverse \fi")

def main():
    if len(sys.argv) != 4:
        print("needed args: <path> <name> <artist>")
        exit(1)

    tf = open(sys.argv[1], encoding="utf-8").read()
    title = sys.argv[2]
    artist = sys.argv[3]
    CTX_SONG = Context(get_song_start(title, artist), r"\endsong")
    tf = sanitize_ug(tf)
    tl = tf.splitlines()
    line_types = [get_line_type(line) for line in tl]
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
    def ensure_ctx(ctx: Context):
        if len(context) == 2 and context[1] != ctx:
            end_ctx()
        if len(context) != 2:
            start_ctx(ctx)
    start_ctx(CTX_SONG)
    for i in range(len(tl)):
        match line_types[i]:
            case LineType.LT_CAPO:
                c = parse_capo(tl[i])
                out_add(r"\capo{" + str(c) + r"}")
            case LineType.LT_CHORD:
                if i == len(tl) - 1 or line_types[i+1] != LineType.LT_LYRIC:
                    out_add(make_solo_line(tl[i]))
            case LineType.LT_EMPTY: pass
            case LineType.LT_LYRIC:
                out_add(merge_lines(tl[i-1], tl[i]))
            case LineType.LT_SOLO:
                out_add(make_solo_line(tl[i]))
            case LineType.LT_INDICATION:
                part_indication = tl[i].strip()[1:-1]
                if part_indication.startswith("Verse") or part_indication.startswith("Couplet") or part_indication.startswith("Pre-chorus") or part_indication.startswith("Pré-refrain") or part_indication.startswith("Bridge"):
                    ensure_ctx(CTX_VERSE)
                elif part_indication.startswith("Chorus") or part_indication.startswith("Refrain"):
                    ensure_ctx(CTX_CHORUS)
                elif part_indication in ["Intro", "Instrumental", "Outro"]:
                    ensure_ctx(CTX_SOLO)
                    # out_add(r"\musicnote{" + part_indication + r"}")
                else:
                    raise Exception(f"Unknown part indication: {part_indication}")
    while end_ctx(): pass
    out_str = "\n".join(out)
    open("scriptout.tex", "w").write(out_str)

if __name__ == "__main__":
    main()
