##-------------------------------------------------------------------------------------------------------------------##
# note: currenty musescore does not open these kinds of .midi files, unexpected eof
# TODO: add support for single notes, scales and other musical ideas
#       e.g. add support for cycle of fifths, hammer-ons / pull-offs, and more
# TODO: add support for specifying chords by key
#       e.g. key=C, I -> V -> iv -> IV = C -> G -> Fm -> A
##-------------------------------------------------------------------------------------------------------------------##
# MidiWrite by Cameron Terry
# May 28, 2018
#
# MidiWrite makes turning a chord progression into a MIDI file a super simple process while lessening the time
# required needed to create a MIDI file based on a progression.
##-------------------------------------------------------------------------------------------------------------------##

import array
import struct
import math

# class for helper functions
class Misc:
    '''
    Check input to see if it is a number
    '''
    @staticmethod
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

# class for dealing with tones and notes
class ToneHelper:
    # used to map notes to sound frequencies
    note_map = {
        "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63, "E": 64, "F": 65, "F#": 66,
        "Gb": 66, "G": 67, "G#": 68, "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
    }
    # used for translating fret-based input
    guitar_map_standard_tuning = {
        "E": ["E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb"],
        "A": ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab"],
        "D": ["D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db"],
        "G": ["G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb"],
        "B": ["B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb"],
    }

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

    @staticmethod
    def get_key(k: str):
        '''
        Returns the number of sharps / flats for a given key
        :param k: the key signature
        :return: the number of sharps / flats and if the key is major / minor
        '''

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


