import pandas as pd

ENTRY_THRESHOLD = 2
EXIT_THRESHOLD = 0

def get_positions(z_score):
    positions = pd.Series(data=0, index=z_score.index)
    
    # 0 = flat, 1 = long position in spread, -1 = short position in spread
    position = 0

    for i in range(1, len(z_score)):
        #TODO: what about large jumps in z-score? e.g. <-ENTRY_THRESHOLD to >ENTRY_THRESHOLD
        #Enter long position
        if z_score.iloc[i] <= -ENTRY_THRESHOLD and z_score.iloc[i-1] > -ENTRY_THRESHOLD and position == 0:
            position = 1
        #Exit long position
        elif z_score.iloc[i] >= -EXIT_THRESHOLD and z_score.iloc[i-1] < -EXIT_THRESHOLD and position == 1:
            position = 0
        #Enter short position
        elif z_score.iloc[i] >= ENTRY_THRESHOLD and z_score.iloc[i-1] < ENTRY_THRESHOLD and position == 0:
            position = -1
        #Exit short position
        elif z_score.iloc[i] <= EXIT_THRESHOLD and z_score.iloc[i-1] > EXIT_THRESHOLD and position == -1:
            position = 0
        
        positions.iloc[i] = position
    
    return positions

def get_signals(positions):
    # 0 = no change, 1 = buy, -1 = sell
    return positions.diff()