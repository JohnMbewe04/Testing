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
    st.markdown("Input your favorite movie (by name or genre) and we'll find your aesthetic twins!")

    # Input fields
    movie_input = st.text_input("🎬 Enter a movie title or genre (e.g., Inception or comedy):", "")
    song_input = st.text_input("🎵 Enter a song title (optional):", "")
    
    # Recommendation logic
    if movie_input:
        if st.button("Get Movie Recommendations"):
            url = "https://hackathon.api.qloo.com/v2/insights/"
            headers = {
                "x-api-key": API_KEY
            }

            # Detect if input is a genre or title (simple heuristic: lowercase and short = genre)
            if movie_input.strip().lower() in [
                "action", "comedy", "drama", "horror", "romance", "thriller", 
                "fantasy", "sci-fi", "animation", "crime", "documentary"
            ]:
                filter_type = "urn:entity:movie"
                filter_tag = f"urn:tag:genre:media:{movie_input.strip().lower()}"
                params = {
                    "filter.type": filter_type,
                    "filter.tags": filter_tag
                }
                query_type = "genre"
            else:
                # Treat as a title name match
                params = {
                    "filter.type": "urn:entity:movie",
                    "filter.name": movie_input.strip()
                }
                query_type = "title"

            with st.spinner("Fetching recommendations..."):
                response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                insights = data.get("insights", [])

                if insights:
                    st.success(f"🎯 Found {len(insights)} recommendations based on your {query_type}:")
                    for item in insights:
                        st.markdown(f"- 🎬 **{item.get('name', 'Unknown')}**")
                else:
                    st.warning("No results found. Try another movie or genre.")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

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
