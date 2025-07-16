import re

from enums import LineType
import converters, chords

def get_line_type(line: str) -> LineType:
    if line.strip() == "":
        return LineType.LT_EMPTY
    if converters.parse_capo(line):
        return LineType.LT_CAPO
    if is_part_indication(line):
        return LineType.LT_PART_INDICATION
    if is_tab_line(line):
        return LineType.LT_TAB
    if converters.convert_chord_spec(line):
        return LineType.LT_CHORD_SPEC
    if is_note(line):
        return LineType.LT_NOTE
    words = line.split(" ")
    for w in words:
        if w in ["", "N.C.", "-", "|"] or re.match(r"x[0-9]*", w):
            continue
        while w.endswith('*'):
            w = w.removesuffix("*")
        w = w.removeprefix("(").removesuffix(")")
        if w not in chords.chords_set:
            return LineType.LT_LYRIC
    return LineType.LT_CHORD

def is_part_indication(line: str) -> bool:
    return bool(re.fullmatch(r"\[.*\]", line.strip()))

def is_note(line: str) -> bool:
    return bool(re.fullmatch(r"\{.*\}", line.strip()))

def is_tab_line(line: str) -> bool:
    return bool(re.fullmatch(r"[eBGDAE]? \| ?[\-0-9\/hp( \| )\(\)\^\>]* \| [\space]*(\(?x[0-9]*\)?)?", line))
