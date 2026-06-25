import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
PERSIST_DIRECTORY = "./chroma_db"
PDF_FILE_PATH = "gsbcookbook.pdf"

if not GOOGLE_API_KEY:
    st.error("❌ Missing GOOGLE_API_KEY in the environment setup.")
    st.stop()