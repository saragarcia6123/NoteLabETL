import streamlit as st
import config

def main():
    st.set_page_config(layout="wide")
    cf = config.load()
    SERVER_URL = cf['SERVER_URL']
    swagger_ui_html = f"""
    <iframe src="{SERVER_URL}" width="100%" height="600px" frameborder="0"></iframe>
    """

    st.title('API Documentation')
    st.components.v1.html(swagger_ui_html, height=600)

if __name__ == "__main__":
    main()
