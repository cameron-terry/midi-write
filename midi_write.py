##-------------------------------------------------------------------------------------------------------------------##
# TODO: abstract musical ideas even further
#       e.g. add support for cycle of fifths, hammer-ons / pull-offs, and more
# TODO: add variability to note length
# TODO: add file for defining new chords (e.g. x2222x = B9sus4)
#       if it doesn't find chord in definition look in file
#       or denote with character %
#TODO: add arpeggios! and markup file
#       arpeggios shouldn't be too hard. it's a matter of spacing out the notes in the chord (increasing delta-time)
#       sample markup file:
#       e.g.
#           <begin [title]>
#               <time-sig=[time_sig]> (not a necessary tag, default is 4/4)
#               <tempo=[tempo]> (not a necessary tag, default is 120
#               <key_sig=[key_sig]> (not a necessary tag, default is Cmaj)
#               <begin commands>
#                   commands = [<command1> <command2> ... ]
#               <end commands>
#           <end [title]>
#
#       and the output, of course, is a midi file.
##-------------------------------------------------------------------------------------------------------------------##
# MidiWrite by Cameron Terry
# May 28, 2018
# time: 2 days (and counting!)
#
# MidiWrite makes turning a chord progression into a midi file a super simple process while lessening the time
# required needed to create a midi file based on a progression.
##-------------------------------------------------------------------------------------------------------------------##

import array


