import streamlit as st
import requests
import urllib.parse
import base64
import json
import time
import random
from PIL import Image
from io import BytesIO
import numpy as np
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
from streamlit_js_eval import streamlit_js_eval

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
genre_options = ["comedy","horror","romance","action","animation","crime","sci-fi","drama"]

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
@st.cache_data(ttl=600)
def upload_to_imgbb(image_file):
    api_key = st.secrets["imgbb"]["imgbb_api_key"]
    url = "https://api.imgbb.com/1/upload"

    # Read and encode image
    image_bytes = image_file.read()
    b64_encoded = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "key": api_key,
        "image": b64_encoded
    }

    response = requests.post(url, data=payload)
    data = response.json()
    return data["data"]["url"] if data.get("data") else None

@st.cache_data
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def render_coverflow(images):
    image_html = ''.join(f"<div class='slide'><img src='{url}' onclick=\"selectImage('{url}')\"></div>" for url in images)

    html_code = f"""
    <style>
        .slider-container {{
            position: relative;
            width: 100%;
            overflow: hidden;
            padding: 10px 0;
        }}
        .slider {{
            display: flex;
            gap: 16px;
            transition: transform 0.3s ease;
            padding: 10px;
            scroll-behavior: smooth;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        .slider::-webkit-scrollbar {{
            display: none;
        }}
        .slide {{
            flex: 0 0 auto;
            width: 200px;
            height: 300px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 12px rgba(0,0,0,0.25);
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        .slide img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .slide:hover {{
            transform: scale(1.05);
        }}
        .arrow {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 32px;
            color: #333;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 50%;
            padding: 4px 12px;
            cursor: pointer;
            z-index: 10;
        }}
        .arrow.left {{
            left: 10px;
        }}
        .arrow.right {{
            right: 10px;
        }}
    </style>
    
    <div class="slider-container">
        <div class="arrow left" onclick="document.getElementById('slider').scrollBy({{left: -220, behavior: 'smooth'}})">&#10094;</div>
        <div class="slider" id="slider">
            {image_html}
        </div>
        <div class="arrow right" onclick="document.getElementById('slider').scrollBy({{left: 220, behavior: 'smooth'}})">&#10095;</div>
    </div>

    <script>
    function selectImage(url) {{
        const message = {{ type: 'SELECT_OUTFIT', url }};
        window.parent.postMessage(message, '*');
    }}
    </script>
    """

    components.html(html_code, height=360, scrolling=False)
    
# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def get_pexels_images(query, per_page=5):
    try:
        headers = {
            "Authorization": st.secrets["api"]["pexels_key"]
        }
        params = {
            "query": query,
            "per_page": per_page
        }
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return [photo["src"]["medium"] for photo in data.get("photos", [])]
    except:
        return []
    return []

def get_pixabay_images(query, per_page=5):
    try:
        params = {
            "key": st.secrets["api"]["pixabay_key"],
            "q": query,
            "image_type": "photo",
            "per_page": per_page
        }
        resp = requests.get("https://pixabay.com/api/", params=params)
        if resp.status_code == 200:
            data = resp.json()
            return [img["webformatURL"] for img in data.get("hits", [])]
    except:
        return []
    return []

