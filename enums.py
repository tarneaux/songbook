from dataclasses import dataclass
from enum import Enum

class LineType(Enum):
    LT_SOLO = 1
    LT_CHORD = 2
    LT_LYRIC = 3
    LT_CAPO = 4
    LT_PART_INDICATION = 5
    LT_TAB = 6
    LT_CHORD_SPEC = 7
    LT_NOTE = 8
    LT_EMPTY = 9

@dataclass
class Context:
    begin: str
    end: str

CTX_VERSE = Context(r"\beginverse", r"\endverse")
CTX_CHORUS = Context(r"\beginchorus", r"\endchorus")
CTX_SOLO = Context(r"\ifchorded \beginverse*", r"\endverse \fi")

CTX_TABLATURE = Context(r"""
\ifchorded
\begin{music}
\instrumentnumber{1}
\nobarnumbers
\TAB1
\setlines1{6}
\startpiece
""", r"""\endpiece
\end{music} \fi
""")

