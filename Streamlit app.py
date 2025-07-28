import streamlit as st
import requests
import urllib.parse
import base64

# -------------------------------------------------------------------
# Secrets & API Keys
# -------------------------------------------------------------------
QLOO_API_KEY        = st.secrets["api"]["qloo_key"]
TMDB_API_KEY        = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]
lastfm_API_KEY = st.secrets["api"]["lastfm_key"]
SPOTIFY_CLIENT_ID = st.secrets["spotify"]["client_id"]
SPOTIFY_CLIENT_SECRET = st.secrets["spotify"]["client_secret"]

# -------------------------------------------------------------------
# Style & Genre Mappings
# -------------------------------------------------------------------
genre_options = ["comedy","horror","romance","action","animation","crime","sci-fi","drama", "anime"]

style_search_terms = {
    "indie":       "indie aesthetic outfit",
    "retro":       "retro fashion look",
    "grunge":      "grunge style clothing",
    "punk":        "punk outfit fashion",
    "minimalist":  "minimalist outfit woman",
    "techwear":    "techwear fashion look",
    "cottagecore": "cottagecore outfit",
    "fairycore":   "fairycore aesthetic clothes",
    "cyberpunk":   "cyberpunk style clothes",
    "soft girl":   "soft girl outfit aesthetic",
    "streetwear":  "streetwear fashion",
    "clean girl":  "clean girl fashion",
    "gothic":      "gothic outfit",
    "boho":        "boho fashion woman",
    "vintage":     "vintage aesthetic look",
    "dark academia":"dark academia outfit",
    "avant-garde": "avant-garde fashion",
    "90s-core":    "90s aesthetic outfit",
    "maximalist":  "colorful maximalist fashion",
    "classic":     "classic elegant fashion",
    "preppy":      "preppy outfit aesthetic",
    "normcore":    "normcore fashion",
    "utilitarian": "utilitarian outfit",
    "alt":         "alt fashion look",
    "emo":         "emo aesthetic outfit",
    "softcore":    "softcore aesthetic clothes",
    "cozy":        "cozy aesthetic fashion",
    "eclectic":    "eclectic fashion look",
    "biker":       "biker outfit aesthetic",
    "scandi":      "scandi fashion",
    "y2k":         "y2k fashion",
    "artcore":     "artcore fashion",
    "experimental":"experimental outfit",
    "conceptual":  "conceptual fashion"
}

style_to_brands = {
    "indie":       ["Urban Outfitters","Monki","Lazy Oaf"],
    "retro":       ["Beyond Retro","Levi's","Dickies"],
    "normcore":    ["Uniqlo","Everlane","Muji"],
    "cottagecore": ["Doen","Christy Dawn","Reformation"],
    "vintage":     ["Depop","Thrifted","Rokit"],
    "soft girl":   ["Brandy Melville","YesStyle","Princess Polly"],
    "grunge":      ["Killstar","Disturbia","Hot Topic"],
    "punk":        ["Tripp NYC","Punk Rave","AllSaints"],
    "techwear":    ["Acronym","Nike ISPA","Guerrilla Group"],
    "cyberpunk":   ["Demobaza","Y-3","Rick Owens"],
    "gothic":      ["Killstar","The Black Angel","Punk Rave"],
    "classic":     ["Ralph Lauren","J.Crew","Brooks Brothers"],
    "preppy":      ["Tommy Hilfiger","GANT","Lacoste"],
    "minimalist":  ["COS","Everlane","Arket"],
    "streetwear":  ["Supreme","Stüssy","Palace"],
    "boho":        ["Anthropologie","Spell","Free People"],
    "fairycore":   ["Selkie","For Love & Lemons","Free People"],
    "scandi":      ["Arket","Weekday","COS"],
    "clean girl":  ["Skims","Aritzia","Zara"],
    "avant-garde": ["Comme des Garçons","Maison Margiela","Rick Owens"],
    "glam":        ["House of CB","Revolve","PrettyLittleThing"],
    "maximalist":  ["Desigual","Moschino","The Attico"],
    "90s-core":    ["Tommy Jeans","Fila","Champion"],
    "dark academia":["Massimo Dutti","Ralph Lauren","Zara"]
}

