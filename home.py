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
# Setting the map in the background


@st.cache_data(ttl=3600)
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


@st.cache_data(ttl=600)
def get_weather_data():
    """
    Get Current Weather for NYC
    """
    weather_url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": st.secrets['weather'],
              "q": "New York",
              "aqi": "no"} ##air quality index

    response_weather = requests.get(weather_url, params=params).json()

    return response_weather

@st.cache_data(ttl=1800)
def get_fare_prediction(pickup_datetime, pickup_longitude, pickup_latitude,
                       dropoff_longitude, dropoff_latitude, passenger_count):
    """
    Get fare prediction from our API
    """
    url = "https://taxifare.lewagon.ai/predict"
    params = {"pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude":dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count}
    response = requests.get(url, params=params).json()
    return response['fare']

@st.cache_data(ttl=1800)
def get_30_day_fare_prediction(pickup_datetime, pickup_longitude, pickup_latitude,
                       dropoff_longitude, dropoff_latitude, passenger_count):
    pickups = [(datetime.datetime.today() - datetime.timedelta(days = day)) for day in range(31)]
    res = {"Dates": [], "Fare Amount ($)": []}
    for pickup in pickups:
        res['Dates'].append(pickup.strftime(format = "%d-%m-%Y"))
        res['Fare Amount ($)'].append(get_fare_prediction(pickup, pickup_longitude, pickup_latitude,
                                               dropoff_longitude, dropoff_latitude,
                                               passenger_count))
        time.sleep(np.random.uniform(0,0.5))

    return pd.DataFrame(res).set_index("Dates").sort_index()



# Initialize session state variables
if 'pickup' not in st.session_state:
    st.session_state['pickup'] = None
if 'dropoff' not in st.session_state:
    st.session_state['dropoff'] = None
# if "pickup_latitude" not in st.session_state:
#     st.session_state['pickup_latitude'] = None
# if "pickup_longitude" not in st.session_state:
#     st.session_state['pickup_longitude'] = None
# if "dropoff_latitude" not in st.session_state:
#     st.session_state['dropoff_latitude'] = None
# if "dropoff_longitude" not in st.session_state:
#     st.session_state['dropoff_longitude'] = None
pickup_latitude = None
pickup_longitude = None
dropoff_latitude = None
dropoff_longitude = None

if "fare_now" not in st.session_state:
    st.session_state["fare_now"] = None


header_1,_, header_2 = st.columns([2,1,3], vertical_alignment="center")
with header_1:
    st.title(":taxi: need a wagon?:taxi:")


with header_2:
    # Weather information

    with st.container(border = True, height = 300):

        response_weather = get_weather_data()
        temp_c = response_weather['current']['temp_c']
        temp_f = response_weather['current']['temp_f']

        wind_mph = response_weather['current']['wind_mph']
        precip_in = response_weather['current']['precip_in'] # not using this one but why not add it one day
        uv_index = round(response_weather['current']['uv'])



        title, icon_bar, description = st.columns([3,1,1])
        title.markdown("#### Current NYC Weather")
        icon = "https:"+response_weather['current']['condition']['icon']
        icon_bar.image(icon)
        description.markdown("")
        description.markdown(response_weather['current']['condition']['text'])

        a,b = st.columns(2)
        c,d = st.columns(2)
        st.markdown("""
            <style>
            [data-testid="stMetricValue"] {
                font-size: 1.2rem;
            }
            [data-testid="stMetricLabel"] {
                font-size: 0.8rem;
            }
            </style>
            """, unsafe_allow_html=True)
        a.metric("Temp °C", temp_c, border=True)
        b.metric("Temp °F", temp_f, border=True)

        c.metric("Wind", f"{wind_mph} m/h", border=True)
        d.metric("UV Index", f"{uv_index}", border=True)


        # with col2_bis:






