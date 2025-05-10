
import streamlit as st

def render_footer():
    st.markdown(
        '''
        <div style='text-align: center; margin-top: 3em;'>
            <img src='scoreisup_logo.png' style='height: 50px; opacity: 0.8;' />
            <p style='font-size: 12px; color: gray;'>© 2025 ScoreIsUp</p>
        </div>
        ''',
        unsafe_allow_html=True
    )