genre_to_tags = {
    "comedy":    ["quirky","heartwarming","nostalgic"],
    "horror":    ["dark","intense","surreal"],
    "romance":   ["romantic","elegant","whimsical"],
    "sci-fi":    ["futuristic","surreal","dramatic"],
    "drama":     ["emotional","elegant","nostalgic"],
    "action":    ["gritty","rebellious","intense"],
    "animation": ["whimsical","quirky","nostalgic"],
    "crime":     ["gritty","dark","minimalist"]
}

music_to_tags = {
    "pop":        ["quirky","whimsical"],
    "rock":       ["gritty","rebellious"],
    "electronic": ["futuristic","edgy"],
    "jazz":       ["elegant","nostalgic"],
    "classical":  ["elegant","minimalist"],
    "hip-hop":    ["streetwear","edgy"]
}

tag_to_style = {
    "quirky":      ["indie","retro","normcore"],
    "romantic":    ["cottagecore","vintage","soft girl"],
    "gritty":      ["grunge","punk","utilitarian"],
    "futuristic":  ["techwear","cyberpunk"],
    "dark":        ["gothic","alt","emo"],
    "elegant":     ["classic","preppy","minimalist"],
    "rebellious":  ["punk","streetwear","biker"],
    "heartwarming":["softcore","cozy","vintage"],
    "whimsical":   ["fairycore","boho","eclectic"],
    "minimalist":  ["scandi","normcore","clean girl"],
    "dramatic":    ["avant-garde","glam","maximalist"],
    "nostalgic":   ["retro","vintage","90s-core"],
    "intense":     ["military","dark academia","utilitarian"],
    "surreal":     ["artcore","experimental","conceptual"],
    "edgy":        ["streetwear","alt","y2k"]
}

# Genre to Tags
# (other dictionaries omitted here to save space, same as previous version)
# Include: genre_to_tags, music_to_tags, tag_to_style, style_to_brands
# [Insert same dictionaries from your previous code here]

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def get_archetypes_from_media(movie=None, genre=None, music=None):
    raw_tags = []
    if movie:
        res = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": movie}
        ).json().get("results", [])
        if res:
            id2name = {28:"action",35:"comedy",18:"drama",10749:"romance",
                       27:"horror",16:"animation",878:"sci-fi",80:"crime"}
            for gid in res[0].get("genre_ids", []):
                raw_tags += genre_to_tags.get(id2name.get(gid, ""), [])
    elif genre:
        raw_tags = genre_to_tags.get(genre.lower(), [])
    elif music:
        raw_tags = music_to_tags.get(music.lower(), [])

    arch = set()
    for t in raw_tags:
        arch.update(tag_to_style.get(t, []))
    return list(arch)

@st.cache_data(ttl=300)
def get_outfit_images(q, per_page=4):
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        params={"query": q, "per_page": per_page}
    )
    return resp.json().get("results", [])

def get_user_country():
    try:
        import geocoder
        g = geocoder.ip("me")
        return g.country or "US"
    except:
        return "US"

def get_tmdb_details(name, tmdb_id=None):
    detail = None
    if tmdb_id:
        detail = requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY, "language": "en-US"}
        ).json()
        if detail.get("status_code") == 34:
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

    title = detail.get("title", name)
    poster = detail.get("poster_path")
    overview = detail.get("overview", "")
    poster_url = f"https://image.tmdb.org/t/p/w200{poster}" if poster else None
    return title, poster_url, overview

