import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_bbox.json/run"

data = {
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@176|pipeline@123":[2000,2005,2010],
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@176|pipeline@124":[130,140],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": [0.1],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[1,10,100], 
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": 10.0,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": 50.0,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@12": "Quercus sartorii",
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@14": 1980,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@15": 2020,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@21":[19,29,10,20]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)