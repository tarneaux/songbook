import json

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
