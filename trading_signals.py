from enum import IntEnum
import pandas as pd

ENTRY_THRESHOLD = 2
EXIT_THRESHOLD = 0

class Position(IntEnum):
    FLAT = 0
    LONG = 1
    SHORT = -1

class Signal(IntEnum):
    NONE = 0
    ENTER_LONG = 1
    ENTER_SHORT = -1
    EXIT_LONG = 2
    EXIT_SHORT = -2
    EXIT_LONG_AND_ENTER_SHORT = 3
    EXIT_SHORT_AND_ENTER_LONG = -3

def classify_position(position, previous_z_score, current_z_score):
    new_position = position
    if position == Position.FLAT:
        # Enter long position
        if current_z_score <= -ENTRY_THRESHOLD < previous_z_score:
            new_position = Position.LONG
        # Enter short position
        elif current_z_score >= ENTRY_THRESHOLD > previous_z_score:
            new_position = Position.SHORT
    elif position == Position.LONG:
        # Reversal to short position
        if current_z_score >= ENTRY_THRESHOLD > previous_z_score:
            new_position = Position.SHORT
        # Exit long position
        elif current_z_score >= -EXIT_THRESHOLD > previous_z_score:
            new_position = Position.FLAT
    elif position == Position.SHORT:
        # Reversal to long position
        if current_z_score <= -ENTRY_THRESHOLD < previous_z_score:
            new_position = Position.LONG
        # Exit short position
        elif current_z_score <= EXIT_THRESHOLD < previous_z_score:
            new_position = Position.FLAT

    return Position(new_position)

def get_positions(z_score):
    z_score_entries = z_score.dropna()
    positions = pd.Series(data=Position(0).name, index=z_score_entries.index, dtype=object)
    position = Position.FLAT

    for i in range(1, len(z_score_entries)):
        #TODO: what about large jumps in z-score? e.g. <-ENTRY_THRESHOLD to >ENTRY_THRESHOLD
        #i.e. two different positions are arguable true at the same time...
        previous_z_score = z_score_entries.iloc[i-1]
        current_z_score = z_score_entries.iloc[i]
        position = classify_position(position, previous_z_score, current_z_score)
        positions.iloc[i] = position.name

    return positions

def classify_signal(previous_position, current_position):

    if previous_position == current_position:
        return Signal.NONE
    elif previous_position == Position.FLAT:
        if current_position == Position.LONG:
            return Signal.ENTER_LONG
        else:
            return Signal.ENTER_SHORT
    elif previous_position == Position.LONG:
        if current_position == Position.FLAT:
            return Signal.EXIT_LONG
        else:
            return Signal.EXIT_LONG_AND_ENTER_SHORT
    else:
        if current_position == Position.FLAT:
            return Signal.EXIT_SHORT
        else:
            return Signal.EXIT_SHORT_AND_ENTER_LONG

def get_signals(positions):
    position_entries = positions.dropna()
    signals = pd.Series(data=Signal(0).name, index=position_entries.index)

    for i in range(1, len(position_entries)):
        previous_position = Position[position_entries.iloc[i-1]]
        current_position = Position[position_entries.iloc[i]]
        signal = classify_signal(previous_position, current_position)
        signals.iloc[i] = signal.name

    return signals