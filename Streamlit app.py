import streamlit as st
import requests
import urllib.parse

# -------------------------------------------------------------------
#  Secrets & API Keys
# -------------------------------------------------------------------
QLOO_API_KEY        = st.secrets["api"]["qloo_key"]
TMDB_API_KEY        = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]

# -------------------------------------------------------------------
#  Mappings & Search Terms
# -------------------------------------------------------------------
genre_options = ["comedy", "horror", "romance", "action", "animation", "crime", "sci-fi", "drama"]

style_search_terms = {
    # your existing style→Unsplash queries
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
    "preppy":      "preppy outfit aesthetic"
}

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
    "pop":        ["quirky", "whimsical"],
    "rock":       ["gritty", "rebellious"],
    "electronic": ["futuristic", "edgy"],
    "jazz":       ["elegant", "nostalgic"],
    "classical":  ["elegant", "minimalist"],
    "hip-hop":    ["streetwear", "edgy"]
}

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

# -------------------------------------------------------------------
#  Helper Functions
# -------------------------------------------------------------------

def get_archetypes_from_media(movie=None, genre=None, music=None):
    raw_tags = []
    if movie:
        # fetch TMDb genres
        res = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": movie}
        ).json().get("results", [])
        if res:
            id2name = {
                28:"action",35:"comedy",18:"drama",10749:"romance",
                27:"horror",16:"animation",878:"sci-fi",80:"crime"
            }
            g_ids = res[0].get("genre_ids", [])
            for gid in g_ids:
                raw_tags += genre_to_tags.get(id2name.get(gid,""), [])
    elif genre:
        raw_tags = genre_to_tags.get(genre.lower(), [])
    elif music:
        raw_tags = music_to_tags.get(music.lower(), [])

    archetypes = set()
    for tag in raw_tags:
        for stl in tag_to_style.get(tag, []):
            archetypes.add(stl)
    return list(archetypes)


@st.cache_data(ttl=600)
def get_outfit_images(style_query, per_page=4):
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization":f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        params={"query": style_query, "per_page": per_page}
    )
    return resp.json().get("results", [])


@st.cache_data(show_spinner=False)
def check_image(url):
    try:
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False


def get_tmdb_details(name, tmdb_id=None):
    detail = None
    if tmdb_id:
        detail = requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY,"language":"en-US"}
        ).json()
        if detail.get("status_code")==34:
            detail = None
    if not detail:
        results = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY,"query":name}
        ).json().get("results",[])
        detail = results[0] if results else {}
    title = detail.get("title", name)
    poster = detail.get("poster_path")
    overview = detail.get("overview","")
    poster_url = f"https://image.tmdb.org/t/p/w200{poster}" if poster else None
    return title, poster_url, overview


def get_user_country():
    try:
        return requests.get("https://ipinfo.io").json().get("country","US")
    except:
        return "US"


# -------------------------------------------------------------------
#  Session State & “Tabs” Setup
# -------------------------------------------------------------------
TAB_MEDIA   = "🎬 Media Style Match"
TAB_FASHION = "👗 Fashion & Brands"
TAB_FIT     = "🧍 AI Fitting Room"

if "active_tab" not in st.session_state:
    st.session_state.active_tab = TAB_MEDIA
if "archetypes" not in st.session_state:
    st.session_state.archetypes = []
if "selected_style" not in st.session_state:
    st.session_state.selected_style = None

# -------------------------------------------------------------------
#  Page Layout & Navigation
# -------------------------------------------------------------------
st.set_page_config(page_title="AI StyleTwin", layout="wide")
st.title("🧠 AI StyleTwin")
st.caption("Discover your aesthetic twin in media and fashion.")

# Render our “tabs” as a radio bar
choice = st.radio(
    "Navigate:",
    [TAB_MEDIA, TAB_FASHION, TAB_FIT],
    index=[TAB_MEDIA, TAB_FASHION, TAB_FIT].index(st.session_state.active_tab),
    horizontal=True
)
st.session_state.active_tab = choice
st.write("---")

# -------------------------------------------------------------------
#  🎬 Tab 1: Media Style Match
# -------------------------------------------------------------------
if choice == TAB_MEDIA:
    st.header("🎥 Movie & Song Recommendations")
    st.markdown("Input your favorite movie, genre, or music to find your style twin.")

    movie_input    = st.text_input("🎬 Enter a movie title:")
    selected_genre = st.selectbox("…or pick a genre:", [""] + genre_options)

    if st.button("Get Recommendations"):
        # compute archetypes from media
        st.session_state.archetypes = get_archetypes_from_media(
            movie=movie_input or None,
            genre=selected_genre or None
        )
        st.session_state.selected_style = None
        # advance to Fashion tab
        st.session_state.active_tab = TAB_FASHION
        st.experimental_rerun()

# -------------------------------------------------------------------
#  👗 Tab 2: Fashion & Brands
# -------------------------------------------------------------------
elif choice == TAB_FASHION:
    st.header("👚 Clothing & Brand Recommendations")
    if not st.session_state.archetypes:
        st.info("Run “Get Recommendations” in the Media tab first.")
    else:
        styles = st.session_state.archetypes
        st.success(f"Found these fashion archetypes: {', '.join(styles)}")

        cols = st.columns(2)
        for idx, style in enumerate(styles):
            with cols[idx % 2]:
                st.markdown(f"### 👗 {style.title()} Look")

                # show an Unsplash preview
                q = style_search_terms.get(style, f"{style} outfit")
                imgs = get_outfit_images(q, per_page=1)
                if imgs:
                    st.image(imgs[0]["urls"]["small"], use_column_width=True)
                else:
                    st.warning("No preview image found.")

                # suggested brands with Google search links
                brands = style_to_brands.get(style, ["Coming soon…"])
                brand_links = ", ".join(
                    f"[🔸 {b}](https://google.com/search?q={urllib.parse.quote_plus(b + ' clothing')})"
                    for b in brands
                )
                st.markdown("**🛍️ Brands:** " + brand_links)

                # “Try in Fitting Room” button
                if st.button(f"Try {style}", key=f"try_{style}"):
                    st.session_state.selected_style = style
                    st.session_state.active_tab = TAB_FIT
                    st.experimental_rerun()

# -------------------------------------------------------------------
#  🧍 AI Fitting Room
# -------------------------------------------------------------------
else:
    st.header("🧍 Virtual Fitting Room")
    style = st.session_state.selected_style
    if not style:
        st.warning("Pick a look in the Fashion tab first.")
    else:
        st.success(f"Fitting Room – {style.title()} Look")

        # let user take or upload a selfie
        selfie = st.camera_input("📸 Take a photo") or st.file_uploader("…or upload an image")
        if selfie:
            st.image(selfie, caption="Your photo", width=200)

            # display multiple outfit options
            outfits = get_outfit_images(style_search_terms[style], per_page=4)
            cols = st.columns(2)
            for i, outfit in enumerate(outfits):
                with cols[i % 2]:
                    st.image(outfit["urls"]["small"], caption=f"{style.title()} #{i+1}", use_column_width=True)
