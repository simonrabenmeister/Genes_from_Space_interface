import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Forest_cover_v_obs_server.json/run"

data = {
"GFS_IndicatorsTool>read_csv.yml@40|csv": '[(''ID'', ''Value''), (1, ''a''), (2, ''b''), (3, ''c'')]',
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@33|pipeline@38":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[19,29,10,20],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@39|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": 10
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)