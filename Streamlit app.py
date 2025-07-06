import streamlit as st

API_KEY = st.secrets["api"]["qloo_key"]

try:
    st.write("🔑 Your API Key is:", st.secrets["api"]["qloo_key"])
except Exception as e:
    st.error(f"🚨 Could not access API key: {e}")

# App Title
st.set_page_config(page_title="AI StyleTwin", layout="wide")
st.title("🧠 AI StyleTwin")
st.caption("Discover your aesthetic twin in media and fashion.")

# Create the main tabs
tabs = st.tabs(["🎬 Media Style Match", "👗 Fashion & Brands", "🧍‍♂️ AI Fitting Room"])

# === Tab 1: Media Style Match ===
with tabs[0]:
    st.header("🎥 Movie & Song Recommendations")
    st.markdown("Input your favorite movie or song and we'll find your aesthetic twins!")

    # Placeholder input
    movie_input = st.text_input("🎬 Enter a movie title:", "")
    song_input = st.text_input("🎵 Enter a song title (optional):", "")
    
    # Placeholder output
    if movie_input or song_input:
        st.info("🎯 This is where your recommendations will show up.")

# === Tab 2: Fashion & Brands ===
with tabs[1]:
    st.header("👚 Clothing & Brand Recommendations")
    st.markdown("Find clothing brands or outfits that match your media style.")

    # Placeholder input and logic
    st.selectbox("Pick a theme from your recommended movies or songs", ["Casual", "Vintage", "Grunge", "Avant-Garde"])
    st.info("🛍️ Clothing suggestions will appear here.")

# === Tab 3: AI Fitting Room ===
with tabs[2]:
    st.header("🧍 Virtual Fitting Simulation")
    st.markdown("Try on clothing styles using your image and AI simulation.")

    # Placeholder upload
    uploaded_file = st.file_uploader("📸 Upload a full-body photo (optional)", type=["jpg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Your uploaded photo", use_column_width=True)
    
    st.info("🪞 AI-generated virtual fitting results will appear here.")

# Footer
st.markdown("---")
st.markdown("Made with 💡 for the hackathon.")
