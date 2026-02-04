import streamlit as st
import pandas as pd
from yt_dlp import YoutubeDL
from io import BytesIO

st.set_page_config(page_title="YouTube Playlist Metadata Exporter", layout="centered")

st.title("📺 YouTube Playlist Metadata Exporter")
st.write("Export playlist info to Excel (.xlsx)")

playlist_url = st.text_input("Paste YouTube playlist URL")

filename = st.text_input("Output filename", value="playlist.xlsx")


def extract_metadata(url):
    rows = []

    ydl_opts = {
        "quiet": True,
        "skip_download": True,     # metadata only
        "extract_flat": True,      # fast + avoids 403 issues
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        entries = info.get("entries", [])

        for i, e in enumerate(entries, 1):
            rows.append({
                "No": i,
                "Title": e.get("title"),
                "URL": f"https://www.youtube.com/watch?v={e.get('id')}",
                "Channel": e.get("channel") or e.get("uploader"),
                "Duration_sec": e.get("duration"),
                "Upload_date": e.get("upload_date"),
                "Views": e.get("view_count"),
                "Likes": e.get("like_count"),
                "Comments": e.get("comment_count"),
            })

    return pd.DataFrame(rows)


if st.button("Extract Metadata"):
    if not playlist_url:
        st.warning("Please paste a playlist URL first.")
    else:
        with st.spinner("Extracting metadata..."):
            df = extract_metadata(playlist_url)

        st.success(f"{len(df)} videos found")

        st.dataframe(df)

        # Save to Excel in memory
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            label="⬇ Download Excel",
            data=buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