col1, col2= st.columns(2)
with col1:


    ## Fare display
    st.markdown("### Fare Prediction")
    with st.container(border = True):
        with st.form("details", border = False, enter_to_submit=False):
            pickup = st.text_input("Where are you ?", placeholder="Manhattan")
            if pickup:
                pickup_latitude, pickup_longitude = get_lat_long(pickup)
                st.session_state['pickup'] = (pickup_latitude, pickup_longitude)
            dropoff = st.text_input("Where do you want to go ?", placeholder="Brooklyn")
            if dropoff:
                dropoff_latitude, dropoff_longitude = get_lat_long(dropoff)
                st.session_state['dropoff'] = (dropoff_latitude, dropoff_longitude)
            passenger_count = st.number_input("How many are you ?", min_value = 1, max_value = 5,
                            step = 1, placeholder=1)
            submitted = st.form_submit_button("Get Fare")
            if submitted:
                if pickup_longitude != None and dropoff_longitude != None:
                    pickup_datetime = datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")
                    st.session_state.fare_now = round(get_fare_prediction(pickup_datetime=pickup_datetime,
                                pickup_longitude=pickup_longitude, pickup_latitude=pickup_latitude,
                                dropoff_longitude=dropoff_longitude, dropoff_latitude=dropoff_latitude,
                                passenger_count=passenger_count), 2)
                    st.markdown(f"#### Predicted fare: {st.session_state.fare_now}$")



with col2:


    # Build points data dynamically
    points = []
    if st.session_state['pickup']:
        points.append({
            "lat": float(st.session_state['pickup'][0]),
            "lon": float(st.session_state['pickup'][1]),
            "type": "Pickup"
        })

    if st.session_state['dropoff']:
        points.append({
            "lat": float(st.session_state['dropoff'][0]),
            "lon": float(st.session_state['dropoff'][1]),
            "type": "Dropoff"
        })

    points_data = pd.DataFrame(points)

    # Build Layers
    layers = []
    if not points_data.empty:
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=points_data,
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 255]',
            get_radius=200,
            pickable=True
        )
        layers.append(point_layer)

    # Add line if both pickup & dropoff are present
    if st.session_state['pickup'] and st.session_state['dropoff']:
        line_data = pd.DataFrame([{
            "path": [
                [st.session_state['pickup'][1], st.session_state['pickup'][0]],
                [st.session_state['dropoff'][1], st.session_state['dropoff'][0]]
            ]
        }])

        line_layer = pdk.Layer(
            "PathLayer",
            data=line_data,
            get_path="path",
            get_color=[0, 0, 255, 255],
            width_scale=20,
            width_min_pixels=2
        )
        layers.append(line_layer)

    # Center View
    if points:
        avg_lat = sum(float(p['lat']) for p in points) / len(points)
        avg_lon = sum(float(p['lon']) for p in points) / len(points)
    else:
        avg_lat, avg_lon = 40.7128, -74.0060  # Default to NYC

    view_state = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=10)

    # Render Map
    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={"text": "{type}"},
        height = 150
    ))

st.markdown(f'#### 30 Day Price Comparison for rides at {datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M %p")}')
button = st.button("Get Comparison")
if button and st.session_state['fare_now'] != None:
    pickup_datetime = datetime.datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")

    df_fares = get_30_day_fare_prediction(pickup_datetime=pickup_datetime,
                            pickup_latitude=st.session_state['pickup'][0], pickup_longitude=st.session_state['pickup'][1],
                            dropoff_latitude=st.session_state['dropoff'][0], dropoff_longitude=st.session_state['dropoff'][1],
                            passenger_count=passenger_count)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x = df_fares.index,
            y = df_fares['Fare Amount ($)'],
            mode = 'lines+markers',
            marker = dict(size = 8, color = "#ffc25a"),
            line = dict(color = "#6AE7FF", width = 2),
            showlegend=False,
            hovertext= df_fares.reset_index().apply(lambda row: f"Fare Amout ($): {round(row['Fare Amount ($)'],2)}\nDate {row['Dates']}", axis = 1),
            hovertemplate='%{hovertext}<extra></extra>'
        ))
        ## ymin fill
    min_fill = df_fares['Fare Amount ($)'].min()

    fig.add_trace(go.Scatter(
            x = df_fares.index,
            y = [min_fill] * len(df_fares),
            mode = "lines",
            fill= "tonexty",
            line = dict(color = "lightblue", width = 0),
            showlegend= False,
            hoverinfo="skip"
        ))
    fig.update_layout(xaxis=dict(showgrid = False, tickangle=45),
                          yaxis= dict(showgrid=True, gridcolor="lightgrey"))
    st.plotly_chart(fig)

elif button:
    st.write("Please input information")
