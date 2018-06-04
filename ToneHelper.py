# class for dealing with tones and notes
class ToneHelper:
    # used to map notes to sound frequencies
    note_map = {
        "C#": 37, "D#": 39, "F#": 42, "G#": 44, "A#": 46,
        "Db": 37, "Eb": 39, "Gb": 42, "Ab": 44, "Bb": 46,
        "D": 38, "C": 36,  "E": 40, "F": 41, "G": 43, "A": 45, "B": 47
    }

    chromatic = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

    # used for translating fret-based input
    guitar_map_standard_tuning = dict(E=chromatic[-8:] + chromatic[:-8], A=chromatic[-3:] + chromatic[:-3],
                                      D=chromatic[-10:] + chromatic[:-10], G=chromatic[-5:] + chromatic[:-5],
                                      B=["B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb"])

    # used for translating chords to notes
    chord_dict = {
        "dim7*":   [0, 9, 5, 18],
        "dim7**":  [0, 6, 10, 13, 19],
        "dim7***": [0, 6, 9, 15],
        "aug7*":   [0, 11, 16, 20],
        "aug7**":  [0, 8, 11, 16],
        "aug7***": [0, 8, 10, 16],
        "dim*":    [0, 6, 12, 15],
        "dim**":   [0, 6, 9, 15],
        "dim***":  [0, 3, 6, 12],
        "aug*":    [0, 4, 8, 12, 16],
        "aug**":   [0, 4, 8, 12],
        "aug***":  [0, 4, 8, 12],
        "sus4*":   [0, 7, 12, 17, 19, 24],
        "sus4**":  [0, 7, 12, 17, 19],
        "sus4***": [0, 7, 12, 17],
        "sus2*":   [0, 14, 19, 24],
        "sus2**":  [0, 7, 12, 14, 19],
        "sus2***": [0, 7, 12, 14],
        "mM7*":    [0, 11, 15, 19],
        "mM7**":   [0, 7, 11, 15, 21],
        "mM7***":  [0, 3, 7, 11],
        "m7b5*":   [0, 10, 15, 18],
        "m7b5**":  [0, 6, 10, 15],
        "m7b5***": [0, 6, 11, 16],
        "maj6*":   [0, 9, 16, 19],
        "maj6**":  [0, 7, 12, 16, 21],
        "maj6***": [0, 4, 9, 12],
        "m6*":     [0, 9, 15, 19],
        "m6**":    [0, 7, 12, 15, 21],
        "m6***":   [0, 7, 9, 16],
        "maj7*":   [0, 11, 16, 19],
        "maj7**":  [0, 7, 11, 16, 19],
        "maj7***": [0, 7, 11, 16],
        "maj*":    [0, 7, 12, 16, 19, 24],
        "maj**":   [0, 7, 12, 16, 19],
        "maj***":  [0, 7, 12, 16],
        "m7*":     [0, 10, 15, 19],
        "m7**":    [0, 7, 10, 15, 19],
        "m7***":   [0, 3, 10],
        "m*":      [0, 7, 12, 15, 19, 24],
        "m**":     [0, 7, 12, 15, 19],
        "m***":    [0 - 12, 5 - 12, 8 - 12, 12 - 12],  # based off of 5th string root
        "7*":      [0, 7, 10, 16, 19],
        "7**":     [0, 7, 10, 16, 19],
        "7***":    [0, 4, 10, 12],
        "13*":     [0, 10, 16, 21],
        "13**":    [0, 4, 10, 14, 21]
    }

    major_keys = {
        'Cb': -7, 'Gb': -6, 'Db': -5, 'Ab': -4, 'Eb': -3, 'Bb': -2, 'F#': 6, 'C#': 7, 'F': -1,
        'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5
    }

    minor_keys = {
        'Ab': -7, 'Eb': -6, 'Bb': -5, 'F#': 3, 'C#': 4, 'G#': 5, 'D#': 6, 'A#': 7, 'F': -4,
        'C': -3, 'G': -2, 'D': -1, 'A': 0, 'E': 1, 'B': 2
    }

    patterns = {
        "4/4:1": ["03-1-2-03-2-1"],
        "4/4:2": ["0-1-2-3-2-1"],
    }

    scale_dict = {
        "C":  ["C", "D", "E", "F", "G", "A", "B"],
        "C#": ["C#", "D#", "E#", "F#", "G#", "A#", "B#"],
        "Db": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"],
        "D":  ["D", "E", "F#", "G", "A", "B", "C#"],
        "D#": ["D#", "E#", "G", "G#", "A#", "B#", "D"],
        "Eb": ["Eb", "F", "G", "Ab", "Bb", "C", "D"],
        "E":  ["E", "F#", "G#", "A", "B", "C#", "D#"],
        "F":  ["F", "G", "A", "Bb", "C", "D", "E"],
        "F#": ["F#", "G#", "A#", "B", "C#", "D#", "E#"],
        "Gb": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],
        "G":  ["G", "A", "B", "C", "D", "E", "F#"],
        "G#": ["G#", "A#", "B#", "C#", "D#", "E#", "G"],
        "Ab": ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],
        "A":  ["A", "B", "C#", "D", "E", "F#", "G#"],
        "A#": ["A#", "B#", "D", "D#", "E#", "G", "A"],
        "Bb": ["Bb", "C", "D", "Eb", "F", "G", "A"],
        "B":  ["B", "C#", "D#", "E", "F#", "G#", "A#"]
    }

    rn_scale = {
        "vii": 6, "vi": 5, "iii": 2, "ii": 1, "iv": 3, "v": 4, "i": 0
    }

    @staticmethod
    def get_key(k: str):
        """
        Returns the number of sharps / flats for a given key.
        :param k: the key signature
        :return: the number of sharps / flats and if the key is major / minor
        """

        if "maj" in k:
            for element in ToneHelper.major_keys:
                if element == k[:2]:
                    return ToneHelper.major_keys[element], 0
            for element in ToneHelper.major_keys:
                if element == k[0]:
                    return ToneHelper.major_keys[element], 0
        elif "m" in k:
            for element in ToneHelper.minor_keys:
                if element == k[:2]:
                    return ToneHelper.minor_keys[element], 1
            for element in ToneHelper.minor_keys:
                if element == k[0]:
                    return ToneHelper.minor_keys[element], 1
        else:
            raise ValueError

    @staticmethod
    def shift_to_scale(shift: str, base: str) -> str:
        """
        Shifts into a new key given a base note.
        :param shift: the chord's tonic to shift to
        :param base: the original chord
        :return: the new key
        """
        return ToneHelper.scale_dict[base][ToneHelper.rn_scale[shift]]

    @staticmethod
    def sharp_flat_shifted_note(sf: str, shift: str, base: str) -> str:
        """
        Shifts notes affected by accidentals.
        :param sf: number of sharps / flats
        :param shift: roman numeral number to shift
        :param base: root key
        :return: the note in corresponding key
        """
        note = None

        if sf == "bb":
            note = ToneHelper.scale_dict[base][ToneHelper.rn_scale[shift] - 1]
        elif sf == "b":
            note = ToneHelper.shift_to_scale(shift, base)
            for i in range(len(ToneHelper.chromatic)):
                if ToneHelper.chromatic[i][-2:] == note or ToneHelper.chromatic[i][:2] == note:
                    return ToneHelper.chromatic[(i - 1 + 12) % 12][-2:]
        elif sf == "##":
            note = ToneHelper.scale_dict[base][ToneHelper.rn_scale[shift] + 1]
        elif sf == "#":
            note = ToneHelper.shift_to_scale(shift, base)
            for i in range(len(ToneHelper.chromatic)):
                if ToneHelper.chromatic[i][:2] == note or ToneHelper.chromatic[i][-2:] == note:
                    return ToneHelper.chromatic[(i + 1) % 12][:2]
        else:
            print("Error: shift " + sf + " not recognized")
            exit(1)

        return note

    @staticmethod
    def cycle_of_mths(base: str, n: int, spacing: str='iv') -> [str]:
        """
        Calculates a cycle of mths progression for a given base up to n iterations.
        Leave spacing default for cycle of fifths.
        :param base: the base key
        :param n: number of iterations
        :param spacing: the spacing between key changes
        :return: A list of key changes
        """
        cycle = ['0' for _ in range(n)]
        cycle[0] = base

        for _ in range(n - 1):
            cycle[_ + 1] = ToneHelper.shift_to_scale(spacing, cycle[_])  # down a 4th = up a 5th and vice versa

        return cycle
