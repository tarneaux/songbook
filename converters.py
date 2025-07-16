import re
from typing import Optional

import chords
from enums import *

def merge_lines(chordline: str, lyricline: str) -> str:
    chordline_chords = chords.get_words_n_positions(chordline)
    l = len(lyricline)
    inner_chords = [ (c, i) for c, i in chordline_chords if i < l]
    inner_positions = [ i for _, i in inner_chords ]
    cut_lyricline = [ lyricline[a:b] for a, b in zip([0] + inner_positions, inner_positions + [l]) ]
    lyricline = (cut_lyricline.pop(0) + "".join([
        f"\\[{c}]" + (cut_lyricline.pop(0) if cut_lyricline else " ")
        for c, _ in chordline_chords
    ])).strip()
    return lyricline


def convert_solo_line(chordline: str) -> str:
    chordline = chordline.strip()
    def convert_word(w: str):
        w_stripped = w
        while w_stripped.endswith("*"):
            w_stripped = w_stripped.removesuffix('*')
        if w_stripped in chords.chords_set: return f"\\[{w}]"
        elif re.match(r"x[0-9]*", w): return f"\\rep{{{w[1:]}}}"
        else: return w
    chordline = " ".join([
        convert_word(word)
        for word in chordline.split(" ")
    ])
    return "{\\nolyrics " + chordline + "}"


indications = (
    (CTX_VERSE, ("verse", "couplet", "pre-chorus", "pré-refrain", "bridge", "interlude")),
    (CTX_CHORUS,  ("chorus", "refrain")),
    (CTX_SOLO, ("intro", "instrumental", "outro", "solo", "lead", "guitar solo", "fill", "coda", "post-"))
)

def convert_indication_line(indication_line: str) -> Context:
    part_indication = indication_line.strip()[1:-1]
    for ctx, matches in indications:
        for match in matches:
            if part_indication.lower().startswith(match):
                return ctx
    raise Exception(f"Unknown part indication: {part_indication}")

def convert_capo(line: str) -> str:
    c = parse_capo(line)
    if not c:
        raise Exception("Capo is not set at this line. This is a bug.")
    return r"\capo{" + str(c) + r"}"

def parse_capo(line: str) -> Optional[int]:
    if re.fullmatch(r"Capo [0-9]*", line):
        return int(line[5:])

def convert_chord_spec(line: str) -> Optional[str]:
    m = re.fullmatch(r"([^ ]+) +[\=\-] +([0-9xX]{6})", line)
    if m:
        return f"\\gtab{{{m.group(1)}}}{{{m.group(2).upper()}}}"


def transpose_staff(staff: list[str]) -> list[list[Optional[str]]]:
    firstcol = staff[0].find("| ")+2
    lastcol = len(staff[0]) - staff[0][::-1].find("| ") - 2
    print(lastcol)
    # TODO: Repeaters
    conv = lambda c: c if c != "" else None
    def findany(s, l, start):
        return min([
            item
            for item in [s.find(item, start) for item in l]
            if item != -1
        ])
    transposed = [
        [
            conv(string[col:findany(string, ["-", " "], col)]) if staff[i][col-1] in ["-", " "] else None
            for i, string in enumerate(staff)
        ]
        for col in range(firstcol, lastcol+1)
    ]
    return transposed

def convert_staff(staff: list[str], above: Optional[str], below: Optional[str]) -> list[str]:
    ab_offset = staff[0].find("| ")+2
    staff_t: list[list[Optional[str]]] = transpose_staff(staff)
    above = above or ""
    below = below or ""
    above_wp = chords.get_words_n_positions(above)
    below_wp = chords.get_words_n_positions(below)
    def get_next(abwp, col) -> Optional[str]:
        try:
            if abwp[0][1] < col:
                return abwp.pop(0)[0]
        except IndexError: pass
    return [
        convert_staff_column(
            column,
            get_next(above_wp, i+ab_offset),
            get_next(below_wp, i+ab_offset)
        )
        for i, column in enumerate(staff_t)
        if column != [None] * 6
    ]

def convert_staff_column(col: list[Optional[str]], above: Optional[str], below: Optional[str]) -> str:
    print(col)
    if col == ["|"]*6:
        return "\\bar"
    # if col == [None]*6:
        # return r" \notes\hsk\en"
        # return r"\hsk\zbar"
    return (
        r" \notes"
        + (r"\chord{" + above + "}" if above is not None else "")
        + (r"\textbelow{" + below + "}" if below is not None else "")
        + "".join([
            r"\str{" + str(6-string) + r"}{" + col_string + r"}"
            for string, col_string in enumerate(col)
            if col_string is not None
        ])
        + (
            # max([0] + [
            #     len(col_string)
            #     for col_string in col
            #     if col_string is not None
            # ])//1 * r"\hsk"
            (max([0] + [
                len(col_string)
                for col_string in col
                if col_string is not None
            ])-1)//2 * r"\en\notes"
        )
        + r"\en"
        + r"\zbar"
    )
