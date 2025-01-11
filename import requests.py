import requests
from datetime import datetime
import pandas as pd
import geocoder
from geopy.distance import geodesic

def get_air_temperature(date=None, pagination_token=None):
    base_url = "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"
    params = {}
    
    if date:
        params['date'] = date
    if pagination_token:
        params['paginationToken'] = pagination_token
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example usage

date = datetime.today().strftime('%Y-%m-%d')
try:
    data = get_air_temperature(date=date)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

g = geocoder.ip('me')
current_coords = g.latlng



#%%


df_stations = pd.DataFrame(data["data"]["stations"])


location_df = pd.json_normalize(df_stations['location'])
df_stations = df_stations.drop(columns=['location']).join(location_df)

df_stations['distance'] = df_stations.apply(
        lambda row: geodesic(current_coords, (row['latitude'], row['longitude'])).meters, axis=1
    )
closest_station_id = df_stations.loc[df_stations['distance'].idxmin()]['id']
        


time = data['data']['readings'][-1]["timestamp"]

df_current = pd.DataFrame(data['data']['readings'][-1]["data"])

print(f"The tempearture is {df_current[df_current['stationId']==closest_station_id]['value'].values[0]} at time of {time}")
