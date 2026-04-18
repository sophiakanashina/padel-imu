# 1. imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 2. helper functions (ADD IT HERE)
def load_uploaded_file(uploaded_file):
    if uploaded_file.name.endswith(".txt"):
        return pd.read_csv(uploaded_file, sep="\t")
    return pd.read_csv(uploaded_file)

# 3. streamlit UI starts here
st.title("Padel IMU Analysis")

uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt"])

if uploaded_file is not None:
    df = load_uploaded_file(uploaded_file)

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    st.subheader("Quick Demo Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    if "AccX(g)" in df.columns:
        st.subheader("Sample Plot")

        fig, ax = plt.subplots()
        ax.plot(df["AccX(g)"].head(200))
        ax.set_title("AccX Preview")
        st.pyplot(fig)