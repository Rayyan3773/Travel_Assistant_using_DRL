import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim  # Free geocoding
import random  # For mock weather data
import requests  # For API calls (we'll use free services)
from datetime import datetime  # For seasonal weather

# Free sample data - no API needed
travel_data = {
    "Destination": ["Paris", "Tokyo", "Bali", "Rome", "New York"],
    "Type": ["City", "City", "Beach", "Historical", "City"],
    "Budget": [3, 4, 2, 3, 4],  # 1=Cheapest ($), 4=Most Expensive ($$$$)
    "Best_Season": ["Spring", "Fall", "Summer", "Spring", "Fall"],
    "Description": [
        "Romantic city with museums and cafes",
        "High-tech metropolis with ancient temples",
        "Tropical beaches and yoga retreats",
        "Ancient ruins and Italian cuisine",
        "Skyscrapers and Broadway shows"
    ]
}
df = pd.DataFrame(travel_data)

# Initialize the free geocoding service
geolocator = Nominatim(user_agent="travel_app")

def show_free_map(city):
    try:
        # Get location data (free but rate-limited)
        location = geolocator.geocode(city)
        if location:
            # Create map data
            map_data = pd.DataFrame({
                'lat': [location.latitude],
                'lon': [location.longitude]
            })
            # Display map with zoom
            st.map(map_data, zoom=12)
            return location
        else:
            st.warning(f"Couldn't find {city} on map")
            return None
    except Exception as e:
        st.warning(f"Map loading delayed - free service limit reached. Try again in a minute.")
        return None
    
    def recommend_destinations(df, user_prefs):
    """Filters destinations based on user preferences"""
    filtered = df.copy()
    
    # Budget filter (1-4 scale)
    if 'budget' in user_prefs:
        filtered = filtered[filtered["Budget"] <= user_prefs["budget"]]
    
    # Season filter
    if 'season' in user_prefs and user_prefs["season"] != "Any":
        filtered = filtered[filtered["Best_Season"] == user_prefs["season"]]
    
    # Destination type filter
    if 'type' in user_prefs and user_prefs["type"] != "Any":
        filtered = filtered[filtered["Type"] == user_prefs["type"]]
    
    # Sort by budget (cheapest first)
    return filtered.sort_values("Budget")


# Test the function
test_prefs = {"budget": 3, "season": "Spring"}
print(recommend_destinations(df, test_prefs))


# Add the Country column to your existing data
df["Country"] = ["France", "Japan", "Indonesia", "Italy", "USA"]  # Match your 5 destinations

# Verify it worked
print(df[["Destination", "Country"]])  # Should show all destinations with countries

def get_mock_weather(destination):
    """Generates realistic seasonal weather"""
    seasons = {
        "Spring": ("🌤️ Mild", 15, 20),
        "Summer": ("☀️ Warm", 25, 35),
        "Fall": ("🍂 Cool", 10, 18),
        "Winter": ("❄️ Cold", 0, 10)
    }
    today = datetime.now().month
    season = "Spring" if 3 <= today <= 5 else \
             "Summer" if 6 <= today <= 8 else \
             "Fall" if 9 <= today <= 11 else "Winter"
    
    weather_type, temp_min, temp_max = seasons[season]
    return {
        "temperature": random.randint(temp_min, temp_max),
        "conditions": weather_type,  # Note: using "conditions" (with 's')
        "season": season
    }

def main():
    # Configure page
    st.set_page_config(page_title="Travel Assistant", layout="wide")
    
    # Header
    st.title("🌍 Free Travel Assistant")
    st.write("Discover your perfect destination based on preferences")
    
    # Sidebar filters
    st.sidebar.header("Your Preferences")
    user_prefs = {
        "budget": st.sidebar.slider("Budget Level", 1, 4, 2),
        "season": st.sidebar.selectbox("Preferred Season", ["Any", "Spring", "Summer", "Fall", "Winter"]),
        "type": st.sidebar.selectbox("Destination Type", ["Any", "City", "Beach", "Historical"])
    }
    
    # Get recommendations
    recommendations = recommend_destinations(df, user_prefs)
    
    # Display results
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
                    
                    # Show map
                    if st.button(f"Show Map of {row['Destination']}"):
                        location = show_free_map(row['Destination'])
                
                with col2:
                    weather = get_mock_weather(row['Destination'])
                    st.subheader("Current Weather")
                    st.metric("Temperature", f"{weather['temperature']}°C")
                    #st.write(weather['condition'])
                    st.write(weather['conditions'])  # Changed to match the dictionary key
                    st.write(f"({weather['season']} season)")
    else:
        st.warning("No destinations match your filters. Try being more flexible!")

if __name__ == "__main__":
    main()