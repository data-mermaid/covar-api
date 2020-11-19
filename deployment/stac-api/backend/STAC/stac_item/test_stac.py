from fastapi import FastAPI
from fastapi.testclient import TestClient
from .routes import stac_router
import json

client = TestClient(stac_router)

with open("ingest/stac_examples/root_catalog/root.json") as json_file:
  root = json.load(json_file)

with open("ingest/stac_examples/items/digitalglobe-sample.json") as json_file:
    dg_item = json.load(json_file)

''' Basic GET routes '''

def test_get_root():
    response = client.get("/")
    assert response.status_code == 200, "Not able to root stac collection"
    # assert response.json() == root
    assert response.json()['title'] == "Prescient Discovery"

def test_get_all_collections():
    response = client.get("/collections")
    assert response.status_code == 200, "Not able to GET stac collections"
    assert len(response.json()) == 3
    assert response.json()[0]['title'] == "Landsat-8 L1 Collection-1"
    assert response.json()[1]['title'] == "Sentinel 2 L2A COGs"
    assert response.json()[2]['title'] == "RADARSAT-1 Open Data"

def test_get_landsat_collection():
    response = client.get("/collections/landsat-8-l1-c1")
    assert response.status_code == 200, "Not able to GET landsat collection"
    assert response.json()['description'] == "Landat-8 L1 Collection-1 \
imagery radiometrically calibrated and orthorectified using gound points \
and Digital Elevation Model (DEM) data to correct relief displacement."

def test_get_sentinel_cogs_collection():
    response = client.get("/collections/sentinel-s2-l2a-cogs")
    assert response.status_code == 200, "Not able to GET sentinel collection"
    assert response.json()['description'] == "Sentinel-2a and Sentinel-2b \
imagery, processed to Level 2A (Surface Reflectance) and converted to \
Cloud-Optimized GeoTIFFs"

def test_get_sentinel_cogs_items():
    response = client.get("/collections/sentinel-s2-l2a-cogs/items")
    assert response.status_code == 200, "Not able to GET sentinel items"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"

def test_get_landsat_items():
    response = client.get("/collections/landsat-8-l1-c1/items")
    assert response.status_code == 200, "Not able to GET sentinel items"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"

def test_get_single_sentinel_cog_item():
    response = client.get("/collections/sentinel-s2-l2a-cogs/items/S2A_21XWL_20200809_4_L2A")
    assert response.status_code == 200, "Not able to GET sentinel item"
    assert response.json()['id'] == "S2A_21XWL_20200809_4_L2A"

def test_get_single_landsat_item():
    response = client.get("/collections/landsat-8-l1-c1/items/LC08_L1GT_090110_20200101_20200101_01_RT")
    assert response.status_code == 200, "Not able to GET landsat item"
    assert response.json()['id'] == "LC08_L1GT_090110_20200101_20200101_01_RT"

''' GET /search '''

def test_get_search_limit():
    response = client.get("/search?limit=2")
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2

def test_get_search_collection_sentinel():
    response = client.get("/search?collections=sentinel-s2-l2a-cogs&limit=2")
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    assert response.json()['features'][1]['collection'] == "sentinel-s2-l2a-cogs"

# -123.693953,48.374155,-123.155622,48.628938 - greater victoria bbox
# -127.953644,48.198362,-121.801300,50.933551 - van island

def test_get_search_collection_landsat():
    response = client.get("/search?collections=landsat-8-l1-c1&limit=2")
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    # assert response.json()['features'][1]['collection'] == "landsat-8-l1-c1"

bbox_string = "/search?collections=sentinel-s2-l2a-cogs&limit=2&bbox0=-127.953644&bbox1=48.198362&bbox2=-121.801300&bbox3=50.933551"
def test_get_search_bbox():
    response = client.get(bbox_string)
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    assert response.json()['features'][1]['collection'] == "sentinel-s2-l2a-cogs"
    # assert -127.953644 <= response.json()['features'][0]['bbox'][0] 
    # assert 48.198362 <= response.json()['features'][0]['bbox'][1] 
    # assert response.json()['features'][0]['bbox'][2] <= -121.801300
    # assert response.json()['features'][0]['bbox'][3] <= 50.933551

date_string = '/search?collections=sentinel-s2-l2a-cogs&limit=2&bbox0=-127.953644&bbox1=48.198362&bbox2=-121.801300&bbox3=50.933551&datetime=2020-10-01T00%3A00%3A00Z%2F2020-10-11T12%3A31%3A12Z'
def test_get_search_date():
    response = client.get(date_string)
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    assert response.json()['features'][1]['collection'] == "sentinel-s2-l2a-cogs"
    assert '2020-10-01T00%3A00%3A00Z' <= response.json()['features'][0]['properties']['datetime'] <= '2020-10-11T12%3A31%3A12Z'

searchValString_string = '/search?collections=sentinel-s2-l2a-cogs&limit=2&bbox0=-127.953644&bbox1=48.198362&bbox2=-121.801300&bbox3=50.933551&datetime=2019-10-01T00%3A00%3A00Z%2F2020-10-11T12%3A31%3A12Z&searchKey=sentinel%3Agrid_square&searchValStr=XQ'
def test_get_search_value_string():
    response = client.get(searchValString_string)
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    assert response.json()['features'][1]['collection'] == "sentinel-s2-l2a-cogs"
    assert response.json()['features'][1]['properties']['sentinel:grid_square'] == "XQ"

