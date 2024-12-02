import streamlit as st
def page_dashboard():
    st.title('Dashboard')

    repo_url = 'https://github.com/saragarcia6123/NoteLab'
    st.link_button('Link to GitHub Repository', repo_url)

page_dashboard()