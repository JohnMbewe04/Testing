import streamlit as st
import requests

QLOO_API_KEY = st.secrets["api"]["qloo_key"]
TMDB_API_KEY = st.secrets["api"]["tmdb_key"]

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
        headers = {
            "x-api-key": QLOO_API_KEY,
            "Content-Type": "application/json"
        }

        response = None
        fallback_used = False

        if movie_input:
            # Try Qloo first
            qloo_url = "https://hackathon.api.qloo.com/v2/recommendations"
            qloo_data = {
                "type": "urn:entity:movie",
                "inputs": [
                    {
                        "type": "urn:entity:movie",
                        "name": movie_input.strip()
                    }
                ]
            }
            with st.spinner("🎬 Fetching recommendations from Qloo..."):
                response = requests.post(qloo_url, headers=headers, json=qloo_data)

            # If Qloo fails or returns no results, use TMDb
            if response.status_code != 200 or not response.json().get("recommendations"):
                fallback_used = True
                st.warning("Qloo returned no results. Using TMDb as fallback.")

                # Step 1: Search TMDb
                tmdb_search_url = "https://api.themoviedb.org/3/search/movie"
                tmdb_params = {
                    "api_key": TMDB_API_KEY,
                    "query": movie_input,
                    "include_adult": False
                }
                tmdb_search = requests.get(tmdb_search_url, params=tmdb_params).json()
                tmdb_results = tmdb_search.get("results", [])

                if tmdb_results:
                    tmdb_id = tmdb_results[0]["id"]
                    tmdb_title = tmdb_results[0]["title"]

                    # Step 2: Get TMDb recommendations
                    tmdb_rec_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations"
                    tmdb_rec_params = {
                        "api_key": TMDB_API_KEY,
                        "language": "en-US",
                        "page": 1
                    }
                    tmdb_response = requests.get(tmdb_rec_url, params=tmdb_rec_params)
                    tmdb_recs = tmdb_response.json().get("results", [])

                    if tmdb_recs:
                        st.success(f"🎥 TMDb Recommendations based on '{tmdb_title}':")
                        for rec in tmdb_recs[:10]:
                            title = rec.get("title", "Unknown Title")
                            rating = rec.get("vote_average", "N/A")
                            votes = rec.get("vote_count", "N/A")
                            poster_path = rec.get("poster_path")
                            if poster_path:
                                st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                            st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                            st.markdown("---")
                    else:
                        st.warning("No fallback recommendations found on TMDb.")
                else:
                    st.error("TMDb could not find the movie.")
        elif selected_genre:
            # Use Qloo genre-based insights
            url = "https://hackathon.api.qloo.com/v2/insights/"
            headers = {"x-api-key": QLOO_API_KEY}
            params = {
                "filter.type": "urn:entity:movie",
                "filter.tags": f"urn:tag:genre:media:{selected_genre}"
            }
            with st.spinner("🎞️ Fetching genre-based recommendations from Qloo..."):
                response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200 or not response.json().get("insights"):
                fallback_used = True
                st.warning("Qloo returned no genre-based results. Using TMDb as fallback.")

                # TMDb genre fallback
                genre_map = {
                    "action": 28, "animation": 16, "comedy": 35, "crime": 80,
                    "drama": 18, "horror": 27, "romance": 10749, "sci-fi": 878
                }
                genre_id = genre_map.get(selected_genre.lower())
                if genre_id:
                    tmdb_genre_url = "https://api.themoviedb.org/3/discover/movie"
                    tmdb_params = {
                        "api_key": TMDB_API_KEY,
                        "with_genres": genre_id,
                        "sort_by": "popularity.desc",
                        "language": "en-US",
                        "page": 1
                    }
                    tmdb_response = requests.get(tmdb_genre_url, params=tmdb_params)
                    tmdb_recs = tmdb_response.json().get("results", [])

                    if tmdb_recs:
                        st.success(f"🎬 Popular {selected_genre.title()} Movies (via TMDb):")
                        for rec in tmdb_recs[:10]:
                            title = rec.get("title", "Unknown Title")
                            rating = rec.get("vote_average", "N/A")
                            votes = rec.get("vote_count", "N/A")
                            poster_path = rec.get("poster_path")
                            if poster_path:
                                st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                            st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                            st.markdown("---")
                    else:
                        st.warning("No fallback genre results found on TMDb.")
                else:
                    st.error("Genre not recognized.")
        else:
            st.warning("Please enter a movie title or select a genre.")

        # Handle Qloo response if not using fallback
        if response and not fallback_used:
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
