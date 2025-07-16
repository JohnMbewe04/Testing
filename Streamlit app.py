import streamlit as st
import requests

QLOO_API_KEY = st.secrets["api"]["qloo_key"]
TMDB_API_KEY = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]

genre_options = ["comedy", "horror", "romance", "action", "animation", "crime", "sci-fi", "drama"]

style_search_terms = {
    "indie": "indie aesthetic outfit",
    "retro": "retro fashion look",
    "grunge": "grunge style clothing",
    "punk": "punk outfit fashion",
    "minimalist": "minimalist outfit woman",
    "techwear": "techwear fashion look",
    "cottagecore": "cottagecore outfit",
    "fairycore": "fairycore aesthetic clothes",
    "cyberpunk": "cyberpunk style clothes",
    "soft girl": "soft girl outfit aesthetic",
    "streetwear": "streetwear fashion",
    "clean girl": "clean girl fashion",
    "gothic": "gothic outfit",
    "boho": "boho fashion woman",
    "vintage": "vintage aesthetic look",
    "dark academia": "dark academia outfit",
    "avant-garde": "avant-garde fashion",
    "90s-core": "90s aesthetic outfit",
    "maximalist": "colorful maximalist fashion",
    "classic": "classic elegant fashion",
    "preppy": "preppy outfit aesthetic"
}


# 1) static mapping of media/music genre → Qloo‐style “tags”
genre_to_tags = {
    "comedy":    ["quirky", "heartwarming", "nostalgic"],
    "horror":    ["dark", "intense", "surreal"],
    "romance":   ["romantic", "elegant", "whimsical"],
    "sci-fi":    ["futuristic", "surreal", "dramatic"],
    "drama":     ["emotional", "elegant", "nostalgic"],
    "action":    ["gritty", "rebellious", "intense"],
    "animation": ["whimsical", "quirky", "nostalgic"],
    "crime":     ["gritty", "dark", "minimalist"]
}

music_to_tags = {
    "pop":       ["quirky", "whimsical"],
    "rock":      ["gritty", "rebellious"],
    "electronic":["futuristic", "edgy"],
    "jazz":      ["elegant", "nostalgic"],
    "classical": ["elegant", "minimalist"],
    "hip-hop":   ["streetwear", "edgy"]
}

# 2) Qloo style‐tag → fashion archetype
tag_to_style = {
    "quirky":      ["indie", "retro", "normcore"],
    "romantic":    ["cottagecore", "vintage", "soft girl"],
    "gritty":      ["grunge", "punk", "utilitarian"],
    "futuristic":  ["techwear", "cyberpunk"],
    "dark":        ["gothic", "alt", "emo"],
    "elegant":     ["classic", "preppy", "minimalist"],
    "rebellious":  ["punk", "streetwear", "biker"],
    "heartwarming":["softcore", "cozy", "vintage"],
    "whimsical":   ["fairycore", "boho", "eclectic"],
    "minimalist":  ["scandi", "normcore", "clean girl"],
    "dramatic":    ["avant-garde", "glam", "maximalist"],
    "nostalgic":   ["retro", "vintage", "90s-core"],
    "intense":     ["military", "dark academia", "utilitarian"],
    "surreal":     ["artcore", "experimental", "conceptual"],
    "edgy":        ["streetwear", "alt", "y2k"]
}

