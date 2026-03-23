"""
This file contains the Streamlit app with Auth0 Google Sign-In.
"""

import streamlit as st
from datetime import datetime
from db import get_or_create_user

if not st.user.is_logged_in:
    if st.button('Authenticate'):
        st.login('auth0')

else:
    if st.button("Log out"):
        st.logout()
    user_row = get_or_create_user(st.user.sub, 'auth0')
    
    st.session_state['user_name'] = st.user.name
    st.session_state['user_email'] = st.user.email
    st.session_state['user_picture'] = st.user.picture
    st.session_state['user_id'] = user_row['id']
    # st.switch_page('pages/app.py')
    st.header('Hello ' + st.user.name)
    st.image(st.user.picture)