class MidiWrite:
    note_map = ToneHelper.note_map

    # user defined file that contains additional chord mappings
    custom_file = None

    debug = False  # set in track_chunk

    # constant bytes
    mthd                = b'\x4d\x54\x68\x64'
    header_chunk_length = b'\x00\x00\x00\x06'

    mtrk                = b'\x4d\x54\x72\x6b'
    track_chunk_length  = b'\x00\x00\x00\x14'

    eof                 = b'\x00\xff\x2f\x00'

    @staticmethod
    def set_custom_file(file: str):
        '''
        Set a pointer to the custom file
        :param file: the custom file
        :return: none
        '''
        if file is not None:
            MidiWrite.custom_file = file

    @staticmethod
    def octave_shift_down(n: int):
        '''
        Shifts all notes down n octaves
        :param n: number of octaves to shift down
        :return: none
        '''
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] -= n * 12

    @staticmethod
    def octave_shift_up(n: int):
        '''
        Shifts all notes up n octaves
        :param n: number of octaves to shift up
        :return: none
        '''
        if n > 0:
            for key in MidiWrite.note_map:
                MidiWrite.note_map[key] += n * 12

    # based on pseudo-code from http://midi.teragonaudio.com/tech/midifile/vari.htm
    @staticmethod
    def write_var_len(n: int) -> [int]:
        '''
        Transforms an integer into a variable-length quantity
        :param n: the integer to convert
        :return: variable-length quantity array of the integer
        '''

        # constants
        EIGHT_BIT_MAX = 256
        SEVEN_BIT_MAX = 128

        byte_arr = [0 for _ in range(4)]
        count = 0

        while True:
            if n < SEVEN_BIT_MAX:
                byte_arr[count] = n & 0x7f
                count += 1
                break
            else:
                result = n
                byte_arr[count] = result & 0x7f | 0x80
                count += 1
                n >>= 7

        byte_arr = byte_arr[:count]
        byte_arr.reverse()

        r = True  # used for additional formatting
        for i in range(len(byte_arr)):
            if i < len(byte_arr) - 1:
                if byte_arr[i] + byte_arr[i + 1] < EIGHT_BIT_MAX:
                    byte_arr[i] = byte_arr[i] + byte_arr[i + 1]
                    byte_arr[i + 1] = 0
                    r = False

        if r:
            byte_arr.reverse()

        byte_arr = array.array('B', byte_arr).tostring()
        return byte_arr

    @staticmethod
    def read_var_len(n: [int]) -> int:
        '''
        converts a variable-length quantity to an integer.
        :param n: the variable-length quantity to convert
        :return: integer representation of the variable-length quantity
        '''
        result = 0
        for val in n:
            result <<= 7
            result |= (val & 0x7f)
            if not (val & 0x80 == 0x80):
                return result

    @staticmethod
    def write_preqs(file: str, time="4/4", tempo=120):
        '''
        write the pre-requisite headers to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        # check prefix
        if file[-5:] != ".midi":
            print("File not could be created.")
            exit(1)

        MidiWrite.write_header_chunk(file)
        MidiWrite.write_track_chunk(file, time, tempo)

    @staticmethod
    def write_header_chunk(file: str):
        '''
        write the header chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        fmat         = b'\x00\x01'  # multiple-track format
        track        = b'\x00\x02'  # 1 track
        quart_length = b'\x00\x60'  # quarter tick length

        with open(file, "wb") as f:
            f.write(MidiWrite.mthd)
            f.write(MidiWrite.header_chunk_length)
            f.write(fmat)
            f.write(track)
            f.write(quart_length)

    @staticmethod
    def write_track_chunk(file: str, time, tempo):
        '''
        write the track chunk to the midi file.
        :param file: the midi file to write to
        :param time: the time signature as a string
        :param tempo: the tempo of the progression as an integer
        :return: none
        '''

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(MidiWrite.track_chunk_length)

        MidiWrite.write_time_sig(file, time, tempo)

    @staticmethod
    def write_time_sig(file: str, time: str, tempo: int):
        '''
        write the time signature and other relevant meta tags to the midi file
        :param file: the midi file to write to
        :param time: the time signature as a string
        :param tempo: the tempo of the progression as an integer
        :return: none
        '''
        tempo_bytes = b'\x00\xff\x51\x03'
        eot         = b'\x83\x00\xff\x2f\x00'

        time_sig = b'\x00\xff\x58\x04'
        time_sig_end_bytes = b'\x24\x08'

        # to convert bpm to tempo, use 60_000_000 / tempo
        tempo_hex = hex(int(60_000_000 / tempo))  # number of microseconds in a minute

        if len(tempo_hex) % 2 == 1:
            byte_1 = int(tempo_hex[:2] + '0' + tempo_hex[2], 0)
            byte_2 = int(tempo_hex[:2] + tempo_hex[3:5], 0)
            byte_3 = int(tempo_hex[:2] + tempo_hex[5:], 0)
            tempo_bytes += struct.pack("BBB", byte_1, byte_2, byte_3)

        ts_num = bytes([int(time.split("/")[0])])
        ts_denom = bytes([int(math.log(int(time.split("/")[1]), 2))])

        time_sig += ts_num + ts_denom + time_sig_end_bytes

        with open(file, "ab") as f:
            f.write(time_sig)
            f.write(tempo_bytes)
            f.write(eot)

    @staticmethod
    def write_track(file: str, commands: [bytes], title='Main', key='Cmaj', shift=0, debug=False, arpeggiate=False):
        if shift != 0:
            if shift < 0:
                MidiWrite.octave_shift_down(abs(shift))
            else:
                MidiWrite.octave_shift_up(shift)

        if debug:
            MidiWrite.debug = True
        '''
        write the track data to the midi file
        :param file: the midi file to write to
        :param commands: the notes to write to the midi file
        :param title: the title of the track
        :param key: the key signature of the track
        :param debug: show progress on creating midi file
        :return:
        '''
        chunk_length = b'\x00\x00'
        preset = b'\x00\xc1' + bytes([24])
        chunk_title = b'\x00\xff\x03'
        key_sig = b'\x00\xff\x59\x02'

        chunk_title_length = bytes([len(title)])
        chunk_title += chunk_title_length
        for letter in title:
            chunk_title += bytes([ord(letter)])

        flats, major_minor = ToneHelper.get_key(key)

        key_sig += bytes([flats if flats > 0 else 256 + flats])  # two's complement if negative
        key_sig += bytes([major_minor])

        # not sure why count is 1 less than it needs to be
        count = 1 + len(chunk_length) + len(MidiWrite.eof) + len(chunk_title) + len(key_sig)
        notes_list = []

        flip = False
        for chord in commands:
            if arpeggiate:
                notes = MidiWrite.find_notes(chord, flip=flip)
            else:
                notes = MidiWrite.find_notes(chord)
            for note in notes:
                count += len(note)
            notes_list.append(notes)
            if arpeggiate:
                flip = not flip

        b = MidiWrite.write_var_len(count)
        chunk_length += b

        # just a check to make sure number is formatted correctly
        if len(chunk_length) < 4:
            chunk_length = chunk_length[0:2] + b'\x00' + chunk_length[2:]

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(chunk_length)
            f.write(chunk_title)
            f.write(key_sig)
            f.write(preset)

            for i in range(len(notes_list)):
                if MidiWrite.debug:
                    print("Writing \"%s\" to %s... " % (commands[i], file), end="", flush=True)
                for note in notes_list[i]:
                    f.write(note)
                if MidiWrite.debug:
                    print("Done.")

            f.write(MidiWrite.eof)

    @staticmethod
    def find_notes(chord, flip=False) -> [bytes]:
        '''
        find the notes needed to play the chord
        :param chord: the chord to find the notes of
        :return: the midi representation of the chord / notes
        '''
        start_simul       = b'\x00\x90'
        note_on           = b'\x40'
        note_off          = b'\x00'
        delay             = b'\x81\x40'
        time_arp_delay    = b'\x30'  # 1/2 of b'\x60', the quarter note length

        notes, arpeggiate, arp_rev, note_type = MidiWrite.chord_shape(chord)

        if arp_rev:
            flip = not flip

        # TODO: test all delays
        if note_type == 'w':  # have to test
            delay = b'\x90\xf2'  # or b'\xc0'?
            time_arp_delay = b'\xc1'
        elif note_type == 'h':  # is equivalent to default?
            pass
        elif note_type == 'q':  # works
            delay = b'\x60'
            time_arp_delay = b'\x30'
        elif note_type == 'e':  # works
            delay = b'\x30'
            time_arp_delay = b'\x18'
        elif note_type == 's':
            delay = b'\x18'
            time_arp_delay = b'\x0c'
        elif note_type == 't':
            delay = b'\x0c'
            time_arp_delay = b'\x06'

        note_arr = []

        if notes:
            if not arpeggiate:
                for i in range(len(notes)):
                    # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x40
                    note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)

                note_arr.append(delay + bytes(notes[len(notes)-1:len(notes)]) + note_off)

                for j in range(len(notes) - 1, 0, -1):
                    # turn off all at same time
                    note_arr.append(b'\x00' + bytes(notes[j-1:j]) + note_off)
            else:
                num_notes = 4 if len(notes) >= 4 else len(notes)
                if not flip:
                    for i in range(num_notes):
                        # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x40
                        note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)
                        # means 0x90 - turn off - 0x?? - 60 + n (C#, 60 is C) -- 0x00 after time_arp_delay
                        note_arr.append(time_arp_delay + bytes(notes[i:i+1]) + note_off)
                else:
                    for i in range(num_notes, 0, -1):
                        note_arr.append(start_simul + bytes(notes[i-1:i]) + note_on)
                        note_arr.append(time_arp_delay + bytes(notes[i-1:i]) + note_off)

            return note_arr
        else:
            return [b'\x81\x40\x90\x4c\x20',
                    b'\x81\x40\x4c\x00']  # return single note

    @staticmethod
    def chord_shape(chord) -> [int]:
        '''
        determine the notes of the chord based on chord type / fret locations
        :param chord: the chord to find the notes of
        :return: the chord as a set of integer notes
        '''
        arpeggiate = False
        arp_rev = False
        found_flags = False
        search_chord = chord
        note_type = 'd'
        
        if isinstance(chord, str):
            # check for arpeggio flags
            if "-a" in chord:
                found_flags = True
                arpeggiate = True
                if "-ar" in chord:
                    arp_rev = True
                    search_chord = search_chord.replace('-ar', '')
                else:
                    search_chord = search_chord.replace('-a', '')

            time_flags = ['-w', '-h', '-q', '-e', '-s', '-t']

            # check to make sure only one time flag is selected
            for _ in range(2):
                for flag in time_flags:
                    if flag in search_chord and not found_flags:
                        found_flags = True
                        note_type = flag[1:]
                        search_chord = search_chord.replace(flag, '')
                        break
                    else:
                        print("Error: time flag already selected: -" + note_type)
                        exit(1)

            # look for note and chord type in dictionaries
            for element in MidiWrite.note_map:
                if element in search_chord:
                    base = MidiWrite.note_map[element]
                    if '%' not in search_chord:
                        for c_shape in ToneHelper.chord_dict:
                            if c_shape in search_chord:
                                if "***" in search_chord:
                                    return [24 + base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type
                                elif "**" in search_chord:
                                    return [12 + base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type
                                elif "*" in search_chord:
                                    return [base + i for i in ToneHelper.chord_dict[c_shape]], arpeggiate, arp_rev, note_type

                    else:
                        # look for chord in separate custom file
                        # custom file defines chords like so: <chord> : <[notes]> or <chord>:<fret notation>
                        # TODO: currently can only define one type of custom chord, edit to allow multiple
                        # e.g. F7%, F7%%, etc
                        custom_dict = {}
                        if MidiWrite.custom_file is not None:
                            with open(MidiWrite.custom_file, 'r') as f:
                                for line in f:
                                    definition = line.split(":")

                                    if 'x' in definition[1][0]:  # fret-notation
                                        search_chord = definition[1]
                                        break

                                    definition_edit = [int(j) for j in definition[1].split(",")]
                                    custom_dict[definition[0]] = definition_edit
                            for custom_c_shape in custom_dict:
                                if custom_c_shape in search_chord:
                                    return [base + int(i) for i in custom_dict[custom_c_shape]], arpeggiate, arp_rev, note_type

        # assume chord is in fret-notation
        if 'x' not in search_chord and not any(char.isdigit() for char in search_chord):
            print("Chord " + search_chord + " not found. Either chord has not been added or chord is incorrectly typed.")
            return [0], False, False, note_type

        notes = []
        octaves = [0, 0, 0, 0, 0, 0]
        if Misc.is_number(search_chord[0]):
            shift = int(search_chord[0]) // 12
            octaves[0] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["E"][int(search_chord[0]) % 12])  # octaves repeat
        else:
            if MidiWrite.debug and search_chord[0] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[1]):
            shift = int(search_chord[1]) // 12
            octaves[1] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["A"][int(search_chord[1]) % 12])
        else:
            if MidiWrite.debug and search_chord[1] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[2]):
            shift = int(search_chord[2]) // 12
            octaves[2] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["D"][int(search_chord[2]) % 12])
        else:
            if MidiWrite.debug and search_chord[2] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[3]):
            shift = int(search_chord[3]) // 12
            octaves[3] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["G"][int(search_chord[3]) % 12])
        else:
            if MidiWrite.debug and search_chord[3] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[4]):
            shift = int(search_chord[4]) // 12
            octaves[4] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["B"][int(search_chord[4]) % 12])
        else:
            if MidiWrite.debug and search_chord[4] != 'x':
                print("Invalid character found, is ignored.")
        if Misc.is_number(search_chord[5]):
            shift = int(search_chord[5]) // 12
            octaves[5] = shift
            notes.append(ToneHelper.guitar_map_standard_tuning["E"][int(search_chord[5]) % 12])
        else:
            if MidiWrite.debug and search_chord[5] != 'x':
                print("Invalid character found, is ignored.")

        for i in range(len(notes)):
            if len(notes[i]) > 2:
                notes[i] = notes[i][:2]
            for key, value in MidiWrite.note_map.items():
                if key == notes[i]:
                    notes[i] = MidiWrite.note_map[key] + (12 * (1 + octaves[i]))
                    break

        return notes, arpeggiate, arp_rev, note_type
