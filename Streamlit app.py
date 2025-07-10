import streamlit as st
import requests

QLOO_API_KEY = st.secrets["api"]["qloo_key"]
TMDB_API_KEY = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]

genre_options = ["comedy", "horror", "romance", "action", "animation", "crime", "sci-fi", "drama"]

style_search_terms = {
    "retro": "retro outfit streetwear",
    "cozy": "cozy outfit knitwear",
    "soft girl": "soft girl aesthetic outfit",
    "grunge": "grunge outfit street style",
    "punk": "punk fashion editorial",
    "minimalist": "minimalist outfit neutral tones",
    "fairycore": "fairycore dress aesthetic",
    "techwear": "techwear outfit urban",
    "vintage": "vintage outfit 90s",
    "streetwear": "streetwear fashion urban",
    "gothic": "gothic outfit dark fashion",
    "cottagecore": "cottagecore dress aesthetic"
    # Add more as needed
}
        
def get_qloo_styles(input_type, value):
    headers = {
        "X-Api-Key": QLOO_API_KEY,
        "Content-Type": "application/json"
    }

    if input_type == "genre":
        input_data = {"type": "urn:tag:genre:media", "name": value.lower()}
    else:
        input_data = {"type": "urn:tag:mbti", "name": value.lower()}

    body = {
        "type": "urn:entity:brand",
        "inputs": [input_data]
    }

    response = requests.post(
        "https://hackathon.api.qloo.com/v2/recommendations",
        headers=headers,
        json=body
    )

    results = response.json().get("recommendations", [])
    return results  # returns full brand entities

# Detect user's country from IP
def get_user_country():
    try:
        ip_info = requests.get("https://ipinfo.io").json()
        return ip_info.get("country", "US")
    except:
        return "US"

def get_tmdb_details(name, tmdb_id=None):
    """
    Returns: (title, poster_url, overview)
    Tries TMDb ID first. Only falls back to name if ID fails.
    """
    detail = None

    if tmdb_id:
        detail = requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY, "language": "en-US"}
        ).json()
        if detail.get("status_code") == 34:  # TMDb "Not Found"
            detail = None

    if not detail:
        search = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": name, "include_adult": False}
        ).json().get("results", [])
        if search:
            detail = search[0]
        else:
            return name, None, ""

    title      = detail.get("title", name)
    poster     = detail.get("poster_path")
    overview   = detail.get("overview", "")
    poster_url = f"https://image.tmdb.org/t/p/w200{poster}" if poster else None

    return title, poster_url, overview

# Get streaming platforms for a movie
def get_streaming_platforms(movie_id, country_code):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params).json()
    platforms = response.get("results", {}).get(country_code, {}).get("flatrate", [])
    return [p["provider_name"] for p in platforms]

