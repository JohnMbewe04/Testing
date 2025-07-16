import streamlit as st
import requests
import urllib.parse

# -------------------------------------------------------------------
# Secrets & API Keys
# -------------------------------------------------------------------
QLOO_API_KEY        = st.secrets["api"]["qloo_key"]
TMDB_API_KEY        = st.secrets["api"]["tmdb_key"]
UNSPLASH_ACCESS_KEY = st.secrets["api"]["unsplash_key"]

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
        "normcore": "normcore fashion",
    "utilitarian": "utilitarian outfit",
    "alt": "alt fashion look",
    "emo": "emo aesthetic outfit",
    "softcore": "softcore aesthetic clothes",
    "cozy": "cozy aesthetic fashion",
    "eclectic": "eclectic fashion look",
    "biker": "biker outfit aesthetic",
    "scandi": "scandi fashion",
    "y2k": "y2k fashion",
    "artcore": "artcore fashion",
    "experimental": "experimental outfit",
    "conceptual": "conceptual fashion"
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
#  Helpers
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


# -------------------------------------------------------------------
#  Session‐State “Tabs” Setup
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

# -------------------------------------------------------------------
#  Layout & Navigation
# -------------------------------------------------------------------
st.set_page_config(page_title="AI StyleTwin", layout="wide")
st.title("🧠 AI StyleTwin")
st.caption("Discover your aesthetic twin in media and fashion.")

# top‐of‐page “tabs” as a radio menu
choice = st.radio(
    "Go to:",
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
    st.header("🎥 Media Style Match")
    st.markdown("Tell me a movie, genre, or music and I'll find your fashion twin.")

    movie_input    = st.text_input("Enter a movie title:")
    selected_genre = st.selectbox("…or pick a genre:", [""] + genre_options)
    music_input    = st.text_input("…or enter a music genre:")

    if st.button("Get Recommendations"):
        st.session_state.archetypes = get_archetypes_from_media(
            movie=movie_input or None,
            genre=selected_genre or None,
            music=music_input or None
        )
        st.session_state.selected_style = None
        st.session_state.active_tab = TAB_FASHION

        # try rerunning to pick up the new tab
        try:
            st.experimental_rerun()
        except AttributeError:
            st.info("Please click on the 'Fashion & Brands' tab above.")

# -------------------------------------------------------------------
#  👗 Tab 2: Fashion & Brands
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
                q = style_search_terms.get(style, f"{style} outfit")
                imgs = get_outfit_images(q, per_page=1)
                if imgs:
                    st.image(imgs[0]["urls"]["small"], use_column_width=True)
                else:
                    st.warning("No preview image found.")

                brands = style_to_brands.get(style, ["Coming soon…"])
                links = ", ".join(
                    f"[🔸 {b}](https://google.com/search?q={urllib.parse.quote_plus(b+' clothing')})"
                    for b in brands
                )
                st.markdown("**🛍️ Brands:**<br>" + "<br>".join(
                    f"<a href='https://google.com/search?q={urllib.parse.quote_plus(b + ' clothing')}' target='_blank'>{b}</a>"
                    for b in brands
                ), unsafe_allow_html=True)

                if st.button(f"Try {style}", key=f"try_{style}"):
                    st.session_state.selected_style = style
                    st.session_state.active_tab = TAB_FIT
                    try:
                        st.experimental_rerun()
                    except AttributeError:
                        st.info("Please click on the 'AI Fitting Room' tab above.")


# -------------------------------------------------------------------
#  🧍 AI Fitting Room
# -------------------------------------------------------------------
else:
    st.header("🧍 Virtual Fitting Room")
    style = st.session_state.selected_style

    if not style:
        st.warning("First, pick a look in the Fashion tab.")
    else:
        st.success(f"Fitting Room – {style.title()} Look")

        # allow user to snap or upload a photo
        selfie = st.camera_input("📸 Take a selfie") or st.file_uploader("…or upload an image")
        if selfie:
            st.image(selfie, caption="You", width=200)

            outfits = get_outfit_images(style_search_terms[style], per_page=4)
            cols = st.columns(2)
            for i, o in enumerate(outfits):
                with cols[i % 2]:
                    st.image(o["urls"]["small"], caption=f"{style.title()} #{i+1}", use_column_width=True)
