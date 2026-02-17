import streamlit as st
import pandas as pd
import numpy as np
import re

st.title("TOPSIS Web Service")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
weights_input = st.text_input("Enter Weights (comma separated)", "1,1,1,1,1")
impacts_input = st.text_input("Enter Impacts (+ or - comma separated)", "+,+,+,+,+")
email_input = st.text_input("Enter Email ID")

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def topsis(df, weights, impacts):
    matrix = df.iloc[:, 1:].values.astype(float)

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

    df['Topsis Score'] = score
    df['Rank'] = score.argsort()[::-1].argsort() + 1

    return df

if st.button("Submit"):
    if uploaded_file is None:
        st.error("Please upload a file.")
    elif not validate_email(email_input):
        st.error("Invalid email format.")
    else:
        df = pd.read_csv(uploaded_file)

        if df.shape[1] < 3:
            st.error("Input file must contain at least 3 columns.")
        else:
            weights = weights_input.split(',')
            impacts = impacts_input.split(',')

            if len(weights) != len(impacts):
                st.error("Weights and impacts must be same length.")
            elif len(weights) != df.shape[1] - 1:
                st.error("Number of weights must match number of criteria.")
            elif any(i not in ['+', '-'] for i in impacts):
                st.error("Impacts must be + or -.")
            else:
                weights = np.array(weights, dtype=float)
                result = topsis(df, weights, impacts)

                result.to_csv("output.csv", index=False)

                st.success("TOPSIS calculation completed.")
                st.dataframe(result)
