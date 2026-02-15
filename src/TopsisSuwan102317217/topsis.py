import sys
import pandas as pd
import numpy as np



def main():
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters.")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    output_file = sys.argv[4]

    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)

    if data.shape[1] < 3:
        print("Error: Input file must contain three or more columns.")
        sys.exit(1)

    weights = weights.split(',')
    impacts = impacts.split(',')

    if len(weights) != len(impacts):
        print("Error: Weights and impacts must be same length.")
        sys.exit(1)

    if len(weights) != data.shape[1] - 1:
        print("Error: Number of weights, impacts and columns must be same.")
        sys.exit(1)

    for i in impacts:
        if i not in ['+', '-']:
            print("Error: Impacts must be '+' or '-'.")
            sys.exit(1)

    for col in data.columns[1:]:
        if not pd.api.types.is_numeric_dtype(data[col]):
            print("Error: All columns except first must be numeric.")
            sys.exit(1)

    weights = np.array(weights, dtype=float)
    matrix = data.iloc[:, 1:].values

    norm = np.sqrt((matrix**2).sum(axis=0))
    normalized = matrix / norm

    weighted = normalized * weights

    ideal_best = []
    ideal_worst = []

    for i in range(len(impacts)):
        if impacts[i] == '+':
            ideal_best.append(max(weighted[:, i]))
            ideal_worst.append(min(weighted[:, i]))
        else:
            ideal_best.append(min(weighted[:, i]))
            ideal_worst.append(max(weighted[:, i]))

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    s_plus = np.sqrt(((weighted - ideal_best)**2).sum(axis=1))
    s_minus = np.sqrt(((weighted - ideal_worst)**2).sum(axis=1))

    score = s_minus / (s_plus + s_minus)

    data['Topsis Score'] = score
    data['Rank'] = score.argsort()[::-1].argsort() + 1

    data.to_csv(output_file, index=False)

    print("Result saved successfully!")



if __name__ == "__main__":
    main()