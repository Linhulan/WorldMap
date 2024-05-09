
import os
import folium
import folium.map
import folium.plugins
import folium.raster_layers
import requests
import pandas as pd
import json
import branca
from fuzzywuzzy import process
from openpyxl import load_workbook
from xlrd import open_workbook

def read_xlsx(file, sheet_name=None, header=None):
    """读取 xlsx 格式文件。"""
    excel = pd.ExcelFile(load_workbook(file), engine="openpyxl")
    sheet_name = sheet_name or excel.sheet_names[0]
    sheet = excel.book[sheet_name]
    df = excel.parse(sheet_name, header=header)

    for item in sheet.merged_cells:
        top_col, top_row, bottom_col, bottom_row = item.bounds
        base_value = item.start_cell.value
        # 1-based index转为0-based index
        top_row -= 1
        top_col -= 1
        # 由于前面的几行被设为了header，所以这里要对坐标进行调整
        if header is not None:
            top_row -= header + 1
            bottom_row -= header + 1
        df.iloc[top_row:bottom_row, top_col:bottom_col] = base_value
    return df

def read_xls(file, sheet_name=None, header=None):
    """读取 xls 格式文件。"""
    excel = pd.ExcelFile(open_workbook(file, formatting_info=True), engine="xlrd")
    sheet_name = sheet_name or excel.sheet_names[0]
    sheet = excel.book[sheet_name]
    df = excel.parse(sheet_name, header=header)

    # 0-based index
    for top_row, bottom_row, top_col, bottom_col in sheet.merged_cells:
        base_value = sheet.cell_value(top_row, top_col)
        # 由于前面的几行被设为了header，所以这里要对坐标进行调整
        if header is not None:
            top_row -= header + 1
            bottom_row -= header + 1
        df.iloc[top_row:bottom_row, top_col:bottom_col] = base_value
    return df


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

    state_data = pd.read_csv(
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
  tile = 'https://tile.jawg.io/jawg-sunny/{z}/{x}/{y}{r}.png?' + f'access-token={accessToken}'
  attr =  '<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  layer = folium.TileLayer(zoom_start=zoom_start,
                    location=location,
                    tiles=tile, 
                    attr=attr,
                    min_zoom=0,
                    max_zoom=22,
                    name='国家图层'
                  )
  return layer

def get_country_by_status(status=""):
    """
    :param status: 软件开发状态(0-4)
    :0-未开发
    :1-正在开发, 还缺一半以上货币
    :2-正在开发, 还缺新货币
    :3-正在开发, 还缺老货币
    :4-已开发
    :return: 返回国家列表
    """
    # 定义一个函数来检查字符串是否只包含英文字符
    def is_english(s):
        return s.isascii()
    
    # 读取Excel文件
    filtered_df = None
    df = read_xlsx('./data/01-GL20货币开发状态.xlsx', header=0)
    df = df[["国家和地区", "ISO代码", "软件开发状态", "货币状态", "鉴伪状态"]]

    # 使用 apply 方法调用 is_english 函数，创建一个新的列来表示是否是英文字符
    df['is_english'] = df['ISO代码'].apply(is_english)

    if status == "":
      return df["国家和地区"].to_list()
    elif status == 0:
      filtered_df = df[ (df["is_english"]) 
                  & (df["软件开发状态"]).isna()
                  & (df["货币状态"]).isna()
                  & (df["鉴伪状态"]).isna()
          ]
    elif status == 1:
      filtered_df = df[ (df["is_english"]) 
                  & (df["软件开发状态"] == "初步开发") 
                  & (df["货币状态"] == "货币不全") 
                  & (df["鉴伪状态"] == "未做鉴伪")
          ]
    elif status == 2:
      filtered_df = df[ (df["is_english"]) 
                  & (df["软件开发状态"] == "初步开发") 
                  & (df["货币状态"] == "货币不全")
                  & (df["鉴伪状态"] == "鉴伪不全")
          ]
    elif status == 3:
      filtered_df = df[ (df["is_english"]) 
                  & (df["软件开发状态"] == "初步开发") 
                  & (df["货币状态"] == "货币不全")
                  & (df["鉴伪状态"]).isna()
          ]
    elif status == 4:
      filtered_df = df[ (df["is_english"]) 
                  & (df["软件开发状态"]).isin(["初步开发", "客户认证", "官方认证"])
                  & (df["货币状态"]).isna()
                  & (df["鉴伪状态"]).isna()
          ]
    
    return filtered_df["国家和地区"]
    
