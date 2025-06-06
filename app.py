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

col1, col2= st.columns(2)
with col1:
    ## Current Weather Display
    st.markdown("### Current NYC Weather")
    weather_url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": st.secrets['weather'],
              "q": "New York",
              "aqi": "no"} ##air quality index
    response_weather = requests.get(weather_url, params=params).json()
    icon = "https:"+response_weather['current']['condition']['icon']
    temp_c = response_weather['current']['temp_c']
    temp_f = response_weather['current']['temp_f']
    col1_bis, col2_bis, col3_bis = st.columns(3)
    with col1_bis:
        st.markdown(f"#### {temp_c}°C")
        st.markdown(f"#### {temp_f}°F")

    with col2_bis:
        st.image(icon)
        st.text(response_weather['current']['condition']['text'])

    with col3_bis:
        wind_mph = response_weather['current']['wind_mph']
        precip_in = response_weather['current']['precip_in']
        uv_index = round(response_weather['current']['uv'])
        st.text(f"Wind: {wind_mph} m/h")
        st.text(f"Precipitation: {precip_in} inches")
        st.text(f"UV Index: {uv_index}")


    ## Fare display
    st.markdown("### Fare Prediction")
    pickup = st.text_input("Where are you ?", placeholder="Manhattan")
    if pickup:
        pickup_latitude, pickup_longitude = get_lat_long(pickup)
    dropoff = st.text_input("Where do you want to go ?", placeholder="Brooklyn")
    if dropoff:
        dropoff_latitude, dropoff_longitude = get_lat_long(dropoff)
    passenger_count = st.number_input("How many are you ?", min_value = 1, max_value = 5,
                    step = 1, placeholder=1)


    url = "https://taxifare.lewagon.ai/predict"

    pickup_datetime = datetime.datetime.today()
    pickup_yesterday = datetime.datetime.today() - datetime.timedelta(days = 1)
    if pickup_longitude != None and dropoff_longitude != None:
        params_now = {"pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude":dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count}
        response_now = requests.get(url=url, params = params_now).json()
        fare_now = round(response_now['fare'],2)
        st.markdown(f"#### Predicted fare: {fare_now}$")
        params_yesterday = {"pickup_datetime": pickup_yesterday,
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude":dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count}

        if st.button("Compare with yesterday's price ?"):
            response_yesterday = requests.get(url=url, params = params_yesterday).json()
            fare_yesterday = round(response_yesterday['fare'], 2)
            if fare_yesterday < fare_now:
                st.markdown(f"That's {round(fare_now - fare_yesterday,2)}$ more expensive than yesterday!")
            else:
                st.markdown(f"That's {round(fare_now - fare_yesterday,2)}$ less expensive than yesterday!")




with col2:
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
