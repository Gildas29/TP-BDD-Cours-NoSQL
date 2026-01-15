# app_streamlit.py
import streamlit as st
from ui.pages_characters import render_page

st.set_page_config(page_title="Dragon Ball - CRUD", layout="wide")


def main():
    render_page()


if __name__ == "__main__":
    main()