def get_similar_movies(movie_name, limit=5):
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}
    search_resp = requests.get(search_url, params=params).json()
    results = search_resp.get("results", [])

    if not results:
        return []

    movie_id = results[0]["id"]
    rec_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
    rec_params = {"api_key": TMDB_API_KEY}
    rec_resp = requests.get(rec_url, params=rec_params).json()
    recs = rec_resp.get("results", [])[:limit]

    return [
        {
            "id": r.get("id"),
            "title": r.get("title"),
            "overview": r.get("overview", ""),
            "poster": f"https://image.tmdb.org/t/p/w200{r['poster_path']}" if r.get("poster_path") else None
        }
        for r in recs
    ]

def get_movies_by_genre(genre_name, country_code="US"):
    GENRE_MAP = {
        "action": 28, "comedy": 35, "drama": 18, "sci-fi": 878,
        "romance": 10749, "horror": 27, "animation": 16, "crime": 80
        # Add more genres if needed
    }
    genre_id = GENRE_MAP.get(genre_name.lower())
    if not genre_id:
        st.warning("Selected genre is not supported.")
        return []

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "region": country_code,
        "sort_by": "popularity.desc",
        "language": "en-US"
    }
    response = requests.get(url, params=params).json()
    return [{
        "title": m.get("title"),
        "id": m.get("id"),
        "poster": f"https://image.tmdb.org/t/p/w200{m['poster_path']}" if m.get("poster_path") else None,
        "overview": m.get("overview")
    } for m in response.get("results", [])]

def get_streaming_platforms(movie_id, country_code):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params).json()
    platforms = response.get("results", {}).get(country_code, {}).get("flatrate", [])
    return [p["provider_name"] for p in platforms]

def get_similar_songs(song_name, limit=5):
    base_url = "http://ws.audioscrobbler.com/2.0/"

    search_params = {
        "method": "track.search",
        "track": song_name,
        "api_key": lastfm_API_KEY,
        "format": "json",
        "limit": 1
    }
    search_resp = requests.get(base_url, params=search_params).json()
    results = search_resp.get("results", {}).get("trackmatches", {}).get("track", [])

    # Ensure results is a list
    if isinstance(results, dict):
        results = [results]

    if not results:
        return []

    artist = results[0].get("artist")
    track = results[0].get("name")

    sim_params = {
        "method": "track.getsimilar",
        "artist": artist,
        "track": track,
        "api_key": lastfm_API_KEY,
        "format": "json",
        "limit": limit
    }

    sim_resp = requests.get(base_url, params=sim_params).json()
    similar = sim_resp.get("similartracks", {}).get("track", [])

    if isinstance(similar, dict):
        similar = [similar]

    return [
        {
            "title": s.get("name", "Unknown"),
            "artist": s.get("artist", {}).get("name", "Unknown"),
            "url": s.get("url", "#")
        }
        for s in similar
    ]

# --- Spotify Auth ---
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {'Authorization': f'Basic {auth_header}'}
    data = {'grant_type': 'client_credentials'}
    resp = requests.post(auth_url, headers=headers, data=data)
    return resp.json().get("access_token")

def get_similar_songs_spotify(song_name, token, limit=5):
    # 1. Search for the song to get its track ID
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    search_params = {"q": song_name, "type": "track", "limit": 1}
    search_resp = requests.get(search_url, headers=headers, params=search_params).json()
    items = search_resp.get("tracks", {}).get("items", [])
    
    if not items:
        return []

    seed_track_id = items[0]["id"]

    # 2. Use the track ID to get recommendations
    rec_url = "https://api.spotify.com/v1/recommendations"
    rec_params = {
        "limit": limit,
        "seed_tracks": seed_track_id
    }

    rec_resp = requests.get(rec_url, headers=headers, params=rec_params).json()
    rec_tracks = rec_resp.get("tracks", [])

    return [
        {
            "title": t["name"],
            "artist": t["artists"][0]["name"],
            "album_img": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
            "preview_url": t.get("preview_url"),
            "spotify_url": t["external_urls"]["spotify"]
        }
        for t in rec_tracks
    ]


