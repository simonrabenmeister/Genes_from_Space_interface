import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Landcover_v_polygon.json/run"

data = {
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@123":[1,10,100],
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@124":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"pipeline@38": "/userdata/population_polygons.geojson"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)