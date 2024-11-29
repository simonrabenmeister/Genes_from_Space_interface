import requests

url = "http://localhost/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_countries.json/run"

data = {
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@178|pipeline@123":[1,10,100],
"GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@178|pipeline@124":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density":[1,10,100],
"GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": "Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023",
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": 10,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": 50,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|data>getObservations.yml@10|year_end": 2020,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@12": "Quercus sartorii",
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@14": 1980,
"GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@22":["Mexico", "Guatemala"]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)