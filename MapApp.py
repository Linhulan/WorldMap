import folium
import folium.map
import requests
import pandas
import json
from geopy.geocoders import Nominatim

class WorldMap:
  
  def __init__(self, location=None, zoom_start=10, tiles=None):
    accessToken = '8wpMncgJdplYGie68vZuWguQqxbGTmUpa8wkcu775mrZNfBRdjWsg761NBsrUQoW'
    tile = 'https://tile.jawg.io/jawg-sunny/{z}/{x}/{y}{r}.png?access-token=8wpMncgJdplYGie68vZuWguQqxbGTmUpa8wkcu775mrZNfBRdjWsg761NBsrUQoW'
    attr = 'jawg-sunny'
    self.map = folium.Map(zoom_start=zoom_start,
                          location=location,
                          tiles=tile, 
                          attr=attr
                        )
  
  def add_layer(self, lat=None, lon=None, popup=None):
    geojson_data = requests.get(
        "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json"
    ).json()

    folium.GeoJson(geojson_data, name="hello world").add_to(map)
    folium.LayerControl().add_to(map)

  def get_map(self):
    return self.map
  
  def save(self, filename):
    self.map.save(filename)
  
  def test_choropleth(self):
    with open("./us_states.json", "r") as f:
      state_geo = json.load(f)

    state_data = pandas.read_csv(
        'us_unemployment_oct_2012.csv'
    )

    m = self.map

    folium.Choropleth(
        geo_data=state_geo,
        name="choropleth",
        data=state_data,
        columns=["State", "Unemployment"],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Unemployment Rate (%)",
    ).add_to(m)

    folium.LayerControl().add_to(m)
    self.map = m

def create_jawg_sunny_TileLayer(zoom_start=10, location=None):
  accessToken = '8wpMncgJdplYGie68vZuWguQqxbGTmUpa8wkcu775mrZNfBRdjWsg761NBsrUQoW'
  tile = 'https://tile.jawg.io/jawg-sunny/{z}/{x}/{y}{r}.png?' + 'access-token={accessToken}'.format(accessToken=accessToken)
  attr = 'jawg-sunny'
  layer = folium.TileLayer(zoom_start=zoom_start,
                    location=location,
                    tiles=tile, 
                    attr=attr,
                    name='国家图层'
                  )
  return layer

def get_country_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my-application")
    location = geolocator.reverse(str(latitude) + ", " + str(longitude))
    address = location.raw['address']
    country = address.get('country', '')
    return country

def main():
  map = folium.Map(location=[0, 0], zoom_start=2)
  create_jawg_sunny_TileLayer().add_to(map)

  fg = folium.FeatureGroup(name="Icon collection", show=True).add_to(map)
  folium.Marker(location=(0, 0)).add_to(fg)


  geojson_data = requests.get(
      "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/world_countries.json"
  ).json()
  color_fg = folium.FeatureGroup(name="开发状态", show=False).add_to(map)
  folium.GeoJson(geojson_data, name="hello world").add_to(color_fg)
  
  map.add_child(
    folium.devStatusPopup()
  )

  # 增加图层控制器
  folium.LayerControl().add_to(map)
  map.save("basic_map.html")


def test():
    # Create a map centered around a specific location
  map = folium.Map(location=[0, 0], zoom_start=2)

  # Add tile layers with custom names
  folium.TileLayer(
      tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attr='OpenStreetMap',
      name='Original Layer Name'
  ).add_to(map)

  folium.TileLayer(
      tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attr='OpenStreetMap',
      name='New Layer Name'  # Set the new name for this layer
  ).add_to(map)

  # Add layer control and specify the names of the layers
  folium.LayerControl().add_to(map)

  # Display the map
  map.save("map.html")

if __name__ == "__main__":
  main()


  # # 接口地址
  # url = "https://api.map.baidu.com/reverse_geocoding/v3"

  # # 此处填写你在控制台-应用管理-创建应用后获取的AK
  # ak = "EYve3CTfebITGLeJYPNVTiywtpACck3R"

  # params = {
  #     "ak":       ak,
  #     "output":    "json",
  #     "coordtype":    "wgs84ll",
  #     "extensions_poi":    "0",
  #     "location":    "31.225696563611,121.49884033194",

  # }

  # response = requests.get(url=url, params=params)
  # if response:
  #     print(response.json())