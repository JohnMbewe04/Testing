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

    movie_input = st.text_input("🎬 Enter a movie title:", "")
    selected_genre = st.selectbox("Or select a genre:", [""] + genre_options)

    if st.button("Get Recommendations"):
        country_code = get_user_country()

        # ---- Qloo-first movie lookup & recs ----
        if movie_input:
            # 1) Search Qloo for the movie entity
            search_url = "https://hackathon.api.qloo.com/search"
            headers = {"X-Api-Key": QLOO_API_KEY}
            params = {
                "query": movie_input.strip(),          # ← use "query", not "q"
                "filter.type": "urn:entity:movie",
                "limit": 5
            }

            with st.spinner("🔍 Searching Qloo for your movie..."):
                search_resp = requests.get(search_url, headers=headers, params=params)

            # Debug: uncomment to see raw JSON
            # st.json(search_resp.json())

            qloo_results = search_resp.json().get("results", [])
            if not qloo_results:
                st.warning("Qloo couldn’t find the movie. Falling back to TMDb.")
                fallback_used = True
            else:
                ent = qloo_results[0]
                entity_id, entity_name = ent["entity_id"], ent["name"]

                # 2) Get Qloo recommendations
                rec_url = "https://hackathon.api.qloo.com/recommendations"
                rec_params = {"type": "urn:entity:movie", "entity_ids": entity_id}
                with st.spinner(f"🎬 Getting recs for '{entity_name}'..."):
                    rec_resp = requests.get(rec_url, headers=headers, params=rec_params)

                recs = rec_resp.json().get("results", [])
                if recs:
                    st.success(f"🎥 Qloo Recommendations for '{entity_name}':")
                    for r in recs[:10]:
                        name = r["name"]
                        imdb = r.get("properties", {}).get("external", {}).get("imdb", {})
                        rating = imdb.get("user_rating", "N/A")
                        votes  = imdb.get("user_rating_count", "N/A")
                        st.markdown(f"**🎬 {name}** — {rating} ⭐ ({votes} votes)")
                    return  # stop here if Qloo gave us something
                else:
                    st.warning("Qloo returned no recommendations. Falling back to TMDb.")
                    fallback_used = True

        # ---- TMDb fallback ----
        if movie_input and fallback_used:
            st.info("🔄 Fetching from TMDb as fallback…")
            tmdb_search_url = "https://api.themoviedb.org/3/search/movie"
            tmdb_params     = {"api_key": TMDB_API_KEY, "query": movie_input, "include_adult": False}
            tmdb_search     = requests.get(tmdb_search_url, params=tmdb_params).json()
            results         = tmdb_search.get("results", [])
            if not results:
                st.error("❌ TMDb could not find the movie.")
            else:
                tmdb_id, tmdb_title = results[0]["id"], results[0]["title"]
                st.success(f"🎬 TMDb Recommendations based on '{tmdb_title}':")
                tmdb_rec_url    = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations"
                tmdb_rec_params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": 1}
                tmdb_recs       = requests.get(tmdb_rec_url, params=tmdb_rec_params).json().get("results", [])
                if not tmdb_recs:
                    st.warning("No TMDb recs found.")
                else:
                    for rec in tmdb_recs[:10]:
                        title       = rec["title"]
                        overview    = rec.get("overview","")
                        rating      = rec.get("vote_average","N/A")
                        votes       = rec.get("vote_count","N/A")
                        poster_path = rec.get("poster_path")
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}", width=120)
                        st.markdown(f"**🎬 {title}** — {rating} ⭐ ({votes} votes)")
                        st.markdown(f"📝 {overview}")
                        st.markdown("---")
        # …then your genre branch below…

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

