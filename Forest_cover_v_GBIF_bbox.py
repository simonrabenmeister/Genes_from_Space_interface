import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Forest_cover_v_GBIF_bbox.json/run"

data = {
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@12": "Quercus sartorii",
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@14": 1980,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@15": 2020,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": 10.0,
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": 50.0,
  "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
  "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@189|pipeline@38": [2000, 2005, 2010, 2015, 2020],
  "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": [0.1],
  "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": [50],
  "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@21":[19,29,10,20]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)