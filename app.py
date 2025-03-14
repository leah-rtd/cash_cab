import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
import datetime

## Setting page configuration
st.set_page_config(page_title = "need a wagon?",
                   page_icon=":taxi:",
                   layout = "wide",
                   initial_sidebar_state="collapsed")

# Setting the map in the background

st.title(":taxi: need a wagon?:taxi:")

def get_lat_long(address):
    """
    Retrieve latitude and longitude from an address using Nomatim
    """
    nomatim_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address,
              "format": "json"}
    headers = {"User-Agent": "my-app"}
    response = requests.get(nomatim_url, params = params, headers=headers).json()
    return response[0]['lat'], response[0]['lon']


pickup_latitude = None
pickup_longitude = None
dropoff_latitude = None
dropoff_longitude = None
col1, col2, col3 = st.columns(3)
with col1:
    pickup = st.text_input("Where are you ?", placeholder="Manhattan")
    if pickup:
        pickup_latitude, pickup_longitude = get_lat_long(pickup)


with col2:
    dropoff = st.text_input("Where do you want to go ?", placeholder="Brooklyn")
    if dropoff:
        dropoff_latitude, dropoff_longitude = get_lat_long(dropoff)


with col3:
    passenger_count = st.number_input("How many are you ?", min_value = 1, max_value = 5,
                    step = 1, placeholder=1)

url = "https://taxifare.lewagon.ai/predict"

pickup_datetime = datetime.datetime.today()
if pickup_longitude != None and dropoff_longitude != None:
    params = {"pickup_datetime": pickup_datetime,
          "pickup_longitude": pickup_longitude,
          "pickup_latitude": pickup_latitude,
          "dropoff_longitude":dropoff_longitude,
          "dropoff_latitude": dropoff_latitude,
          "passenger_count": passenger_count}
    response = requests.get(url=url, params = params).json()
    fare = round(response['fare'],2)
    st.markdown(f"### {fare}$")

m = folium.Map(location=[ 40.708116, -73.957070], zoom_start=11)

# Add markers if valid coordinates are available
if pickup_latitude and pickup_longitude:
    folium.Marker([pickup_latitude, pickup_longitude], popup="Pickup", icon=folium.Icon(color="green")).add_to(m)

if dropoff_latitude and dropoff_longitude:
    folium.Marker([dropoff_latitude, dropoff_longitude], popup="Dropoff", icon=folium.Icon(color="red")).add_to(m)


if pickup_latitude and pickup_longitude and dropoff_latitude and dropoff_longitude:
    coordinates = [[float(pickup_latitude), float(pickup_longitude)],
                   [float(dropoff_latitude), float(dropoff_longitude)]]
    folium.PolyLine(locations= coordinates).add_to(m)


# Display Map
st.markdown(
    """
    <style>
        iframe {
            width: 90vw !important;  /* Set map width */
            height: 70vh !important; /* Set map height */
        }
    </style>
    """,
    unsafe_allow_html=True
)
folium_static(m)



st.markdown(
    f"""
    <style>
        .footer {{
                        position: fixed;
            bottom: 10px;
            right: 20px;  /* Moves it slightly left so it's visible */
            background-color: #f1f1f1;
            padding: 10px 20px;
            font-size: 14px;
            color: black;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);

        }}
        .footer img {{
            border-radius: 50%;
            width: 30px;
            height: 30px;
            vertical-align: middle;
            margin-right: 5px;
        }}
    </style>
    <div class="footer">
        Designed by
        <a href="https://github.com/leah-rtd" target="_blank">
            <img src="https://github.com/leah-rtd.png" alt="GitHub Profile Picture">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