# 3) archetype → curated brand lists
style_to_brands = {
    "indie":       ["Urban Outfitters", "Monki", "Lazy Oaf"],
    "retro":       ["Beyond Retro", "Levi's", "Dickies"],
    "normcore":    ["Uniqlo", "Everlane", "Muji"],
    "cottagecore": ["Doen", "Christy Dawn", "Reformation"],
    "vintage":     ["Depop", "Thrifted", "Rokit"],
    "soft girl":   ["Brandy Melville", "YesStyle", "Princess Polly"],
    "grunge":      ["Killstar", "Disturbia", "Hot Topic"],
    "punk":        ["Tripp NYC", "Punk Rave", "AllSaints"],
    "techwear":    ["Acronym", "Nike ISPA", "Guerrilla Group"],
    "cyberpunk":   ["Demobaza", "Y-3", "Rick Owens"],
    "gothic":      ["Killstar", "The Black Angel", "Punk Rave"],
    "classic":     ["Ralph Lauren", "J.Crew", "Brooks Brothers"],
    "preppy":      ["Tommy Hilfiger", "GANT", "Lacoste"],
    "minimalist":  ["COS", "Everlane", "Arket"],
    "streetwear":  ["Supreme", "Stüssy", "Palace"],
    "boho":        ["Anthropologie", "Spell", "Free People"],
    "fairycore":   ["Selkie", "For Love & Lemons", "Free People"],
    "scandi":      ["Arket", "Weekday", "COS"],
    "clean girl":  ["Skims", "Aritzia", "Zara"],
    "avant-garde": ["Comme des Garçons", "Maison Margiela", "Rick Owens"],
    "glam":        ["House of CB", "Revolve", "PrettyLittleThing"],
    "maximalist":  ["Desigual", "Moschino", "The Attico"],
    "90s-core":    ["Tommy Jeans", "Fila", "Champion"],
    "dark academia":["Massimo Dutti","Ralph Lauren","Zara"]
    # …and so on
}

def get_archetypes_from_media(movie=None, genre=None, music=None):
    # 1) pick the raw tags
    raw_tags = []
    if movie:
        # pull TMDb genres
        t = requests.get(
            f"https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": movie}
        ).json().get("results", [])
        if t:
            # take the first movie’s genre names
            genre_ids = t[0].get("genre_ids", [])
            # map ids → names via your own TMDb genre lookup dictionary
            id2name = {28:"action",35:"comedy",18:"drama",10749:"romance",27:"horror",16:"animation",878:"sci-fi",80:"crime"}
            movie_genres = [id2name[g] for g in genre_ids if g in id2name]
            for g in movie_genres:
                raw_tags += genre_to_tags.get(g, [])

    elif genre:
        raw_tags = genre_to_tags.get(genre.lower(), [])

    elif music:
        raw_tags = music_to_tags.get(music.lower(), [])

    # 2) collapse tags → archetypes
    archetypes = set()
    for tag in raw_tags:
        for st in tag_to_style.get(tag, []):
            archetypes.add(st)

    return list(archetypes)

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

    media_type = st.radio("Input type:", ["Movie", "Genre", "Music"])
    if media_type == "Movie":
        user_input = st.text_input("Enter a movie title:")
    elif media_type == "Genre":
        user_input = st.selectbox("Select genre:", list(genre_to_tags.keys()))
    else:
        user_input = st.text_input("Enter a music genre:")

    if st.button("Find My Style"):
        # 3) get archetypes
        mc = user_input if media_type=="Movie" else None
        gc = user_input if media_type=="Genre" else None
        mu = user_input if media_type=="Music" else None

        archetypes = get_archetypes_from_media(movie=mc, genre=gc, music=mu)
        if not archetypes:
            st.warning("Sorry, we couldn't detect an aesthetic. Try another input.")
        else:
            st.success(f"Found these archetypes: {', '.join(archetypes)}")
            cols = st.columns(2)
            for idx, style in enumerate(archetypes):
                with cols[idx % 2]:
                    # your code continues...


        st.success(f"Found these archetypes: {', '.join(archetypes)}")

        cols = st.columns(2)
        for idx, style in enumerate(archetypes):
            with cols[idx % 2]:
                st.markdown(f"### 👗 {style.title()} Look")
                # Unsplash image
                q = style_search_terms.get(style, f"{style} outfit")
                resp = requests.get(
                    "https://api.unsplash.com/search/photos",
                    headers={"Authorization":f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                    params={"query":q,"per_page":1}
                )
                img = resp.json().get("results", [])
                if img:
                    thumb = img[0]["urls"]["small"]
                    full  = img[0]["urls"]["regular"]
                    st.image(thumb, use_column_width=True)
                    with st.expander("View full image"):
                        st.image(full, use_column_width=True)
                else:
                    st.warning("No image found")

                # Brands
                brands = style_to_brands.get(style, ["Coming soon…"])
                st.markdown("**🛍️ Suggested Brands:** " + ", ".join(f"🔸 {b}" for b in brands))
                st.markdown(", ".join(f"[{b}](https://www.google.com/search?q={b}+clothing)" for b in brands))

                st.markdown("---")
                st.info(f"Based on your love for *{user_input}*, your style twin might love:")

                
            
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

