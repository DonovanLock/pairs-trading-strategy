import numpy as np

def get_upper_triangle_of_matrix(matrix):
    return matrix.where(np.triu(matrix, k=1).astype(bool))