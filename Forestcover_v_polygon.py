import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Forestcover_v_polygon.json/run"

data = {
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@33|pipeline@38":[2000,2010, 2015],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": [0.1],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"pipeline@40": "/userdata/population_polygons.geojson"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)

print(response.status_code)
print(response.json())