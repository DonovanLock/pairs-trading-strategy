import numpy as np

def get_upper_triangle_of_matrix(matrix):
    return matrix.where(np.triu(matrix, k=1).astype(bool))

def get_columns_from_pair_data(pair_data):
    return pair_data.iloc[:, 0], pair_data.iloc[:, 1]