import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import random
import requests
from datetime import datetime

# Your travel data
travel_data = {
    "Destination": ["Paris", "Tokyo", "Bali", "Rome", "New York"],
    "Type": ["City", "City", "Beach", "Historical", "City"],
    "Budget": [3, 4, 2, 3, 4],
    "Best_Season": ["Spring", "Fall", "Summer", "Spring", "Fall"],
    "Description": [
        "Romantic city with museums and cafes",
        "High-tech metropolis with ancient temples",
        "Tropical beaches and yoga retreats",
        "Ancient ruins and Italian cuisine",
        "Skyscrapers and Broadway shows"
    ],
    "Country": ["France", "Japan", "Indonesia", "Italy", "USA"]
}
df = pd.DataFrame(travel_data)

# Initialize geocoder
geolocator = Nominatim(user_agent="travel_app")

def show_free_map(city):
    try:
        location = geolocator.geocode(city)
        if location:
            map_data = pd.DataFrame({'lat': [location.latitude], 'lon': [location.longitude]})
            st.map(map_data, zoom=12)
            return location
        else:
            st.warning(f"Couldn't find {city} on map")
            return None
    except Exception as e:
        st.warning(f"Map loading delayed - free service limit reached. Try again in a minute.")
        return None

def recommend_destinations(df, user_prefs):
    filtered = df.copy()
    if 'budget' in user_prefs:
        filtered = filtered[filtered["Budget"] <= user_prefs["budget"]]
    if 'season' in user_prefs and user_prefs["season"] != "Any":
        filtered = filtered[filtered["Best_Season"] == user_prefs["season"]]
    if 'type' in user_prefs and user_prefs["type"] != "Any":
        filtered = filtered[filtered["Type"] == user_prefs["type"]]
    return filtered.sort_values("Budget")

def get_mock_weather(destination):
    seasons = {
        "Spring": ("🌤️ Mild", 15, 20),
        "Summer": ("☀️ Warm", 25, 35),
        "Fall": ("🍂 Cool", 10, 18),
        "Winter": ("❄️ Cold", 0, 10)
    }
    today = datetime.now().month
    season = "Spring" if 3 <= today <= 5 else "Summer" if 6 <= today <= 8 else "Fall" if 9 <= today <= 11 else "Winter"
    weather_type, temp_min, temp_max = seasons[season]
    return {
        "temperature": random.randint(temp_min, temp_max),
        "conditions": weather_type,
        "season": season
    }

def main():
    st.set_page_config(page_title="Travel Assistant", layout="wide")
    st.title("🌍 Free Travel Assistant")
    
    user_prefs = {
        "budget": st.sidebar.slider("Budget Level", 1, 4, 2),
        "season": st.sidebar.selectbox("Preferred Season", ["Any", "Spring", "Summer", "Fall", "Winter"]),
        "type": st.sidebar.selectbox("Destination Type", ["Any", "City", "Beach", "Historical"])
    }
    
    recommendations = recommend_destinations(df, user_prefs)
    
    if not recommendations.empty:
        st.header("Recommended Destinations")
        for _, row in recommendations.iterrows():
            with st.expander(f"{row['Destination']} - {row['Type']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(row["Destination"])
                    st.write(f"**Country:** {row['Country']}")
                    st.write(f"**Best Season:** {row['Best_Season']}")
                    st.write(f"**Budget:** {'💰' * row['Budget']}")
                    st.write(row["Description"])
                    if st.button(f"Show Map of {row['Destination']}"):
                        location = show_free_map(row['Destination'])
                with col2:
                    weather = get_mock_weather(row['Destination'])
                    st.subheader("Current Weather")
                    st.metric("Temperature", f"{weather['temperature']}°C")
                    st.write(weather['conditions'])
                    st.write(f"({weather['season']} season)")
    else:
        st.warning("No destinations match your filters. Try being more flexible!")

if __name__ == "__main__":
    main()