def fuzz_match(country, status: list) -> bool:
    """
    :param country: 输入的国家名
    :param status: 对应开发状态的列表
    :return: 返回是否匹配成功
    """
    best_match = process.extract(country, status)
    best_match_country = [country[0] for country in best_match if country[1] > 49]
    # print(best_match)

    if country in ''.join(best_match_country):
        return True
    else:
        return False
    

    # best_match = process.extractOne(country, status)
    # if best_match[1] > 49:
    #     return True
    # else:
    #     return False

    

all_countries = get_country_by_status()
undevlop = get_country_by_status(0)             # 原色
devlopping_half = get_country_by_status(1)      # 红色
devlopping_lack_new = get_country_by_status(2)  # 黄色
devlopping_lack_old = get_country_by_status(3)  # 淡绿
developed = get_country_by_status(4)            # 深绿

status = 0

def country_style(feature):
    global all_countries
    global undevlop                       # 原色
    global devlopping_half                # 红色
    global devlopping_lack_new            # 黄色
    global devlopping_lack_old            # 淡绿
    global developed                      # 深绿
    global status
    country = feature['properties']['name']
    color = '#ffffff'

    # best_match = process.extractOne(country, all_countries)
    # best_match_country = [country[0] for country in best_match if country[1] > 49]
    # if country in ''.join(best_match_country):
    #    print(country)
    #    color = '#00ff00'

    if status==0 and fuzz_match(country, undevlop):
        print(country)
        print("原色\r\n")
        color = '#ffffff'

    if status==1 and fuzz_match(country, devlopping_half):
        print(country)
        print("红色\r\n")
        color = '#ff0000'
        
    if status==2 and fuzz_match(country, devlopping_lack_new):
        print(country)
        print("黄色\r\n")
        color = '#ffff00'
        
    if status==3 and fuzz_match(country, devlopping_lack_old):
        print(country)
        print("淡绿\r\n")
        color = '#99ff99'
        
    if status==4 and fuzz_match(country, developed):
        print(country)
        print("绿色\r\n")
        color = '#00ff00'

    return {
        'fillColor': color,
        'color': 'black',
        'fillOpacity': 0.5,
        'weight': 1,
        'dashArray': '5, 5',
    }


def main():
  map = folium.Map(location=[0, 0], zoom_start=2)
  create_jawg_sunny_TileLayer().add_to(map)

  fg = folium.FeatureGroup(name="Icon collection", show=True).add_to(map)
  folium.Marker(location=(0, 0)).add_to(fg)

  with open('./data/world.zh.json', 'r', encoding="utf-8") as file:
    geo_json_data  = json.load(file)


  global status

  status = 0
  color_undev = folium.FeatureGroup(name="未开发", show=True).add_to(map)
  folium.GeoJson(
      geo_json_data, 
      name="未开发",
      style_function=country_style
    ).add_to(color_undev)

  status = 1
  color_deving_half = folium.FeatureGroup(name="缺一半货币", show=True).add_to(map)
  folium.GeoJson(
      geo_json_data, 
      name="缺一半货币",
      style_function=country_style
    ).add_to(color_deving_half)

  colormap = branca.colormap.LinearColormap(
    colors=["#ffffff", "#ff0000", "#ffff00", "#99ff99", "#00ff00"],
    caption="State Level Median County Household Income (%)",
  )
  colormap.add_to(map)

  # 增加点击事件
  map.add_child(
    folium.DevStatusPopup()
  )
  # 增加搜索框
  folium.plugins.Geocoder().add_to(map)
  # 增加图层控制器
  folium.LayerControl().add_to(map)

  map.save("basic_map.html")

def test_fuzz_match():
   while True:
      country = input("请输入国家：")
      if fuzz_match(country, undevlop):
        print("原色\r\n")
      if fuzz_match(country, devlopping_half):
        print("红色\r\n")
      if fuzz_match(country, devlopping_lack_new):
        print("黄色\r\n")
      if fuzz_match(country, devlopping_lack_old):
        print("淡绿\r\n")

if __name__ == "__main__":
  main()
  # test_fuzz_match()
  # print(get_country_by_status(0).shape)
  # print(get_country_by_status(1).shape)
  # print(get_country_by_status(2).shape)
  # print(get_country_by_status(3).shape)
  # print(get_country_by_status(4).shape)


  # print(get_country_by_status(2))
