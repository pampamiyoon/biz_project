# streamlit_app.py
"""JPOP Random Recommendation Streamlit App

This app loads song data from `songs.json` and provides random recommendations
organized into five thematic categories:
1. love – 사랑하고 싶을 때 듣는 노래
2. night – 밤에 혼자 듣는 노래
3. city – 도시 밤거리 느낌의 노래
4. upbeat – 기분 올리고 싶을 때 듣는 노래
5. complex – 마음이 복잡할 때 듣는 노래

Features:
- Dark‑mode gradient background with glass‑morphism cards.
- Sidebar to select a category and a button to fetch a random song.
- "Surprise Me" button that picks a random song from any category.
- Displays album cover image and clickable YouTube link.
- Custom CSS injected via `st.markdown` for modern aesthetics.
"""

import json
import random
from pathlib import Path

import streamlit as st

# ------------------------------------------------------------
# Load song data
# ------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "songs.json"
with DATA_PATH.open(encoding="utf-8") as f:
    SONGS = json.load(f)

# Helper to persist changes
def save_songs():
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(SONGS, f, ensure_ascii=False, indent=2)

# Dynamically generate category display names from SONGS keys
# If you want custom Korean labels, extend this mapping as needed.
DEFAULT_LABELS = {
    "love": "사랑하고 싶을 때 듣는 노래",
    "night": "밤에 혼자 듣는 노래",
    "city": "도시 밤거리 느낌의 노래",
    "upbeat": "기분 올리고 싶을 때 듣는 노래",
    "complex": "마음이 복잡할 때 듣는 노래",
}
CATEGORIES = {key: DEFAULT_LABELS.get(key, key) for key in SONGS.keys()}

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def get_random_song(category: str) -> dict:
    """Return a random song dict from the given category."""
    return random.choice(SONGS.get(category, []))

def resolve_image_path(image_ref: str) -> Path:
    """Convert the JSON image reference (e.g. "./data/1.jpg") to an absolute Path.
    The reference may start with "./" – we strip it and resolve relative to the project root.
    """
    clean = image_ref.lstrip("./")
    return Path(__file__).parent / clean

# ------------------------------------------------------------
# Custom CSS for dark gradient and glass‑morphism cards
# ------------------------------------------------------------
CUSTOM_CSS = """
<style>
    html, body, [class*=stApp] {
        background: #ffffff;
        color: #000000;
    }
    .card {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 30px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    }
    a { color: #90caf9; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# UI Layout
# ------------------------------------------------------------
# UI Layout
st.title("🎶 J‑POP 랜덤 추천")
st.caption("무드를 선택하고 앨범 이미지와 YouTube 링크가 포함된 곡을 확인하세요.")

# Category selection (interactive random recommendation)
st.subheader("카테고리 선택")
selected_category = st.selectbox(
    "Category",
    list(CATEGORIES.keys()),
    format_func=lambda x: CATEGORIES[x],
)

if st.button("랜덤 곡"):
    st.session_state["song"] = get_random_song(selected_category)

# Display the chosen song if any
song = st.session_state.get("song")
if song:
    st.markdown(f"### {song['title']} - {song['artist']}")
    img_path = resolve_image_path(song["image"])
    if img_path.is_file():
        st.image(str(img_path), width=500)
    else:
        st.warning("Album image not found.")
    st.markdown(f"[▶️ Watch on YouTube]({song['url']})")
    st.markdown("---")
else:
    st.info("카테고리를 선택하고 **랜덤 곡** 버튼을 눌러 추천을 받아보세요.")

# ------------------------------------------------------------
# Section: Add new category
# ------------------------------------------------------------
st.subheader("새 카테고리 추가")
new_category = st.text_input("카테고리 키 (영문 소문자)")
if st.button("카테고리 추가"):
    if new_category and new_category not in SONGS:
        SONGS[new_category] = []
        # Persist changes
        save_songs()
        # Refresh categories mapping
        CATEGORIES = {key: DEFAULT_LABELS.get(key, key) for key in SONGS.keys()}
        st.success(f"카테고리 '{new_category}' 추가되었습니다.")
        st.experimental_rerun()
    else:
        st.warning("유효한 카테고리 키를 입력하거나, 이미 존재하는 카테고리는 추가할 수 없습니다.")

# ------------------------------------------------------------
# Section: Add new song & Delete song (side‑by‑side)
# ------------------------------------------------------------
col_add, col_del = st.columns(2)

# ----- 왼쪽: 새 노래 추가 -----
with col_add:
    with st.expander("새 노래 추가"):
        add_category = st.selectbox(
            "노래를 추가할 카테고리",
            list(SONGS.keys()),
            format_func=lambda x: CATEGORIES.get(x, x),
        )
        title = st.text_input("제목")
        artist = st.text_input("아티스트")
        image_path = st.text_input("이미지 경로 (예: ./data/xxx.jpg)")
        youtube_url = st.text_input("YouTube URL")
        description = st.text_area("설명 (선택)")
        if st.button("노래 추가"):
            if title and artist and image_path and youtube_url:
                new_song = {
                    "id": f"{add_category}{len(SONGS[add_category]) + 1}",
                    "title": title,
                    "artist": artist,
                    "image": image_path,
                    "url": youtube_url,
                    "description": description,
                }
                SONGS[add_category].append(new_song)
                save_songs()
                st.success(f"'{title}' 이(가) 카테고리 '{add_category}'에 추가되었습니다.")
                st.experimental_rerun()
            else:
                st.warning("모든 필수 입력란을 채워 주세요.")

# ----- 오른쪽: 노래 삭제 -----
with col_del:
    with st.expander("노래 삭제"):
        del_category = st.selectbox(
            "삭제할 카테고리",
            list(SONGS.keys()),
            format_func=lambda x: CATEGORIES.get(x, x),
            key="del_category",
        )
        if SONGS.get(del_category):
            del_song_title = st.selectbox(
                "삭제할 노래",
                [song["title"] for song in SONGS[del_category]],
                key="del_song",
            )
            if st.button("노래 삭제"):
                song_to_remove = next(
                    (s for s in SONGS[del_category] if s["title"] == del_song_title), None
                )
                if song_to_remove:
                    SONGS[del_category].remove(song_to_remove)
                    save_songs()
                    st.success(f"'{del_song_title}' 이(가) 카테고리 '{del_category}'에서 삭제되었습니다.")
                    st.experimental_rerun()
                else:
                    st.warning("선택한 노래를 찾을 수 없습니다.")





