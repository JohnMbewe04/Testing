import streamlit as st
import requests

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

style_to_brands = {
        "indie": ["Urban Outfitters", "Monki", "Lazy Oaf"],
        "retro": ["Beyond Retro", "Levi's", "Dickies"],
        "normcore": ["Uniqlo", "Everlane", "Muji"],
        "cottagecore": ["Doen", "Christy Dawn", "Reformation"],
        "vintage": ["Depop", "Thrifted", "Rokit"],
        "soft girl": ["Brandy Melville", "YesStyle", "Princess Polly"],
        "grunge": ["Killstar", "Disturbia", "Hot Topic"],
        "punk": ["Tripp NYC", "Punk Rave", "AllSaints"],
        "utilitarian": ["Carhartt", "Acronym", "Nike ACG"],
        "techwear": ["Acronym", "Nike ISPA", "Guerrilla Group"],
        "cyberpunk": ["Demobaza", "Y-3", "Rick Owens"],
        "gothic": ["Killstar", "Punk Rave", "The Black Angel"],
        "alt": ["Dolls Kill", "Unif", "Disturbia"],
        "emo": ["Hot Topic", "Atticus", "Drop Dead"],
        "classic": ["Ralph Lauren", "J.Crew", "Brooks Brothers"],
        "preppy": ["Tommy Hilfiger", "GANT", "Lacoste"],
        "minimalist": ["COS", "Everlane", "Arket"],
        "streetwear": ["Supreme", "Stüssy", "Palace"],
        "biker": ["Schott NYC", "AllSaints", "Harley-Davidson"],
        "softcore": ["Aritzia", "Frank & Oak", "Sézane"],
        "cozy": ["Uniqlo", "Lululemon", "Skims"],
        "y2k": ["IMVU", "Dolls Kill", "Jaded London"],
        "fairycore": ["Selkie", "For Love & Lemons", "Free People"],
        "boho": ["Anthropologie", "Spell", "Free People"],
        "eclectic": ["Lisa Says Gah", "Gorman", "Desigual"],
        "scandi": ["Arket", "Weekday", "COS"],
        "clean girl": ["Skims", "Aritzia", "Zara"],
        "avant-garde": ["Comme des Garçons", "Maison Margiela", "Rick Owens"],
        "glam": ["House of CB", "Revolve", "PrettyLittleThing"],
        "maximalist": ["Desigual", "Moschino", "The Attico"],
        "90s-core": ["Tommy Jeans", "Fila", "Champion"],
        "military": ["Alpha Industries", "Rothco", "Stone Island"],
        "dark academia": ["Ralph Lauren", "Massimo Dutti", "Zara"],
        "artcore": ["Issey Miyake", "Acne Studios", "Marni"],
        "experimental": ["Maison Margiela", "Craig Green", "Rick Owens"],
        "conceptual": ["Comme des Garçons", "Yohji Yamamoto", "Iris van Herpen"]
    }

QLOO_API_KEY = st.secrets["api"]["qloo_key"]
TMDB_API_KEY = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]

# Map Qloo tags to fashion archetypes
def get_fashion_archetypes(input_type, value):
    tag_to_style = {
        "quirky": ["indie", "retro", "normcore"],
        "romantic": ["cottagecore", "vintage", "soft girl"],
        "gritty": ["grunge", "punk", "utilitarian"],
        "futuristic": ["techwear", "cyberpunk"],
        "dark": ["gothic", "alt", "emo"],
        "elegant": ["classic", "preppy", "minimalist"],
        "rebellious": ["punk", "streetwear", "biker"],
        "heartwarming": ["softcore", "cozy", "vintage"],
        "edgy": ["streetwear", "alt", "y2k"],
        "whimsical": ["fairycore", "boho", "eclectic"],
        "minimalist": ["scandi", "normcore", "clean girl"],
        "dramatic": ["avant-garde", "glam", "maximalist"],
        "nostalgic": ["retro", "vintage", "90s-core"],
        "intense": ["military", "dark academia", "utilitarian"],
        "surreal": ["artcore", "experimental", "conceptual"]
    }
    genre_to_tags = {
        "comedy": ["quirky", "heartwarming", "awkward"],
        "horror": ["dark", "intense", "surreal"],
        "romance": ["romantic", "elegant", "whimsical"],
        "sci-fi": ["futuristic", "surreal", "dramatic"],
        "drama": ["emotional", "elegant", "nostalgic"],
        "action": ["gritty", "rebellious", "intense"],
        "animation": ["whimsical", "quirky", "nostalgic"],
        "crime": ["gritty", "dark", "minimalist"]
    }
    
    mbti_to_tags = {
        "infp": ["whimsical", "romantic", "nostalgic"],
        "intj": ["minimalist", "dark", "futuristic"],
        "enfp": ["quirky", "dramatic", "eclectic"],
        "istp": ["gritty", "rebellious", "utilitarian"]
    }
    
    tags = []
    if input_type == "genre":
        tags = genre_to_tags.get(value.lower(), [])
    elif input_type == "mbti":
        tags = mbti_to_tags.get(value.lower(), [])
    
    styles = set()
    for tag in tags:
        styles.update(tag_to_style.get(tag, []))
    
    return list(styles)

