import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Landcover_v_obs_server.json/run"

data = {
"GFS_IndicatorsTool>read_csv.yml@42|csv": '[(''ID'', ''Value''), (1, ''a''), (2, ''b''), (3, ''c'')]',
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@123":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@124":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@40|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": 10,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@40|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": 50
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)