@st.cache_data(show_spinner=False)
def check_image(url):
    try:
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False

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

    movie_input    = st.text_input("🎬 Enter a movie title:", "")
    selected_genre = st.selectbox("Or select a genre:", [""] + genre_options)

    if st.button("Get Recommendations"):
        country_code = get_user_country()

        # flag to know if we showed Qloo recs
        used_qloo = False

        # 1) Qloo-first path
        if movie_input:
            search_url = "https://hackathon.api.qloo.com/search"
            headers    = {"X-Api-Key": QLOO_API_KEY}
            params     = {
                "query": movie_input.strip(),         # Qloo /search expects "query"
                "filter.type": "urn:entity:movie",
                "limit": 1
            }

            with st.spinner("🔍 Searching Qloo for your movie..."):
                search_resp = requests.get(search_url, headers=headers, params=params)

            # Debugging — uncomment to see raw Qloo response
            # st.write("Qloo status:", search_resp.status_code)
            # st.json(search_resp.json())

            qloo_results = search_resp.json().get("results", [])
            if not qloo_results:
                st.warning("Qloo couldn’t find the movie. Falling back to TMDb.")
            else:
                ent       = qloo_results[0]
                entity_id = ent["entity_id"]
                name      = ent["name"]

                rec_url = "https://hackathon.api.qloo.com/recommendations"
                rec_params = {"type": "urn:entity:movie", "entity_ids": entity_id}

                with st.spinner(f"🎬 Getting recs for '{name}'..."):
                    rec_resp = requests.get(rec_url, headers=headers, params=rec_params)

                recs = rec_resp.json().get("results", [])
                if recs:
                    used_qloo = True
                    st.success(f"🎥 Qloo Recommendations for '{name}':")
                    shown_ids = set()
                    
                    for r in recs[:10]:
                        nm   = r["name"]
                        props = r.get("properties", {}).get("external", {})
                        rt   = props.get("imdb", {}).get("user_rating", "N/A")
                        vt   = props.get("imdb", {}).get("user_rating_count", "N/A")
                        tmdb_id = props.get("tmdb", {}).get("id")
                    
                        # Try TMDb search if no external ID
                        if not tmdb_id:
                            search = requests.get(
                                "https://api.themoviedb.org/3/search/movie",
                                params={"api_key": TMDB_API_KEY, "query": nm, "include_adult": False}
                            ).json().get("results", [])
                            if search:
                                tmdb_id = search[0]["id"]
                    
                        # Skip if we've already shown this tmdb_id
                        if tmdb_id and tmdb_id in shown_ids:
                            continue
                        shown_ids.add(tmdb_id)
                    
                        # Fetch and display details
                        title, poster_url, overview = get_tmdb_details(nm, tmdb_id)
                    
                        if poster_url:
                            st.image(poster_url, width=120)
                        st.markdown(f"**🎬 {title}** — {rt} ⭐ ({vt} votes)")
                        if overview:
                            st.markdown(f"📝 {overview}")
                        st.markdown("---")
                else:
                    st.warning("Qloo found the movie but returned no recommendations. Falling back to TMDb.")

        # 2) Fallback to TMDb if no Qloo recommendations shown
        if movie_input and not used_qloo:
            st.info("🔄 Fetching from TMDb as fallback…")
            search_url = "https://api.themoviedb.org/3/search/movie"
            params     = {"api_key": TMDB_API_KEY, "query": movie_input, "include_adult": False}
            tmdb_search = requests.get(search_url, params=params).json().get("results", [])

            if not tmdb_search:
                st.error("❌ TMDb could not find that movie either.")
            else:
                tmdb_id    = tmdb_search[0]["id"]
                tmdb_title = tmdb_search[0]["title"]
                st.success(f"🎬 TMDb Recommendations based on '{tmdb_title}':")

                rec_url     = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations"
                rec_params  = {"api_key": TMDB_API_KEY, "language": "en-US", "page": 1}
                tmdb_recs   = requests.get(rec_url, params=rec_params).json().get("results", [])

                if not tmdb_recs:
                    st.warning("No TMDb recs found.")
                else:
                    for rec in tmdb_recs[:10]:
                        title       = rec["title"]
                        overview    = rec.get("overview", "")
                        rating      = rec.get("vote_average", "N/A")
                        votes       = rec.get("vote_count", "N/A")
                        poster_path = rec.get("poster_path")
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                        st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                        st.markdown(f"📝 {overview}")
                        st.markdown("---")

        # 3) Genre-based branch stays as-is…
        #elif selected_genre:
            # your existing Qloo-insights → TMDb fallback logic

        else:
            st.warning("Please enter a movie title or select a genre.")


# === Tab 2: Fashion & Brands ===
with tabs[1]:
    st.header("👚 Clothing & Brand Recommendations")
    st.markdown("Find clothing brands or outfits that match your media style or personality.")

    input_type = st.radio("Choose your input type:", ["Genre", "MBTI"])
    if input_type == "Genre":
        selected = st.selectbox("🎬 Select a genre:", genre_options)
        input_key = "genre"
    else:
        selected = st.text_input("🧠 Enter your MBTI type (e.g. INFP):")
        input_key = "mbti"

    if st.button("Find My StyleTwin"):
        if selected:
            styles = get_qloo_styles(input_key, selected)
            if styles:
                st.success("🎨 Your fashion archetypes:")
                cols = st.columns(2)
                for i, brand in enumerate(styles):
                    with cols[i % 2]:
                        brand_name = brand["name"]
                        tags = brand.get("tags", [])
    
                        # Filter for fashion-relevant style tags
                        style_keywords = ["core", "wear", "punk", "goth", "vintage", "grunge", "aesthetic", "boho", "minimal"]
                        style_tags = [tag["name"].lower() for tag in tags if any(k in tag["name"].lower() for k in style_keywords)]
    
                        st.markdown(f"### 👗 {brand_name}")
                        st.info("No specific fashion style tags found, but this brand may still fit your aesthetic.")
    
                        if style_tags:
                            first_style = style_tags[0]
                            search_query = next(
                                (v for k, v in style_search_terms.items() if k in first_style),
                                f"{first_style} fashion outfit"
                            )
                            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
                            params = {"query": search_query, "per_page": 1}
                            response = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
    
                            image_url = None
                            if response.status_code == 200:
                                results = response.json().get("results", [])
                                if results:
                                    image_url = results[0]["urls"]["small"]
                                    full_image_url = results[0]["urls"]["regular"]
    
                            if image_url:
                                st.image(image_url, caption=f"{first_style.title()} Look", use_container_width=True)
                                with st.expander("🔍 View More"):
                                    st.image(full_image_url, caption="Full Size", use_container_width=True)
                            else:
                                st.warning("⚠️ No image found for this style.")
                            st.markdown(f"**Style Tags:** {', '.join(style_tags)}")
                        else:
                            st.info("No specific fashion style tags found, but this brand may still fit your aesthetic.")
                        st.markdown("---")
            else:
                st.warning("No styles found for that input.")
        else:
            st.warning("Please enter a valid input.")


            
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

