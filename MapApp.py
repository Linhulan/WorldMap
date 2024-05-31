
import os
import folium
import folium.map
import folium.plugins
import folium.raster_layers
import requests
import pandas as pd
import json
import branca
import geopandas
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
    
    df = read_xlsx("D:\\200_WL\\298_外国货币信息\世界货币信息统计\\01-双CIS货币开发状态\\01-GL20货币开发状态.xlsx", header=0)
    df = df[["国家和地区", "ISO代码", "软件开发状态", "货币状态", "鉴伪状态", "备注"]]

    # 使用 apply 方法调用 is_english 函数，创建一个新的列来表示是否是英文字符
    df['is_english'] = df['ISO代码'].apply(is_english)

    if status == "":
      return df
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
    elif status == 5:
      filtered_df = df[ (df["is_english"]) 
                  & (df["备注"]).str.contains("不流通")
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
not_circulate = get_country_by_status(5)            # 深绿
# customer_auth = get_country_by_status(5)        # 蓝色
# official_auth = get_country_by_status(6)        # 紫色


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

    if fuzz_match(country, undevlop):
        print(country)
        print("原色\r\n")
        color = '#ffffff'

    if fuzz_match(country, devlopping_half):
        print(country)
        print("红色\r\n")
        color = '#ff0000'
        
    if fuzz_match(country, devlopping_lack_new):
        print(country)
        print("黄色\r\n")
        color = '#ffff00'
        
    if fuzz_match(country, devlopping_lack_old):
        print(country)
        print("淡绿\r\n")
        color = '#99ff99'
        
    if fuzz_match(country, developed):
        print(country)
        print("绿色\r\n")
        color = '#00ff00'

    return {
        'fillColor': color,
        'color': 'black',
        'fillOpacity': 0.3,
        'weight': 1,
        'dashArray': '5, 5',
    }

def style_not_circulate(feature):
  global not_circulate
  country = feature['properties']['name']
  color = '#ffffff'

  skip_list = ['俄罗斯']
     
  if fuzz_match(country, not_circulate) & (country not in skip_list):
    print(country)
    print("不流通 红色\r\n")
    color = '#ff0000'
  
  return {
    'fillColor': color,
    'color': 'black',
    'fillOpacity': 0.3,
    'weight': 1,
    'dashArray': '5, 5',
  }


def main():
  map = folium.Map(location=[0, 0], zoom_start=2)
  create_jawg_sunny_TileLayer().add_to(map)

  fg = folium.FeatureGroup(name="Icon collection", show=False).add_to(map)
  folium.Marker(location=(0, 0)).add_to(fg)

  # with open('./data/world.zh.json', 'r', encoding="utf-8") as file:
  #   geo_json_data  = json.load(file)

  with open('./data/world.zh.json', 'r', encoding="utf-8") as file:
    geo_json_data  = json.load(file)
    world = geopandas.GeoDataFrame.from_features(geo_json_data, crs="EPSG:4326")
    print(world.shape)

    global all_countries
    worldmerge =  world.merge(all_countries, how='left', left_on='name', right_on='国家和地区')
    # worldmerge.to_csv('./data/worldmerge.csv', index=False)
    # print(worldmerge.head())
  #   honkong = all_countries[all_countries['国家和地区'] == '中国香港']
  #   print(honkong)
  #   taiwan = all_countries[all_countries['国家和地区'] == '中国台湾']
  #   print(taiwan)
  # return
  
  global status
  status = 0

  tooltip = folium.GeoJsonTooltip(
      fields=["name","ISO代码", "软件开发状态", "货币状态", "鉴伪状态", "备注"],
      aliases=["国家:", "货币:", "软件状态:", "货币状态:", "鉴伪状态:", "备注:"],
      localize=True,
      sticky=False,
      labels=True,
      style="""
        font-size:14px;             /* 修改字体大小 */
        font-family:Arial;          /* 设置字体类型 */
        background-color: #F0EFEF;  /* 设置背景颜色 */
        border: 2px solid #cccccc;  /* 添加边框 */
        padding: 5px;               /* 设置内边距 */
        border-radius: 4px;         /* 边框圆角 */
        min-width: 200px;           /* 设置最小宽度 */
        white-space: pre;           /* 保持文本换行 */
      """,
      max_width=800,
  )

  not_circulate_tooltip = folium.GeoJsonTooltip(
      fields=["name","ISO代码", "软件开发状态", "货币状态", "鉴伪状态", "备注"],
      aliases=["国家:", "货币:", "软件状态:", "货币状态:", "鉴伪状态:", "备注:"],
      localize=True,
      sticky=False,
      labels=True,
      style="""
        font-size:14px;             /* 修改字体大小 */
        font-family:Arial;          /* 设置字体类型 */
        background-color: #F0EFEF;  /* 设置背景颜色 */
        border: 2px solid #cccccc;  /* 添加边框 */
        padding: 5px;               /* 设置内边距 */
        border-radius: 4px;         /* 边框圆角 */
        min-width: 200px;           /* 设置最小宽度 */
        white-space: pre;           /* 保持文本换行 */
      """,
      max_width=800,
  )

  color_undev = folium.FeatureGroup(name="开发状态", show=True).add_to(map)
  folium.GeoJson(
      worldmerge, 
      name = "开发状态",
      tooltip = tooltip,
      style_function = country_style,
      highlight_function = lambda feature: {
        "fillOpacity": 0.6,
      },
    ).add_to(color_undev)
  
  color_not_circulate = folium.FeatureGroup(name="不流通货币", show=False).add_to(map)
  folium.GeoJson(
      worldmerge, 
      name = "不流通货币",
      tooltip = not_circulate_tooltip,
      style_function = style_not_circulate,
      highlight_function = lambda feature: {
        "fillOpacity": 0.6,
      },
    ).add_to(color_not_circulate)

  # 增加搜索框
  folium.plugins.Geocoder().add_to(map)
  # 增加图层控制器
  folium.LayerControl().add_to(map)

  map.save("map.html")

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
  # print (not_circulate)
  # print(all_countries.head())
  # print(enumerate(all_countries['备注']))

  # test_fuzz_match()
  # print(get_country_by_status(0).shape)
  # print(get_country_by_status(1).shape)
  # print(get_country_by_status(2).shape)
  # print(get_country_by_status(3).shape)
  # print(get_country_by_status(4).shape)


  # print(get_country_by_status(2))

  # with open('./data/world.zh.json', 'r', encoding="utf-8") as file:
  #   geo_json_data  = json.load(file)
  #   world = geopandas.GeoDataFrame.from_features(geo_json_data, crs="EPSG:4326")
  #   print(world.shape)

  #   all_countries2 = all_countries[["国家和地区", "软件开发状态", "货币状态", "鉴伪状态"]]
  #   worldmerge =  world.merge(all_countries2, how='left', left_on='name', right_on='国家和地区')
  #   # worldmerge.to_csv('./data/worldmerge.csv', index=False)
  #   print(worldmerge.shape)





