import os
import streamlit as st

def get_password():
    """Get password from environment variable or use default"""
    return os.environ.get('WISHLIST_PASSWORD', 'weihnachten2025')

def verify_password(password):
    """Verify if the provided password is correct"""
    if not password:
        return False
    return password == get_password()

def authenticate():
    """Streamlit authentication flow"""
    password = st.text_input("Passwort eingeben", type="password")
    if verify_password(password):
        st.success("Zugriff gewährt!")
        return True
    elif password:
        st.error("Falsches Passwort")
        return False
    return False