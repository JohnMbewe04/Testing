import streamlit as st
import requests
import urllib.parse
import base64
from urllib.parse import parse_qs
import streamlit.components.v1 as components
import random
from streamlit_lottie import st_lottie
import json
import time
import streamlit_js_eval
import streamlit.components.v1 as components
from PIL import Image
from io import BytesIO
from rembg import remove
import numpy as np
import cv2
import io

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

def mock_try_on_cleaned(user_image, outfit_image):
    try:
        # Remove backgrounds
        user_no_bg = Image.open(io.BytesIO(remove(user_image.getvalue()))).convert("RGBA")
        outfit_no_bg = Image.open(io.BytesIO(remove(requests.get(outfit_image).content))).convert("RGBA")

        # Resize outfit relative to user image
        user_width, user_height = user_no_bg.size
        outfit_width = int(user_width * 0.6)
        outfit_height = int(outfit_width * outfit_no_bg.height / outfit_no_bg.width)
        outfit_resized = outfit_no_bg.resize((outfit_width, outfit_height))

        # Create a white background
        background = Image.new("RGBA", user_no_bg.size, (255, 255, 255, 255))
        background.paste(user_no_bg, (0, 0), user_no_bg)

        # Place outfit roughly centered on the user chest
        x_pos = int((user_width - outfit_width) / 2)
        y_pos = int(user_height * 0.35)
        background.paste(outfit_resized, (x_pos, y_pos), outfit_resized)

        return background.convert("RGB")  # Final image without alpha

    except Exception as e:
        st.error(f"Mock try-on failed: {e}")
        return None

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
    image_html = ''.join(f'<div class="slide"><img src="{url}"></div>' for url in images)

    js_code = f"""
    <script>
    const slider = document.getElementById('slider');
    let currentIndex = 0;

    function updateIndex() {{
        const scrollLeft = slider.scrollLeft;
        const slideWidth = 220;  // 200px + 20px gap
        currentIndex = Math.round(scrollLeft / slideWidth);
        window.parent.postMessage({{ type: "INDEX_UPDATE", index: currentIndex }}, "*");
    }}

    slider.addEventListener('scroll', () => {{
        clearTimeout(window.scrollTimeout);
        window.scrollTimeout = setTimeout(updateIndex, 150);
    }});

    window.onload = updateIndex;
    </script>
    """

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
    </style>

    <div class="slider-container">
        <div class="slider" id="slider">
            {image_html}
        </div>
    </div>
    {js_code}
    """

    components.html(html_code, height=350, scrolling=False)



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

@st.cache_data(ttl=0, show_spinner=False)
def get_outfit_images(q, per_page=8):
    # Add random query param and page number to fetch different results
    random_suffix = random.randint(0, 10000)
    page_num = random.randint(1, 5)

    query = f"{q} {random_suffix}"  # Add randomness to query
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        params={
            "query": query,
            "per_page": per_page,
            "page": page_num
        }
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
TAB_FIT     = "🧍 AI Fitting Room"

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
                with st.spinner("🔍 Getting Spotify previews..."):
                    client_id = st.secrets["spotify"]["client_id"]
                    client_secret = st.secrets["spotify"]["client_secret"]
                    token = get_spotify_token(client_id, client_secret)
        
                    if not token:
                        st.error("Failed to retrieve Spotify token.")
                    else:
                        genre_key, display_song_name = detect_spotify_genre(song_input, token)
        
                        if not genre_key:
                            st.error("Could not detect genre or no genre match found.")
                        else:
                            st.success(f"Detected genre: **{genre_key.title()}**")
        
                            similar_tracks = get_similar_songs(song_input)
                            if not similar_tracks:
                                st.error("No similar tracks found.")
                            else:
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
        selected_outfit_url = st.session_state.get("selected_outfit_url")  # store this when user clicks an outfit

        if selected_outfit_url:
            st.markdown("### 🧥 Selected Outfit")
            st.image(selected_outfit_url, width=200)

        if selfie and selected_outfit_url:
            if st.button("👕 Try it on (Mock)!"):
                with st.spinner("Preparing your mock try-on..."):
                    output_img = mock_try_on_cleaned(selfie, selected_outfit_url)
                if output_img:
                    st.image(output_img, caption="✨ Your Virtual Mock Try-On", use_column_width=True)
        if selfie:
            st.image(selfie, caption="You", width=200)
    
            # Initialize outfits in session if not already loaded or if user requests refresh
            if "fitting_room_outfits" not in st.session_state:
                with st.spinner("Loading style options..."):
                    st.session_state.fitting_room_outfits = get_outfit_images(style_search_terms[style], per_page=8)
    
            # Button to refresh outfits
            if st.button("🔄 Refresh Outfits"):
                # Show Lottie animation while fetching
                with st.spinner("Fetching new styles..."):
                    anim = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_puciaact.json")
                    if anim:
                        st_lottie(anim, height=200, speed=1.2, loop=True)

                    # Optional: Delay just to show animation before refresh
                    time.sleep(2)
            
                    # Force refresh outfits
                    st.session_state.outfit_refresh_key = random.randint(1, 10000)
                    st.rerun()

            if st.session_state.fitting_room_outfits:
                st.markdown("### 👚 Browse Outfit Options:")
            
                # Get list of image URLs
                outfit_urls = [o["urls"]["regular"] for o in st.session_state.fitting_room_outfits]
                
                # Render horizontal scrollable coverflow
                render_coverflow(outfit_urls)
            
                # JavaScript: Get current center index (frontmost image)
                components.html("""
                    <script>
                    const slider = window.parent.document.querySelector('.slider');
                    if (slider) {
                        slider.addEventListener('scroll', () => {
                            const slideWidth = 220;
                            const index = Math.round(slider.scrollLeft / slideWidth);
                            window.parent.postMessage({ type: "CENTER_INDEX", index: index }, "*");
                        });
                    }
                    </script>
                """, height=0)
            
                # Receive the index from JS — fallback to 0
                selected_index = st.session_state.get("coverflow_index", 0)
            
                # Manual override (simulate update from JS since we can't truly sync it in time)
                selected_index = st.slider("Browse outfits", 0, len(outfit_urls)-1, selected_index, key="coverflow_slider")
            
                if st.button("✅ Select This Outfit"):
                    st.session_state.selected_outfit_url = outfit_urls[selected_index]
                    st.success(f"Selected outfit #{selected_index+1}")
                    st.rerun()

            else:
                st.warning("No outfit images found.")

        if st.button("🔙 Back to Fashion Tab"):
            st.session_state.active_tab = TAB_FASHION
            st.rerun()