# Detect user's country from IP
def get_user_country():
    try:
        ip_info = requests.get("https://ipinfo.io").json()
        return ip_info.get("country", "US")
    except:
        return "US"

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
        used_qloo = False

        # 1) Qloo-first: movie title search
        if movie_input:
            qloo_rec_url = "https://hackathon.api.qloo.com/v2/recommendations"
            headers = {
                "X-Api-Key": QLOO_API_KEY,
                "Content-Type": "application/json"
            }
            body = {
                "type": "urn:entity:movie",
                "inputs": [
                    {"type": "urn:entity:movie", "name": movie_input.strip()}
                ]
            }

            with st.spinner("🔍 Fetching recommendations from Qloo..."):
                qloo_resp = requests.post(qloo_rec_url, headers=headers, json=body)
            recs = qloo_resp.json().get("recommendations", [])

            if recs:
                used_qloo = True
                st.success(f"🎥 Qloo Recommendations for '{movie_input.strip()}':")
                for r in recs[:10]:
                    name  = r["name"]
                    props = r.get("properties", {}).get("external", {}).get("tmdb", {})
                    tmdb_id = props.get("id")

                    # Fetch TMDb details if we have an ID
                    if tmdb_id:
                        detail = requests.get(
                            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                            params={"api_key": TMDB_API_KEY, "language": "en-US"}
                        ).json()
                        poster   = detail.get("poster_path")
                        overview = detail.get("overview", "")

                        if poster:
                            st.image(f"https://image.tmdb.org/t/p/w300{poster}", width=120)
                        st.markdown(f"**🎬 {detail.get('title', name)}**")
                        st.markdown(f"📝 {overview}")
                        st.markdown("---")
                    else:
                        st.markdown(f"**🎬 {name}** — details unavailable")
                        st.markdown("---")
            else:
                st.warning("Qloo found no recommendations for that title. Falling back to TMDb.")

        # 2) Qloo-first: genre-based recommendations
        elif selected_genre:
            qloo_rec_url = "https://hackathon.api.qloo.com/v2/recommendations"
            headers = {
                "X-Api-Key": QLOO_API_KEY,
                "Content-Type": "application/json"
            }
            body = {
                "type": "urn:entity:movie",
                "inputs": [
                    {"type": "urn:tag:genre:media", "name": selected_genre}
                ]
            }

            with st.spinner("🎞️ Fetching genre-based recs from Qloo..."):
                qloo_resp = requests.post(qloo_rec_url, headers=headers, json=body)
            recs = qloo_resp.json().get("recommendations", [])

            if recs:
                used_qloo = True
                st.success(f"🎬 Qloo Movie Picks for {selected_genre.title()}:")
                for r in recs[:10]:
                    name  = r["name"]
                    props = r.get("properties", {}).get("external", {}).get("tmdb", {})
                    tmdb_id = props.get("id")

                    if tmdb_id:
                        detail = requests.get(
                            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                            params={"api_key": TMDB_API_KEY, "language": "en-US"}
                        ).json()
                        poster   = detail.get("poster_path")
                        overview = detail.get("overview", "")

                        if poster:
                            st.image(f"https://image.tmdb.org/t/p/w300{poster}", width=120)
                        st.markdown(f"**🎬 {detail.get('title', name)}**")
                        st.markdown(f"📝 {overview}")
                        st.markdown("---")
                    else:
                        st.markdown(f"**🎬 {name}** — details unavailable")
                        st.markdown("---")
            else:
                st.warning("Qloo returned no genre recommendations. Falling back to TMDb.")

        # 3) TMDb fallback if Qloo yielded nothing
        if (movie_input or selected_genre) and not used_qloo:
            st.info("🔄 Fetching recommendations from TMDb as fallback…")

            if movie_input:
                # TMDb similar by title
                search_url = "https://api.themoviedb.org/3/search/movie"
                params     = {"api_key": TMDB_API_KEY, "query": movie_input, "include_adult": False}
                results    = requests.get(search_url, params=params).json().get("results", [])

                if not results:
                    st.error("❌ TMDb could not find that title.")
                else:
                    tmdb_id    = results[0]["id"]
                    tmdb_title = results[0]["title"]
                    st.success(f"🎬 TMDb Recommendations based on '{tmdb_title}':")
                    rec_url     = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations"
                    rec_params  = {"api_key": TMDB_API_KEY, "language": "en-US", "page": 1}
                    tmdb_recs   = requests.get(rec_url, params=rec_params).json().get("results", [])

                    for rec in tmdb_recs[:10]:
                        title       = rec["title"]
                        poster_path = rec.get("poster_path")
                        overview    = rec.get("overview", "")
                        rating      = rec.get("vote_average", "N/A")
                        votes       = rec.get("vote_count", "N/A")

                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                        st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                        st.markdown(f"📝 {overview}")
                        st.markdown("---")

            else:
                # TMDb popular by genre
                genre_map = {
                    "action": 28, "animation": 16, "comedy": 35, "crime": 80,
                    "drama": 18,  "horror": 27, "romance": 10749, "sci-fi": 878
                }
                gid = genre_map[selected_genre.lower()]
                st.success(f"🎬 Popular {selected_genre.title()} Movies (via TMDb):")

                disc_url    = "https://api.themoviedb.org/3/discover/movie"
                disc_params = {
                    "api_key": TMDB_API_KEY,
                    "with_genres": gid,
                    "sort_by": "popularity.desc",
                    "language": "en-US",
                    "page": 1
                }
                tmdb_recs = requests.get(disc_url, params=disc_params).json().get("results", [])

                for rec in tmdb_recs[:10]:
                    title       = rec["title"]
                    poster_path = rec.get("poster_path")
                    overview    = rec.get("overview", "")
                    rating      = rec.get("vote_average", "N/A")
                    votes       = rec.get("vote_count", "N/A")

                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                    st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                    st.markdown(f"📝 {overview}")
                    st.markdown("---")

        # 4) No input at all
        elif not movie_input and not selected_genre:
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
            styles = get_fashion_archetypes(input_key, selected)
            if styles:
                st.success("🎨 Your fashion archetypes:")
                
                cols = st.columns(2)  # 2-column layout
                
                for i, style in enumerate(styles):
                    with cols[i % 2]:
                        st.markdown(f"### 👗 {style.title()}")
                
                        # Build search query
                        search_query = style_search_terms.get(style.lower(), f"{style} outfit street style")
                        headers = {"Authorization": f"Client-ID {st.secrets['api']['unsplash_key']}"}
                        params = {"query": search_query, "per_page": 1}
                        response = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
                
                        image_url = None
                        if response.status_code == 200:
                            results = response.json().get("results", [])
                            if results:
                                image_url = results[0]["urls"]["small"]
                                full_image_url = results[0]["urls"]["regular"]
                        
                        if image_url:
                            st.image(image_url, caption=f"{style.title()} Look", use_container_width=True)
                            with st.expander("🔍 View More"):
                                st.image(full_image_url, caption="Full Size", use_container_width=True)
                        else:
                            st.warning("⚠️ No image found for this style.")
                
                        # Suggested brands
                        brands = style_to_brands.get(style.lower(), ["Coming soon..."])
                        st.markdown(f"**Suggested Brands:** {', '.join(brands)}")
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

