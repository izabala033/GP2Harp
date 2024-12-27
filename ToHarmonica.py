from music21 import *

# Example usage
file_path = 'tmpngpfx2mm.mxl'  # Replace with the path to your MXL file

# Define a more accurate mapping from musical notes to harmonica holes.
note_to_harmonica_hole = {
    note.Note("C3").nameWithOctave: "1",
    note.Note("D3").nameWithOctave: "-1",
    note.Note("E3").nameWithOctave: "2",
    note.Note("G3").nameWithOctave: "-2",
    # note.Note("G3").nameWithOctave: "3", Commented because 3 and -3 are the same note
    note.Note("B3").nameWithOctave: "-3",
    note.Note("C4").nameWithOctave: "4",
    note.Note("D4").nameWithOctave: "-4",
    note.Note("E4").nameWithOctave: "5",
    note.Note("F4").nameWithOctave: "-5",
    note.Note("G4").nameWithOctave: "6",
    note.Note("A4").nameWithOctave: "-6",
    note.Note("C5").nameWithOctave: "7",
    note.Note("B5").nameWithOctave: "-7",
    note.Note("E5").nameWithOctave: "8",
    note.Note("D5").nameWithOctave: "-8",
    note.Note("G5").nameWithOctave: "9",
    note.Note("F5").nameWithOctave: "-9",
    note.Note("C6").nameWithOctave: "10",
    note.Note("A5").nameWithOctave: "-10",
}


def read_mxl(file_path):
    """
    Reads a MusicXML (MXL) file and returns a music21 score object.

    Args:
        file_path (str): The path to the MXL file.

    Returns:
        music21.stream.Score: The loaded score object or None if there was an error.
    """
    try:
        score = converter.parse(file_path)
        print("Successfully loaded the score!")
        print(f"Number of parts: {len(score.parts)}")
        print(f"Score metadata: {score.metadata}")
        return score
    except Exception as e:
        print(f"Error reading MXL file: {e}")
        return None


def add_harmonica_holes(score, note_to_harmonica_hole):
    """
    Adds harmonica hole annotations to notes in the score.

    Args:
        score (music21.stream.Score): The score to annotate.
        note_to_harmonica_hole (dict): Mapping of notes to harmonica holes.

    Returns:
        music21.stream.Score: The annotated score.
    """
    for part in score.parts:
        for element in part.flat.notes:
            if isinstance(element, note.Note):  # Check if it's a note (not a rest)
                # Lookup the corresponding harmonica hole for the note
                harmonica_hole = note_to_harmonica_hole.get(element.nameWithOctave, ":(")

                if harmonica_hole is not None:
                    # Add the harmonica hole annotation as a lyric
                    element.lyric = None
                    element.addLyric(str(harmonica_hole), applyRaw=True)  # Convert hole number to string
    return score


def count_missing_notes(score, note_to_harmonica_hole):
    """
    Counts the missing notes that cannot be played on the harmonica.

    Args:
        score (music21.stream.Score): The score to analyze.
        note_to_harmonica_hole (dict): Mapping of notes to harmonica holes.

    Returns:
        int: The number of missing notes.
    """
    missing_notes = 0
    for part in score.parts:
        for element in part.flat.notes:
            if isinstance(element, note.Note):  # Only process notes
                harmonica_hole = note_to_harmonica_hole.get(element.nameWithOctave)
                if harmonica_hole is None:  # Count notes that are not playable
                    missing_notes += 1
    return missing_notes


def find_best_transposition(score, note_to_harmonica_hole, min_semitones=-36, max_semitones=36):
    """
    Finds the best transposition to minimize missing notes on the harmonica.

    Args:
        score (music21.stream.Score): The score to analyze.
        note_to_harmonica_hole (dict): Mapping of notes to harmonica holes.
        min_semitones (int): Minimum semitones to transpose.
        max_semitones (int): Maximum semitones to transpose.

    Returns:
        tuple: The best transposition and the number of missing notes.
    """
    best_transposition = None
    min_missing_notes = float('inf')
    transposition_results = []

    for semitones in range(min_semitones, max_semitones + 1):
        # Transpose the score
        transposed_score = score.transpose(semitones)
        # Count missing notes
        missing_notes = count_missing_notes(transposed_score, note_to_harmonica_hole)
        transposition_results.append((semitones, missing_notes))

        # Update the best transposition
        if missing_notes < min_missing_notes:
            min_missing_notes = missing_notes
            best_transposition = semitones

    return best_transposition, min_missing_notes, transposition_results

score = read_mxl(file_path)
if score:
    best_transposition, min_missing_notes, transposition_results = find_best_transposition(score, note_to_harmonica_hole)

    print(f"Best transposition: {best_transposition} semitones")
    print(f"Minimum missing notes: {min_missing_notes}")

    # Print detailed results
    print("\nDetailed transposition results:")
    for semitones, missing_notes in transposition_results:
        print(f"Transposition {semitones:+d}: {missing_notes} missing notes")

    best_transposed_score = score.transpose(best_transposition)
    # Annotate the transposed score with harmonica hole mappings
    annotated_score = add_harmonica_holes(best_transposed_score, note_to_harmonica_hole)

    # Show the annotated score
    annotated_score.show()