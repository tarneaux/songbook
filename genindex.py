TITLEIDX="titleidx"
AUTHORIDX="authoridx"

import unicodedata
def strip_accents(s):
   return ''.join(
       c for c in unicodedata.normalize('NFD', s)
       if unicodedata.category(c) != 'Mn'
    )


inp_title, inp_author = (
    open(f"{fn}.sxd").read().splitlines()[1:]
    for fn in (TITLEIDX, AUTHORIDX)
)

out_title = []
out_author = []

def idxentry(label, id):
    return f"\\idxentry{{{label}}}{{{id}}}"


while inp_title:
    title, id, link = (inp_title.pop(0) for _ in range(3))
    author, _, _ = (inp_author.pop(0) for _ in range(3))
    out_title.append(idxentry(f"{title} ({author})", id))
    out_author.append(idxentry(f"{author} - {title}", id))

for (l, fn) in ((out_title, TITLEIDX), (out_author, AUTHORIDX)):
    l.sort(key=lambda s: strip_accents(s.upper()))
    open(f"{fn}.sbx", "w").write("\n".join(l))
