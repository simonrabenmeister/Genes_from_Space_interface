import requests




def TC_obs(session):
    csv= session["csv"]
    years= session["years"]
    ne_nc= session["ne_nc"] 
    pop_density= session["pop_density"] 
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]

    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Forest_cover_v_obs_server.json/run"

    data = {
        "GFS_IndicatorsTool>read_csv.yml@40|csv": csv,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@33|pipeline@38": years,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@39|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response


def TC_bbox(session):
    bbox= session["bbox"]
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]
    pop_distance= session["pop_distance"]
    species= session["species"]
    start_year= session["start_year"]
    end_year= session["end_year"]
    
    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Forest_cover_v_GBIF_bbox.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@12": species,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@14": start_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@15": end_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": pop_distance,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@189|pipeline@38": years,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@204|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@199|pipeline@21": bbox
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_country(session):
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]
    pop_distance= session["pop_distance"]
    species= session["species"]
    start_year= session["start_year"]
    end_year= session["end_year"]
    countries= session["countries"]
    cover_types= session["LC class"]

    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_countries.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@178|pipeline@123": years,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@178|pipeline@124": cover_types,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": [ne_nc],
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": [pop_density],
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@176|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": pop_distance,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|data>getObservations.yml@10|year_end": end_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@12": species,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@14": start_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@177|pipeline@22": [countries]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def TC_country( session):
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]
    pop_distance= session["pop_distance"]
    species= session["species"]
    start_year= session["start_year"]
    end_year= session["end_year"]
    countries= session["countries"]

    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Forest_cover_v_GBIF_countries.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@189|pipeline@38": years,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@199|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@199|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@199|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": pop_distance,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|data>getObservations.yml@10|year_end": end_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|pipeline@12": species,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|pipeline@14": start_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_country.json@198|pipeline@22": countries
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def TC_polygon(session):
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    filepath= session["filepath"]
    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Forestcover_v_polygon.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@33|pipeline@38": years,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "pipeline@40": filepath
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_bbox(session):
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]
    pop_distance= session["pop_distance"]
    species= session["species"]
    start_year= session["start_year"]
    end_year= session["end_year"]
    cover_types= session["LC class"]
    bbox= session["bbox"]
    
    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_bbox.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@176|pipeline@123": years,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@176|pipeline@124": cover_types,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@177|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": pop_distance,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@12": species,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@14": start_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@15": end_year,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_GBIF_occurences_bbox.json@178|pipeline@21": bbox
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_obs(session):
    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Landcover_v_obs_server.json/run"

    cover_types= session["LC class"]
    csv= session["csv"]
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    buffer_size= session["buffer_size"]
    pop_distance= session["pop_distance"]
                          
    data = {
        "GFS_IndicatorsTool>read_csv.yml@42|csv": csv,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@123": years,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@124": cover_types,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@40|GFS_IndicatorsTool>get_pop_poly.yml@5|buffer_size": buffer_size,
        "GenesFromSpace>ToolComponents>GetPopulationPolygons>GFS_Population_polygons_from_table_observations.json@40|GFS_IndicatorsTool>get_pop_poly.yml@5|pop_distance": pop_distance
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_polygon(session):
    url = "http://130.60.24.27/pipeline/GenesFromSpace>Tool>Landcover_v_polygon.json/run"

    cover_types= session["LC class"]
    years= session["years"]
    ne_nc= session["ne_nc"]
    pop_density= session["pop_density"]
    runtitle= session["runtitle"]
    geojson= session["geojson"]

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@123": years,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@124": cover_types,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": [ne_nc],
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": [pop_density],
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": runtitle,
        "pipeline@38": geojson
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response