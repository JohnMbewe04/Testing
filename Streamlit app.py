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
    st.markdown("Input your favorite **movie title** or select a **genre** to get aesthetic recommendations.")

    # Inputs
    movie_input = st.text_input("🎬 Enter a movie title:", "")
    genre_options = [
        "comedy", "horror", "romance", "action", "animation", "crime", "sci-fi", "drama"
    ]
    selected_genre = st.selectbox("Or select a genre:", [""] + genre_options)

    if st.button("Get Recommendations"):
        # Setup common headers
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }

        if movie_input:
            # Use /v2/recommendations endpoint (POST)
            url = "https://hackathon.api.qloo.com/v2/recommendations"
            data = {
                "type": "urn:entity:movie",
                "inputs": [
                    {
                        "type": "urn:entity:movie",
                        "name": movie_input.strip()
                    }
                ]
            }
            with st.spinner("🎬 Fetching recommendations based on movie..."):
                response = requests.post(url, headers=headers, json=data)

        elif selected_genre:
            # Use /v2/insights endpoint (GET)
            url = "https://hackathon.api.qloo.com/v2/insights/"
            headers = {"x-api-key": API_KEY}
            params = {
                "filter.type": "urn:entity:movie",
                "filter.tags": f"urn:tag:genre:media:{selected_genre}"
            }
            with st.spinner("🎞️ Fetching genre-based recommendations..."):
                response = requests.get(url, headers=headers, params=params)

        else:
            st.warning("Please enter a movie title or select a genre.")
            response = None

        # Handle API response
        if response:
            if response.status_code == 200:
                data = response.json()
                items = data.get("recommendations") or data.get("insights") or []
                if items:
                    st.success("Here are your recommendations:")
                    for item in items:
                        st.markdown(f"- **🎬 {item.get('name', 'Unknown')}**")
                else:
                    st.warning("No recommendations found.")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

# === Tab 2: Fashion & Brands ===
with tabs[1]:
    st.header("👚 Clothing & Brand Recommendations")
    st.markdown("Find clothing brands or outfits that match your media style.")

    st.selectbox("Pick a theme from your recommended movies or songs", ["Casual", "Vintage", "Grunge", "Avant-Garde"])
    st.info("🛍️ Clothing suggestions will appear here.")

# === Tab 3: AI Fitting Room ===
with tabs[2]:
    st.header("🧍 Virtual Fitting Simulation")
    st.markdown("Try on clothing styles using your image and AI simulation.")

    uploaded_file = st.file_uploader("📸 Upload a full-body photo (optional)", type=["jpg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Your uploaded photo", use_column_width=True)
    
    st.info("🪞 AI-generated virtual fitting results will appear here.")

# Footer
st.markdown("---")
st.markdown("Made with 💡 for the hackathon.")
