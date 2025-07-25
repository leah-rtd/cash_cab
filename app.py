import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import plotly.graph_objects as go
import time
import numpy as np
from zoneinfo import ZoneInfo
import pydeck as pdk
from pathlib import Path

## Setting page configuration
st.set_page_config(page_title = "need a wagon?",
                   page_icon=":taxi:",
                   layout = "wide",
                   initial_sidebar_state="collapsed")
## Setting Page structure
about_page = st.Page(page = Path("about.py"), title = "About the Project",
                     icon = "ℹ️")
home_page = st.Page(page=Path("home.py"), title = "Home", icon = "🏠", default=True)
pg = st.navigation([home_page, about_page])


pg.run()
