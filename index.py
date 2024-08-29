import numpy as np


def lambda_handler(event, context):

    # Create a 3x3 matrix of random numbers
    matrix = np.random.rand(3, 3)

    # Return the matrix as a string

    return {"statusCode": 200, "body": str(matrix)}
