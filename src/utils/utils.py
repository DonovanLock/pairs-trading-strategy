import numpy as np
import pandas as pd

def get_upper_triangle_of_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    return matrix.where(np.triu(matrix, k=1).astype(bool))