# --- Spotify Search ---
def get_spotify_song_data(song_name, token, limit=5):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": song_name, "type": "track", "limit": limit}

    resp = requests.get(search_url, headers=headers, params=params).json()
    tracks = resp.get("tracks", {}).get("items", [])

    return [
        {
            "title": t["name"],
            "artist": t["artists"][0]["name"],
            "album_img": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
            "preview_url": t.get("preview_url"),
            "spotify_url": t["external_urls"]["spotify"]
        }
        for t in tracks
    ]



# -------------------------------------------------------------------
# Session State Setup
# -------------------------------------------------------------------
TAB_MEDIA   = "🎬 Media Style Match"
TAB_FASHION = "👗 Fashion & Brands"
TAB_FIT     = "🧍 AI Fitting Room"

for key, default in [
    ("active_tab", TAB_MEDIA),
    ("archetypes", []),
    ("selected_style", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "ready_for_fashion" not in st.session_state:
    st.session_state.ready_for_fashion = False

if "similar_movies" not in st.session_state:
    st.session_state["similar_movies"] = []

if "user_country" not in st.session_state:
    st.session_state.user_country = get_user_country()

# -------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------
st.set_page_config(page_title="AI StyleTwin", layout="wide")
st.title("🧠 AI StyleTwin")
st.caption("Discover your aesthetic twin in media and fashion.")

choice = st.radio("Go to:", [TAB_MEDIA, TAB_FASHION, TAB_FIT],
    index=[TAB_MEDIA, TAB_FASHION, TAB_FIT].index(st.session_state.active_tab),
    horizontal=True)
st.session_state.active_tab = choice
st.write("---")

# -------------------------------------------------------------------
# Media Style Match + Music Recommendations
# -------------------------------------------------------------------
if choice == TAB_MEDIA:
    st.header("🎥 Media Style Match")
    st.caption("Discover your fashion style or find similar songs based on your tastes.")

    # Radio to choose mode
    mode = st.radio("Choose mode:", ["🎬 Find My Fashion Style", "🎵 Get Similar Songs"], horizontal=True)

    # ----------------------------
    # 🎬 Mode 1: Fashion Archetypes
    # ----------------------------
    if mode == "🎬 Find My Fashion Style":
        movie_input = st.text_input("Enter a movie title:")
        selected_genre = st.selectbox("…or pick a genre:", [""] + genre_options)

        if st.button("Get Recommendations"):
            if not movie_input and not selected_genre:
                st.warning("Please enter a movie title or genre.")
            else:
                st.session_state.archetypes = get_archetypes_from_media(
                    movie=movie_input or None,
                    genre=selected_genre or None,
                    music=None
                )
        
                # 🎬 Fallback logic for similar movies
                if movie_input:
                    st.session_state.similar_movies = get_similar_movies(movie_input)
                elif selected_genre:
                    st.session_state.similar_movies = get_movies_by_genre(selected_genre, st.session_state.user_country)
        
                st.session_state.selected_style = None
                st.session_state.ready_for_fashion = True
                st.success("Style archetypes and movie recommendations loaded!")

        if st.session_state.similar_movies:
            st.markdown("### 🎬 You Might Also Like")
            for m in st.session_state.similar_movies:
                if not m or "title" not in m:
                    continue  # skip invalid entries
            
                cols = st.columns([1, 4])
                with cols[0]:
                    if m.get("poster"):
                        st.image(m["poster"], width=100)
            
                with cols[1]:
                    st.markdown(f"**{m.get('title', 'Untitled')}**")
                    st.caption(m.get("overview", "No description available."))
            
                    movie_id = m.get("id")
                    if movie_id:
                        providers = get_streaming_platforms(movie_id, st.session_state.user_country)
                        if providers:
                            PLATFORM_URLS = {
                                "Netflix": "https://www.netflix.com",
                                "Disney+": "https://www.disneyplus.com",
                                "Amazon Prime Video": "https://www.primevideo.com",
                                "Hulu": "https://www.hulu.com",
                                "Apple TV+": "https://tv.apple.com"
                            }
                            links = [f"[{name}]({PLATFORM_URLS.get(name, '#')})" for name in providers]
                            st.markdown("🌐 Available on: " + ", ".join(links))
                        else:
                            st.caption("Streaming availability not found for your region.")
                st.write("---")

        if st.session_state.ready_for_fashion:
            st.markdown("---")
            st.markdown("### 👗 Ready to explore fashion inspired by these vibes?")
            if st.button("Explore Fashion Recommendations"):
                st.session_state.active_tab = TAB_FASHION
                st.rerun()

    # ----------------------------
    # 🎵 Mode 2: Music Recommendations
    # ----------------------------
    else:
        song_input = st.text_input("Enter a song you like:")
    
        if st.button("Get Similar Songs"):
            if not song_input:
                st.warning("Please enter a song name first.")
            else:
                with st.spinner("🔍 Getting Spotify previews..."):
                    client_id = st.secrets["spotify"]["client_id"]
                    client_secret = st.secrets["spotify"]["client_secret"]
                    token = get_spotify_token(client_id, client_secret)
                    songs = get_similar_songs_spotify(song_input, token)

                if not songs:
                    st.error("No similar tracks found.")
                else:
                    for song in songs:
                        cols = st.columns([1, 4])
                        with cols[0]:
                            if song["album_img"]:
                                st.image(song["album_img"], width=80)
                        with cols[1]:
                            st.markdown(f"**🎵 {song['title']}** by *{song['artist']}*")
                            if song["preview_url"]:
                                st.audio(song["preview_url"], format="audio/mp3")
                            st.markdown(f"[🔗 Listen on Spotify]({song['spotify_url']})")
                        st.write("---")



# -------------------------------------------------------------------
# Fashion & Brands
# -------------------------------------------------------------------
elif choice == TAB_FASHION:
    st.header("👚 Fashion & Brand Recommendations")

    if not st.session_state.archetypes:
        st.info("First, run 'Get Recommendations' in the Media tab.")
    else:
        st.success("Detected archetypes: " + ", ".join(st.session_state.archetypes))

        cols = st.columns(2)
        for idx, style in enumerate(st.session_state.archetypes):
            with cols[idx % 2]:
                st.markdown(f"### 👗 {style.title()} Look")
                with st.spinner("Fetching outfit image..."):
                    imgs = get_outfit_images(style_search_terms.get(style, f"{style} outfit"), per_page=1)
                if imgs:
                    st.image(imgs[0]["urls"]["small"], use_column_width=True)
                else:
                    st.warning("No preview image found.")

                brands = style_to_brands.get(style, ["Coming soon…"])
                st.markdown("**🛍️ Brands:**<br>" + "<br>".join(
                    f"<a href='https://google.com/search?q={urllib.parse.quote_plus(b + ' clothing')}' target='_blank'>{b}</a>"
                    for b in brands
                ), unsafe_allow_html=True)

                if st.button(f"Try {style}", key=f"try_{style}"):
                    st.session_state.selected_style = style
                    st.session_state.active_tab = TAB_FIT
                    st.rerun()

        if st.button("🔙 Back to Media Tab"):
            st.session_state.active_tab = TAB_MEDIA
            st.rerun()

# -------------------------------------------------------------------
# AI Fitting Room
# -------------------------------------------------------------------
else:
    st.header("🧍 Virtual Fitting Room")
    style = st.session_state.selected_style

    if not style:
        st.warning("First, pick a look in the Fashion tab.")
    else:
        st.success(f"Fitting Room – {style.title()} Look")
        selfie = st.camera_input("📸 Take a selfie") or st.file_uploader("…or upload an image")
        if selfie:
            st.image(selfie, caption="You", width=200)
            with st.spinner("Loading style options..."):
                outfits = get_outfit_images(style_search_terms[style], per_page=4)
            cols = st.columns(2)
            for i, o in enumerate(outfits):
                with cols[i % 2]:
                    st.image(o["urls"]["small"], caption=f"{style.title()} #{i+1}", use_column_width=True)

        if st.button("🔙 Back to Fashion Tab"):
            st.session_state.active_tab = TAB_FASHION
            st.rerun()
