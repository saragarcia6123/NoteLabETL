import streamlit as st
import requests
import json
import pandas as pd
import config


def main():
    st.set_page_config(layout="wide")
    cf = config.load()
    SERVER_URL = cf['SERVER_URL']

    st.title("Home")

if __name__ == '__main__':
    main()
