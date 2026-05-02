import streamlit as st
from db import get_photos
from utils import format_date

def guest_dashboard():
    st.markdown("""
    <style>
    .main-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 20px; text-align: center;}
    </style>
    """, unsafe_allow_html=True)
    
    # Beautiful invitation card
    st.markdown("""
    <div class="main-card">
        <h1 style='font-size: 3rem;'>💍 You're Invited! 💍</h1>
        <h2 style='font-size: 2.5rem;'>Priya & Rohan</h2>
        <p style='font-size: 1.5rem;'>25th December 2024 | 7:00 PM</p>
        <p style='font-size: 1.2rem;'>Taj Hotel, Mumbai</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["✅ RSVP", "📸 Gallery", "💌 Blessings"])
    
    with tab1:
        st.header("✅ Confirm Your Attendance")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎉 Will Attend", use_container_width=True, type="primary"):
                st.balloons()
                st.success("Yay! See you at the wedding! 🎊")
        with col2:
            if st.button("😔 Cannot Attend", use_container_width=True):
                st.error("We're sorry you can't make it! 💔")
    
    with tab2:
        st.header("📸 Sneak Peek Gallery")
        photos = get_photos(1, is_sneak_peek_only=True)  # Demo wedding_id=1
        if photos:
            cols = st.columns(3)
            for i, photo in enumerate(photos):
                with cols[i % 3]:
                    st.image(photo['photo_url'], caption=photo['caption'], use_column_width=True)
        else:
            st.info("📷 Sneak peek photos coming soon!")
    
    with tab3:
        st.header("💌 Share Your Blessings")
        message = st.text_area("Write a message for the couple...", height=150)
        if st.button("💝 Send Blessings", use_container_width=True):
            st.success("Your blessings have been sent! 🌟")
            st.balloons()