def qloo_search_entity(name, entity_type="movie"):
    ENTITY_URN_TYPES = {
        "movie": "urn:entity:movie",
        "music": "urn:entity:artist",
        "genre": "urn:entity:genre"
    }

    headers = {
        "X-API-Key": QLOO_API_KEY
    }
    url = "https://hackathon.api.qloo.com/search"
    params = {
        "query": name.strip().title(),
        "types": ENTITY_URN_TYPES.get(entity_type, "urn:entity:movie")
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                return results[0].get("id")
            else:
                return None
        else:
            return None
    except Exception as e:
        return None


def get_qloo_recommendations(entity_urn):
    headers = {
        "X-API-Key": QLOO_API_KEY,
        "Content-Type": "application/json"
    }
    url = "https://hackathon.api.qloo.com/v1/insights/recommendations"
    payload = {
        "entities": [entity_urn],
        "type": "movie"
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            return [rec["name"].lower() for rec in data.get("results", [])]
        else:
            return []
    except Exception as e:
        return []

def get_style_tags_from_qloo(input_type, input_value, api_key, limit=5):
    endpoint_map = {
        "movie": "movies",
        "music": "music",
        "genre": "tags"
    }

    # Step 1: Search the entity
    entity_type = endpoint_map.get(input_type)
    if not entity_type:
        return []

    url = f"https://hackathon.api.qloo.com/v1/search"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "name": input_value,
        "limit": 1
    }
    search_response = requests.post(url, headers=headers, json=payload)

    if search_response.status_code != 200:
        return []

    entities = search_response.json().get("results", [])
    
    if not entities:
        return []

    entity = entities[0]
    entity_id = entity.get("entity_id")

    if not entity_id:
        return []

    # Step 2: Get related entities
    related_url = f"https://hackathon.api.qloo.com/v1/{entity_type}/related"
    payload = {
        "entity_id": entity_id,
        "limit": limit
    }

    related_response = requests.post(related_url, headers=headers, json=payload)
    if related_response.status_code != 200:
        return []

    related_entities = related_response.json().get("results", [])

    # Step 3: Extract and combine tags
    style_tags = set()
    for entity in related_entities:
        for tag in entity.get("tags", []):
            style_tags.add(tag.get("name"))

    return list(style_tags)


def get_qloo_related_styles(domain, name, limit=8):
    url = f"https://hackathon.api.qloo.com/v1/{domain}/related"
    headers = {
        "X-API-Key": QLOO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "name": name,
        "limit": limit
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            items = response.json().get("results", [])
            return [item["name"].lower() for item in items]
        else:
            return []
    except Exception as e:
        return []

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

@st.cache_data(ttl=0, show_spinner=False)
def get_outfit_images(q, per_page=5):
    # 1️⃣ Try Unsplash first
    try:
        page_num = random.randint(1, 5)
        random_suffix = random.randint(0, 10000)
        query = f"{q} {random_suffix}"

        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": query, "per_page": per_page, "page": page_num}
        )

        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                return results  # Keep Unsplash structure
    except:
        pass

    # 2️⃣ Fallback to Pexels
    fallback_images = get_pexels_images(q, per_page=per_page)
    if fallback_images:
        return [{"urls": {"regular": url}} for url in fallback_images]

    # 3️⃣ Fallback to Pixabay
    fallback_images = get_pixabay_images(q, per_page=per_page)
    if fallback_images:
        return [{"urls": {"regular": url}} for url in fallback_images]

    return []  # Final fallback


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
    
    country_info = response.get("results", {}).get(country_code, {})
    flatrate = country_info.get("flatrate", [])
    link = country_info.get("link", None)  # Generic landing page
    
    return flatrate, link


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

def detect_spotify_genre(song_name, token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": song_name, "type": "track", "limit": 1}

    resp = requests.get(search_url, headers=headers, params=params).json()
    tracks = resp.get("tracks", {}).get("items", [])

    if not tracks:
        return None, None  # No result

    track = tracks[0]
    artist_id = track["artists"][0]["id"]

    # Fetch artist details to get genre
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_resp = requests.get(artist_url, headers=headers).json()
    genres = artist_resp.get("genres", [])

    # Map Spotify genres to your defined keys
    mapped_genre = None
    for g in genres:
        for known_genre in music_to_tags.keys():
            if known_genre in g.lower():
                mapped_genre = known_genre
                break
        if mapped_genre:
            break

    return mapped_genre, track["name"] + " - " + track["artists"][0]["name"]

# -------------------------------------------------------------------
# Session State Setup
# -------------------------------------------------------------------
TAB_MEDIA   = "🎬 Media Style Match"
TAB_FASHION = "👗 Fashion & Brands"
TAB_FIT     = "🧍 Style View"

for key, default in [
    ("active_tab", TAB_MEDIA),
    ("archetypes", []),
    ("selected_style", None),
    ("ready_for_fashion", False),
    ("similar_movies", []),
    ("user_country", get_user_country()),
    ("movie_page", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# 🛠 Tab Navigation (Make sure this sets from session state)
tabs = [TAB_MEDIA, TAB_FASHION, TAB_FIT]
selected_tab = st.radio("Go to:", tabs,
    index=tabs.index(st.session_state.active_tab),
    horizontal=True,
    key="tab_selector"
)
# ✅ Only update session_state if the user clicks a different tab
if selected_tab != st.session_state.active_tab:
    st.session_state.active_tab = selected_tab
st.write("---")

if "ready_for_fashion" not in st.session_state:
    st.session_state.ready_for_fashion = False

if "similar_movies" not in st.session_state:
    st.session_state["similar_movies"] = []

if "user_country" not in st.session_state:
    st.session_state.user_country = get_user_country()

if "movie_page" not in st.session_state:
    st.session_state.movie_page = 1

# -------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------
st.set_page_config(page_title="AI StyleTwin", layout="wide")
st.title("🧠 AI StyleTwin")
st.caption("Discover your aesthetic twin in media and fashion.")

st.write("---")

# -------------------------------------------------------------------
# Media Style Match + Music Recommendations
# -------------------------------------------------------------------
if st.session_state.active_tab == TAB_MEDIA:
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
                media_name = movie_input if movie_input else selected_genre
                entity_urn = qloo_search_entity(media_name, entity_type="movie")
        
                qloo_styles = []
                used_fallback = False
        
                if entity_urn:
                    style_tags = get_style_tags_from_qloo("movie", media_name, QLOO_API_KEY)
                    if style_tags:
                        qloo_styles = style_tags
                    else:
                        used_fallback = True
                else:
                    used_fallback = True
        
                if used_fallback:
                    st.info("Attempted to use Qloo API. No valid styles found, falling back to TMDB/Spotify-based recommendation engine.")
                    qloo_styles = get_archetypes_from_media(movie=movie_input or selected_genre)
        
                if qloo_styles:
                    st.session_state.archetypes = qloo_styles
                    st.session_state.ready_for_fashion = True
        
                    if movie_input:
                        st.session_state.similar_movies = get_similar_movies(movie_input)
                    elif selected_genre:
                        st.session_state.similar_movies = get_movies_by_genre(selected_genre, st.session_state.user_country)
        
                    st.session_state.selected_style = None
                    st.session_state.movie_page = 1

        if st.session_state.similar_movies:
            st.markdown("### 🎬 You Might Also Like")
        
            # Pagination logic
            page_size = 5
            total = len(st.session_state.similar_movies)
            total_pages = (total + page_size - 1) // page_size
        
            # Display pagination buttons (1 2 3 ... →)
            st.markdown("""
            <style>
                button[kind="primary"] {
                    border-radius: 6px;
                    margin: 0 2px;
                    padding: 0.3em 0.8em;
                }
            </style>
            """, unsafe_allow_html=True)

            pagination_cols = st.columns(total_pages + 2)  # Add 2 for ← and →

            # "Previous" arrow
            if pagination_cols[0].button("←", key="prev_page"):
                if st.session_state.movie_page > 1:
                    st.session_state.movie_page -= 1
            
            # Page number buttons
            for i in range(total_pages):
                if pagination_cols[i + 1].button(str(i + 1), key=f"page_{i+1}"):
                    st.session_state.movie_page = i + 1
            
            # "Next" arrow
            if pagination_cols[-1].button("→", key="next_page"):
                if st.session_state.movie_page < total_pages:
                    st.session_state.movie_page += 1
            
            start_idx = (st.session_state.movie_page - 1) * page_size
            end_idx = start_idx + page_size
            current_movies = st.session_state.similar_movies[start_idx:end_idx]
        
            for m in current_movies:
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
                        providers, landing_link = get_streaming_platforms(movie_id, st.session_state.user_country)
                        if providers:
                            st.markdown("🌐 Available on:")
                            logos = st.columns(len(providers))
                            for i, p in enumerate(providers):
                                logo_url = f"https://image.tmdb.org/t/p/w45{p['logo_path']}" if p.get("logo_path") else None
                                provider_name = p.get("provider_name")
                                with logos[i]:
                                    if logo_url:
                                        if landing_link:
                                            st.markdown(
                                                f"<a href='{landing_link}' target='_blank'><img src='{logo_url}' width='40' title='{provider_name}'></a>",
                                                unsafe_allow_html=True
                                            )
                                        else:
                                            st.image(logo_url, width=40, caption=provider_name)
                                    else:
                                        st.markdown(f"**{provider_name}**")
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
                with st.spinner("🔍 Getting Spotify previews and fashion styles..."):
                    client_id = st.secrets["spotify"]["client_id"]
                    client_secret = st.secrets["spotify"]["client_secret"]
                    token = get_spotify_token(client_id, client_secret)
            
                    if not token:
                        st.error("Failed to retrieve Spotify token.")
                    else:
                        genre_key, display_song_name = detect_spotify_genre(song_input, token)
            
                        if not genre_key:
                            st.warning("Could not detect genre from Spotify.")
                            genre_key = None
                        
                        qloo_styles = get_qloo_related_styles("music", song_input, limit=6)
                        
                        if qloo_styles:
                            st.session_state.archetypes = qloo_styles
                            st.session_state.ready_for_fashion = True
                        else:
                            st.info("Attempted to use Qloo API. No valid styles found, falling back to TMDB/Spotify-based recommendation engine.")
                            fallback_styles = get_archetypes_from_media(music=genre_key)
                            if fallback_styles:
                                st.session_state.archetypes = fallback_styles
                                st.session_state.ready_for_fashion = True
                            else:
                                st.error("Could not detect any fashion styles.")
                                
                            # Optional: show Spotify previews
                            similar_tracks = get_similar_songs(song_input)
                            if similar_tracks:
                                spotify_enriched = []
                                for track in similar_tracks:
                                    enriched = get_spotify_song_data(f"{track['title']} {track['artist']}", token, limit=1)
                                    if enriched:
                                        spotify_enriched.append(enriched[0])
            
                                for song in spotify_enriched:
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

        
                                # 🎯 Auto-generate fashion archetypes from genre
                                st.session_state.archetypes = get_archetypes_from_media(music=genre_key)
                                st.session_state.ready_for_fashion = True

    
        if st.session_state.ready_for_fashion:
            st.markdown("---")
            st.markdown(f"**👗 Suggested fashion styles:** {', '.join(st.session_state.archetypes)}")

            #st.markdown("### 👗 Ready to explore fashion inspired by these vibes?")
            if st.button("Explore Fashion Recommendations"):
                st.session_state.active_tab = TAB_FASHION
                st.rerun()

# -------------------------------------------------------------------
# Fashion & Brands
# -------------------------------------------------------------------
elif st.session_state.active_tab == TAB_FASHION:
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
                    st.image(imgs[0]["urls"]["small"], use_container_width=True)
                else:
                    st.warning("No preview image found.")

                brands = style_to_brands.get(style, ["Coming soon…"])
                st.markdown("**🛍️ Brands:**<br>" + "<br>".join(
                    f"<a href='https://google.com/search?q={urllib.parse.quote_plus(b + ' clothing')}' target='_blank'>{b}</a>"
                    for b in brands
                ), unsafe_allow_html=True)

                if st.button(f"Try {style}", key=f"try_{style}"):
                    st.session_state.selected_style = style
                    st.session_state.selected_outfit_url = None  # User will pick this in fitting room
                    st.session_state.active_tab = TAB_FIT
                    st.rerun()

        if st.button("🔙 Back to Media Tab"):
            st.session_state.active_tab = TAB_MEDIA
            st.rerun()

# -------------------------------------------------------------------
# Style view
# -------------------------------------------------------------------
else:
    st.header("🧍 Style View")

    style = st.session_state.get("selected_style")

    if not style:
        st.warning("Please select a fashion style first in the Fashion & Brands tab.")
    else:
        st.success(f"Showing outfits for: **{style.title()}**")

        # Persistent Refresh Button
        refresh_col, _ = st.columns([1, 3])
        with refresh_col:
            if st.button("🔄 Refresh Outfits"):
                with st.spinner("Loading outfits..."):
                    st.session_state.fitting_room_outfits = get_outfit_images(style_search_terms[style], per_page=5)

        # Load outfits initially if not already loaded
        if "fitting_room_outfits" not in st.session_state:
            with st.spinner("Loading outfits..."):
                st.session_state.fitting_room_outfits = get_outfit_images(style_search_terms[style], per_page=10)

        outfit_urls = [img["urls"]["regular"] for img in st.session_state.get("fitting_room_outfits", [])]

        if outfit_urls:
            st.markdown("### 👗 Browse the looks below:")
            render_coverflow(outfit_urls)
        else:
            st.warning("No outfits found for this style.")

        if st.button("🔙 Back to Fashion Tab"):
            st.session_state.active_tab = TAB_FASHION
            st.rerun()
