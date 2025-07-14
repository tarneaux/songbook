import json, sys

chords = json.load(open("chords.complete.json"))
chords_set = set(chords.keys())

def get_words_n_positions(chordline: str) -> list:
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

def make_chord_indication(chord: str) -> str:
    c = chords[chord][0]
    positions = "".join(c["positions"]).replace("x", "X")
    fingerings = "".join(c["fingerings"][0])
    return f"\\gtab{{{chord}}}{{{positions}:{fingerings}}}"


if __name__ == "__main__":
    print(make_chord_indication(sys.argv[1]))
