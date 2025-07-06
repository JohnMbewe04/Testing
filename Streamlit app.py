import streamlit as st
import requests

API_KEY = st.secrets["api"]["qloo_key"]

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

    # Input fields
    movie_input = st.text_input("🎬 Enter a movie title:", "")
    song_input = st.text_input("🎵 Enter a song title (optional):", "")
    
    # Recommendation logic
    if movie_input:
        if st.button("Get Movie Recommendations"):
            url = "https://staging.api.qloo.com/v2/recommendations"
            headers = {
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "type": "urn:entity:movie",
                "inputs": [
                    {
                        "type": "urn:entity:movie",
                        "name": movie_input
                    }
                ]
            }

            with st.spinner("Fetching recommendations..."):
                response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                results = response.json()
                recs = results.get("recommendations", [])

                if recs:
                    st.success("🎯 Here are some recommended movies based on your input:")
                    for r in recs:
                        st.markdown(f"- 🎬 **{r.get('name')}**")
                else:
                    st.warning("No movie recommendations found.")
            else:
                st.error(f"API Error: {response.status_code}")

    elif song_input:
        st.info("🎧 Song recommendations coming soon!")

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