searchValInt_string = '/search?collections=sentinel-s2-l2a-cogs&limit=2&bbox0=-127.953644&bbox1=48.198362&bbox2=-121.801300&bbox3=50.933551&datetime=2019-10-01T00%3A00%3A00Z%2F2020-10-11T12%3A31%3A12Z&searchKey=eo%3Acloud_cover&searchValIntLt=43&searchValIntGt=42'
def test_get_search_value_int():
    response = client.get(searchValInt_string)
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['numberReturned'] == 2
    assert response.json()['features'][1]['collection'] == "sentinel-s2-l2a-cogs"
    assert 42 <= response.json()['features'][1]['properties']['eo:cloud_cover'] <= 43

''' POST /search '''

search_datetime = {
  "datetime": "2018-10-01T00:00:00Z/2018-10-11T12:31:12Z",
#   "collections": ["landsat"],
  "limit": 1
}
def test_post_search_datetime():
    response = client.post("/search", json=search_datetime)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"

bbox_test = {
  "bbox": [-76.615219,-33.059320,-32.318344,3.255693], #brazil
  "limit": 2
}
def test_post_search_bbox():
    response = client.post("/search", json=bbox_test)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    # assert bbox_test['bbox'][0] <= response.json()['features'][1]['bbox'][0] 
    # assert bbox_test['bbox'][1] <= response.json()['features'][1]['bbox'][1] 
    # assert response.json()['features'][1]['bbox'][2] <= bbox_test['bbox'][2]
    # assert response.json()['features'][1]['bbox'][3] <= bbox_test['bbox'][3]

stac_collection = {
  "bbox": [-58.791962,-28.730937,-55.803680,-26.551065],
  "collections": ["sentinel-s2-l2a-cogs"],
  "limit": 1
}
def test_post_search_collection():
    response = client.post("/search", json=stac_collection)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert response.json()['features'][0]['collection'] == "sentinel-s2-l2a-cogs"

cloud_cover = {
    "properties": {
        "eo:cloud_cover": {
            "gt": 0,
            "lt": 1
        }
    }
}
def test_post_search_cloud_cover():
    response = client.post("/search", json=cloud_cover)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert 0 <= response.json()['features'][0]['properties']['eo:cloud_cover'] <= 1

cloud_cover_date = {
    "datetime": "2018-10-15T00:00:00Z/2018-11-01T12:31:12Z",
    "collections": ["sentinel-s2-l2a-cogs"],
    "properties": {
        "eo:cloud_cover": {
            "gt": 99,
            "lt": 100
        }
    }
}
def test_post_search_cloud_cover_date():
    response = client.post("/search", json=cloud_cover_date)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['collection'] == "sentinel-s2-l2a-cogs"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert response.json()['features'][0]['properties']['eo:cloud_cover'] >= 99

sun_elevation = {
    "datetime": "2018-02-15T00:00:00Z/2018-11-01T12:31:12Z",
    "collections":["landsat-8-l1-c1"],
    "properties": {
        "view:sun_elevation": {
            "gt": 48,
            "lt": 49
        }
    }
}
def test_post_search_sun_elevation():
    response = client.post("/search", json=sun_elevation)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert 48 <= response.json()['features'][0]['properties']['view:sun_elevation'] <= 49

intersection = {
    "datetime": "2018-10-01T00:00:00Z/2018-11-01T12:31:12Z",
    "intersects": {
        "type": "Polygon",
        "coordinates": [[
            [-77.08248138427734, 38.788612962793636], 
            [-77.01896667480469, 38.788612962793636],
            [-77.01896667480469, 38.835161408189364], 
            [-77.08248138427734, 38.835161408189364],
            [-77.08248138427734, 38.788612962793636]
        ]]
    },
    "collections": ["sentinel-s2-l2a-cogs"],
    "limit": 100
}
def test_post_intersection_polygon():
    response = client.post("/search", json=intersection)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['collection'] == "sentinel-s2-l2a-cogs"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"

''' dev routes '''

search_cloud = {
    "collection_id": "sentinel-s2-l2a-cogs",
    "limit": 10,
    "cloud_cover": 10,
    "bbox": [
        -110.039063,35.029996,-85.957031,45.951150
    ],
    "start_date": "2018-10-31T00:00:00Z",
    "end_date": "2018-11-01T12:31:12Z"
}
def test_post_dev_search_cloud():
    response = client.post("/dev/searchCloud", json=search_cloud)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert response.json()['features'][0]['collection'] == "sentinel-s2-l2a-cogs"
    assert response.json()['features'][0]['properties']['eo:cloud_cover'] <= 10

sphere_test = {
    "limit": 10,
    "collections": "sentinel-s2-l2a-cogs",
    "point_coordinates": [
        -98.1, 37.2
    ],
    "distance": 0.1
}
def test_post_dev_sphere():
    response = client.post("/dev/spheretest", json=sphere_test)
    response_data = response.json()
    assert response.status_code == 200, "Not able to GET item"
    assert response.json()['features'][0]['stac_version'] == "1.0.0-beta.2"
    assert response.json()['features'][0]['collection'] == "sentinel-s2-l2a-cogs"

insert = {
    "collection": "testadditem",
    "item": dg_item
}
def test_insert_item():
    response = client.post("dev/addItem", json=insert)
    response_data = response.json()
    responses = ["item succesfully added", "item already exists"]
    assert response.status_code == 200, "Not able to ADD item"
    assert response.json() in responses