class MidiWrite:
    # constant bytes
    mthd                = b'\x4d\x54\x68\x64'
    header_chunk_length = b'\x00\x00\x00\x06'

    mtrk                = b'\x4d\x54\x72\x6b'
    track_chunk_length  = b'\x00\x00\x00\x14'

    eof                 = b'\x00\xff\x2f\x00'

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
        "E": ["E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb"]
    }


    @staticmethod
    def get_key(k: str):

        '''
        Returns the number of sharps / flats for a given key
        :param k: the key signature
        :return: the number of sharps / flats and if the key is major / minor
        '''

        major_keys = {
            'Cb': 7, 'Gb': 6, 'Db': 5, 'Ab': 4, 'Eb': 3, 'Bb': 2, 'F#': -6, 'C#': -7, 'F': 1, 
            'C': 0, 'G': -1, 'D': -2, 'A': -3, 'E': -4, 'B': -5
        }

        minor_keys = {
            'Ab': 7, 'Eb': 6, 'Bb': 5, 'F#': -3, 'C#': -4, 'G#': -5, 'D#': -6, 'A#': -7, 'F': 4,
            'C': 3, 'G': 2, 'D': 1, 'A': 0, 'E': -1,'B': -2
        }

        if "maj" in k:
            for element in major_keys:
                if element == k[:2]:
                    return major_keys[element], 1
            for element in major_keys:
                if element == k[0]:
                    return major_keys[element], 1
        elif "m" in k:
            for element in minor_keys:
                if element == k[:2]:
                    return minor_keys[element], 0
            for element in minor_keys:
                if element == k[0]:
                    return minor_keys[element], 0
        else:
            raise ValueError

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
        byte_arr = [0 for _ in range(4)]
        count = 0

        while True:
            if n < 128:
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
                if byte_arr[i] + byte_arr[i + 1] < 256:
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
            result |= (val & 0x7F)
            if not (val & 0x80 == 0x80):
                return result

    @staticmethod
    def write_preqs(file: str):
        '''
        write the pre-requisite headers to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        MidiWrite.write_header_chunk(file)
        MidiWrite.write_track_chunk(file)

    @staticmethod
    def write_header_chunk(file: str):
        '''
        write the header chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        '''
        fmat         = b'\x00\x01'
        track        = b'\x00\x02'
        quart_length = b'\x00\x60'

        with open(file, "wb") as f:
            f.write(MidiWrite.mthd)
            f.write(MidiWrite.header_chunk_length)
            f.write(fmat)
            f.write(track)
            f.write(quart_length)

    @staticmethod
    def write_track_chunk(file: str):
        '''
        write the track chunk to the midi file.
        :param file: the midi file to write to
        :return: none
        '''

        with open(file, "ab") as f:
            f.write(MidiWrite.mtrk)
            f.write(MidiWrite.track_chunk_length)

        MidiWrite.write_time_sig(file)

    @staticmethod
    def write_time_sig(file: str):
        '''
        write the time signature and other relevant meta tags to the midi file
        :param file: the midi file to write to
        :return: none
        '''
        time_sig = b'\x00\xff\x58\x04\x04\x02\x18\x08'
        tempo    = b'\x00\xff\x51\x03\x07\xa1\x20'
        eot      = b'\x83\x00\xff\x2f\x00'

        with open(file, "ab") as f:
            f.write(time_sig)
            f.write(tempo)
            f.write(eot)

    @staticmethod
    def write_track(file: str, commands: [bytes], title='Main', key='Cmaj', debug=False):
        '''
        write the track data to the midi file
        :param file: the midi file to write to
        :param commands: the notes to write to the midi file
        :param title: the title of the track
        :param key: the key signature of the track
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


        flats, major_minor = MidiWrite.get_key(key)

        key_sig += bytes([flats])
        key_sig += bytes([major_minor])

        count = 7 + len(chunk_title) + len(key_sig)
        notes_list = []

        for chord in commands:
            notes = MidiWrite.find_notes(chord)
            for note in notes:
                count += len(note)
            notes_list.append(notes)

        b = MidiWrite.write_var_len(count + 1)
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
                if debug:
                    print("Writing %s to %s... " % (commands[i], file), end="", flush=True)
                for note in notes_list[i]:
                    f.write(note)
                if debug:
                    print("Done.")

            f.write(MidiWrite.eof)

    @staticmethod
    def find_notes(chord, time: bytes= b'\x40') -> [bytes]:
        '''
        find the notes needed to play the chord
        :param chord: the chord to find the notes of
        :param time: time each note is held down
        :return: the midi representation of the chord / notes
        '''
        start_simul = b'\x00\x90'
        note_on     = time
        note_off    = b'\x00'
        delay       = b'\x81\x40'

        notes = MidiWrite.chord_shape(chord)
        note_arr = []

        if notes:
            for i in range(len(notes)):
                # means 0x90 - turn on - 0x?? - 60 + n (C#, 60 is C) -- 0x20 -- for a quarter?
                note_arr.append(start_simul + bytes(notes[i:i+1]) + note_on)

            note_arr.append(delay + bytes(notes[len(notes)-1:len(notes)]) + note_off)

            for j in range(len(notes) - 1, 0, -1):
                # delta times of simultaneous events are 0
                note_arr.append(b'\x00' + bytes(notes[j-1:j]) + note_off)

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
        if isinstance(chord, str):
            for element in MidiWrite.note_map:
                if element in chord:
                    base = MidiWrite.note_map[element]
                    if "maj7" in chord:
                        if chord[-1] == "*":
                            if chord[-2] == "*":
                                return [base, base + 11, base + 16, base + 19]
                            else:
                                return [base, base + 7, base + 11, base + 16, base + 19]

                    elif "m7" in chord:
                        if chord[-1] == "*":
                            if chord[-2] == "*":
                                return [base, base + 10, base + 15, base + 19]
                            else:
                                return [base, base + 7, base + 10, base + 15, base + 19]

                    elif "7" in chord:
                        if chord[-1] == "*":
                            if chord[-2] == "*":
                                return [base, base + 10, base + 15, base + 19]
                            else:
                                return [base, base + 7, base + 10, base + 16, base + 19]
                        elif chord[-1] == "%":
                            return [base, base + 10, base + 15, base + 19]

                    elif "13" in chord:
                        if chord[-1] == "*":
                            if chord[-2] == "*":
                                return [base, base + 10, base + 16, base + 21]
                            else:
                                return [base, base + 4, base + 10, base + 14, base + 21]

        notes = []
        if chord[0] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["E"][int(chord[0])])
        if chord[1] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["A"][int(chord[1])])
        if chord[2] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["D"][int(chord[2])])
        if chord[3] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["G"][int(chord[3])])
        if chord[4] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["B"][int(chord[4])])
        if chord[5] != 'x':
            notes.append(MidiWrite.guitar_map_standard_tuning["E"][int(chord[5])])

        for i in range(len(notes)):
            if len(notes[i]) > 2:
                notes[i] = notes[i][:2]
            for key, value in MidiWrite.note_map.items():
                if key == notes[i]:
                    notes[i] = MidiWrite.note_map[key]
                    break

        return notes
