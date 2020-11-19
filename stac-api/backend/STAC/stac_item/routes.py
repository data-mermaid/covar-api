from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import asyncio
import json
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, GEOSPHERE
from .models import GeoJSON, RootGet, sphereSearch, \
    cloudSearch, returnItems, mainSearch, addItem, metaModel
from stac_validator import stac_validator
from .utils import return_date, do_count, getDB, bbox2poly, poly2bbox, generate_dynamic_links
from .pagination import pagination
from config.config import DB

col_root = DB.root_catalog
col_collections = DB.stac_collections

stac_router = APIRouter()

''' *** STAC API ROUTES *** '''

@stac_router.get("/", response_model=dict)
async def get_root():
    """[summary]
    Gets root collections.
    [description]
    Endpoint to retrieve root collections.
    """
    limit = 10
    col_cursor = await col_root.find_one()
    return col_cursor

@stac_router.get("/conformance", response_model=List[str])
async def get_root():
    """[summary]
    Gets conformance.
    [description]
    Endpoint to retrieve conformance.
    """
    conform = []
    conform.append("https://stacspec.org/STAC-api.html")
    conform.append("http://docs.opengeospatial.org/is/17-069r3/17-069r3.html#ats_geojson")
    conform.append("http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core")
    conform.append("http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html")
    conform.append("http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson")
    return conform

@stac_router.get("/collections", response_model=List[RootGet])
async def get_all_collections():
    """[summary]
    List all collections.
    [description]
    Endpoint to retrieve all collections.
    """
    limit = 10
    col_cursor = col_collections.find()
    cols = await col_cursor.to_list(length=limit)
    return cols

@stac_router.get("/collections/{collection_id}", response_model=dict)
async def get_collection_by_id(collection_id):
    """[summary]
    Return collection by collection id.
    [description]
    Endpoint to retrieve all collections by collection id.
    """
    cursor = await col_collections.find_one({"id": collection_id})
    return cursor

@stac_router.get("/collections/{collection_id}/items", response_model=returnItems)
async def get_items_by_collection_id(collection_id, limit:int=None, bbox0:float=None, bbox1:float=None, bbox2:float=None, bbox3:float=None, datetime:str=None):
    """[summary]
    GET items by collection id and search parameters.
    [description]
    Endpoint to retrieve items by collection id.
    """
    if(limit == None):
        limit = 1
    filters = []

    if(bbox0 != None):
        bbox_filter = {
            "bbox": {"$geoWithin": { "$box": [ [bbox0, bbox1], [bbox2, bbox3]]}},
        }
        filters.append(bbox_filter)
    
    if(datetime != None):
        dt_filter = await return_date(datetime)
        filters.append(dt_filter)

    queries = {}
    for filter in filters:
        queries.update(**filter)

    col = await getDB(collection_id)

    count = await do_count(collection_id, queries, limit)
    item_cursor = col.find(queries)
    ItemA = await item_cursor.to_list(length=limit)

    features = ItemA
    for feature in features:
        feature = await generate_dynamic_links(feature)

    if(count<limit):
        returned = count
    else:
        returned = limit
    Dict = {'numberMatched': count, 'numberReturned':returned, 'features': features}
    return Dict

@stac_router.get("/collections/{collection_id}/items/{item_id}", response_model=dict)
async def get_items_by_item_id(collection_id, item_id):
    """[summary]
    This method returns a single STAC item.
    [description]
    GET a single STAC item.
    """
    if(item_id[-5:]=='.json'):
        item_id = item_id[:-5]
    col = await getDB(collection_id)
    cursor = await col.find_one({"_id": item_id})
    cursor = await generate_dynamic_links(cursor)
    return cursor

@stac_router.get("/search", response_model=dict)
async def query_stac_get(collections:str=None, limit:int=None, bbox0:float=None, 
    bbox1:float=None, bbox2:float=None, bbox3:float=None, datetime:str=None, 
    searchKey:str=None, searchValStr:str=None, searchValIntLt:int=None, 
    searchValIntGt:int=None, page:int=1, ptIntersectA:float=None, ptIntersectB:float=None):
    """[summary]
    GET method to search STAC items on various parameters.
    [description]
    This is the GET search method.
    """
    if(limit == None):
        limit = 1
    filters = []

    ''' pagination logic '''
    page_size = limit

    if(page != None):
        skips = page_size * (page - 1)
    else:
        skips = limit

    if(bbox0 != None):
        poly = bbox2poly(bbox0, bbox1, bbox2, bbox3)
        bbox_filter = {
            "geometry": {"$geoIntersects": { "$geometry": { "type": 'Polygon' , "coordinates": poly }}}
        }
        filters.append(bbox_filter)

    if(ptIntersectA != None and ptIntersectB != None):
        point_filter = {
            "geometry": {"$geoIntersects": { "$geometry": { "type": 'Point' , "coordinates": [ptIntersectA, ptIntersectB] }}}
        }
        filters.append(point_filter)

    if(datetime == None):
        datetime = "2008-12-29T00:00:00Z/2020-12-31T12:31:12Z"
    dt_filter = await return_date(datetime)
    filters.append(dt_filter)
    

    if(searchKey != None):
        key = "properties." + searchKey
        if(searchValStr != None):
            key_filter = { key: searchValStr }
        else:
            key_filter = {
                key: {"$lt":searchValIntLt, "$gt":searchValIntGt}
            }
        filters.append(key_filter)

    queries = {}
    for filter in filters:
        queries.update(**filter)
    
    collections_list = []
    if collections is None:
        collections_list = ["landsat"]
    else:
        collections_list = collections.split(",")   
    results = dict()

    for collection_id in collections_list:

        col = await getDB(collection_id)

        count = await do_count(collection_id, queries, limit)
        item_cursor = col.find(queries).skip(skips).limit(limit) 
        ItemA = await item_cursor.to_list(length=limit)

        features = ItemA

        for feature in features:
            if col == DB.landsat:
                feature["collection"] = "landsat-8-l1"
                feature["properties"]["collection"] = "landsat-8-l1"
            elif col == DB.sentinel_cogs:
                feature["properties"]["collection"] = "sentinel-2-l1c"
            
            feature = await generate_dynamic_links(feature)

        if(count<limit):
            returned = count
        else:
            returned = limit

        bboxX = [bbox0, bbox1, bbox2, bbox3]
        typeInter = "Point"
        
        if(bbox0 != None):
            linkList = pagination(datetime, limit, page, collection_id, bboxX)
        elif(ptIntersectA != None and ptIntersectB != None):
            coordInter = [ptIntersectA, ptIntersectB]
            linkList = pagination(datetime, limit, page, collection_id, None, typeInter, coordInter)
        else:
            linkList = pagination(datetime, limit, page, collection_id)
        prev = linkList[0]
        next = linkList[1]

        ''' Page pagination - END '''

        meta = {'next': next, 'previous': prev, 'count': count, 'limit': limit}
        Dict = {'numberMatched': count, 'numberReturned':returned, 'meta':meta, 'features': features}

        results[collection_id] = Dict
    return results

@stac_router.post("/search", response_model=dict)
async def query_stac(mainSearch: mainSearch, page:int=1):
    """[summary]
    Search STAC items on datetime, properties, intersects etc.
    [description]
    This is the main search method.
    """
    if(mainSearch.limit):
        limit = mainSearch.limit
    else:
        limit = 1
    filters = []

    ''' pagination logic '''
    page_size = limit
    
    if(mainSearch.time and mainSearch.time != 'string'):
        mainSearch.datetime = mainSearch.time

    if(page != None):
        skips = page_size * (page - 1)
    else:
        skips = limit
    
    ''' save this code - bbox within '''
    # if(mainSearch.bbox and mainSearch.bbox[0] != 0):
    #     bbox_filter = {
    #         # "bbox": {"$geoWithin": { "$box": [ [ mainSearch.bbox[0], mainSearch.bbox[1]], [mainSearch.bbox[2], mainSearch.bbox[3]]]}},
    #         "bbox": {"$within": { "$box": [ [ mainSearch.bbox[0], mainSearch.bbox[1]], [mainSearch.bbox[2], mainSearch.bbox[3]]]}},
    #     }
    #     filters.append(bbox_filter)

    if(mainSearch.bbox and mainSearch.bbox[0] != 0):
       
        bbox = mainSearch.bbox
        poly = bbox2poly(bbox[0], bbox[1], bbox[2], bbox[3])
        bbox_filter = {
            "geometry": {"$geoIntersects": { "$geometry": { "type": 'Polygon' , "coordinates": poly }}}
        }
        
        filters.append(bbox_filter)

    if(mainSearch.datetime and mainSearch.datetime != 'string'):
        datetime = mainSearch.datetime
        dt_filter = await return_date(mainSearch.datetime)
        filters.append(dt_filter)
    else:
        datetime = "2008-12-29T00:00:00Z/2020-12-31T12:31:12Z"

    if(mainSearch.intersects):
        if(mainSearch.intersects.type != 'string'):
            if(mainSearch.intersects.type=='Box'):
                bbox = mainSearch.intersects.coordinates
                poly = bbox2poly(bbox[0], bbox[1], bbox[2], bbox[3])
                intersect_filter = {
                    "geometry": {"$geoIntersects": { "$geometry": { "type": 'Polygon' , "coordinates": poly }}}
                }
                filters.append(intersect_filter)
            else:
                intersect_filter = {
                    "geometry": {"$geoIntersects": { "$geometry": { "type": mainSearch.intersects.type , "coordinates": mainSearch.intersects.coordinates }}}
                }
                filters.append(intersect_filter)

    if(mainSearch.ids):
        if(mainSearch.ids[0] != "string"):
            for id in range(len(mainSearch.ids)):
                query = {"id": mainSearch.ids[id]}
                filters.append(query)

    if(mainSearch.properties):
        for key, value in mainSearch.properties.items():
            key = "properties." + key
            if(type(value)==dict):
                key_filter = {
                    key: {"$lt":value['lt'], "$gt":value['gt']}
                }
                filters.append(key_filter)
            elif(type(value)==list):
                for i in value:
                    key_filter = { key : i }
                    filters.append(key_filter)
            else:
                key_filter = { key: value }
                filters.append(key_filter)

    if(mainSearch.query):
        for key, value in mainSearch.query.items():
            key = "properties." + key
            if(type(value)==dict):
                key_filter = {
                    key: {"$lt":value['lt'], "$gt":value['gt']}
                }
                filters.append(key_filter)
            elif(type(value)==list):
                for i in value:
                    key_filter = { key : i }
                    filters.append(key_filter)
            elif(key=="properties.collections"):
                mainSearch.collections = value
            else:
                key_filter = { key: value }
                filters.append(key_filter)

    queries = {}
    for filter in filters:
        queries.update(**filter)
    
    collections = []
    if(mainSearch.collections):
        collections = mainSearch.collections
    else:
        collections = ['landsat']
    results = {}
    
    for collection_id in collections:
        col = await getDB(collection_id)

        count = await do_count(collection_id, queries, limit)

        ''' --- sortby --- '''
        if(mainSearch.sortby):
            sortlist = ()
            for sort in mainSearch.sortby:

                if(sort.field != 'string' and sort.field != None):
                    if(sort.field == 'timestamp'):
                        sort.field = 'properties.datetime'
                    if(sort.direction == 'asc'):
                        item_cursor = col.find(queries).sort(sort.field, 1).skip(skips).limit(limit)
                        break
                    else:
                        item_cursor = col.find(queries).sort(sort.field, -1).skip(skips).limit(limit)   
                        break
                else:
                    item_cursor = col.find(queries).skip(skips).limit(limit)
        else:
            item_cursor = col.find(queries).skip(skips).limit(limit)
        
        ItemA = await item_cursor.to_list(length=limit)
        
        features = ItemA
        
        for feature in features:
            if col == DB.landsat:
                feature["collection"] = "landsat-8-l1"
                feature["properties"]["collection"] = "landsat-8-l1"
            elif col == DB.sentinel_cogs:
                feature["properties"]["collection"] = "sentinel-2-l1c"
            
            feature = await generate_dynamic_links(feature)
        
        if(count<limit):
            returned = count
        else:
            returned = limit

        if(mainSearch.bbox and mainSearch.bbox[0] != 0):
            linkList = pagination(datetime, limit, page, collection_id, mainSearch.bbox)
        elif(mainSearch.intersects and mainSearch.intersects.type != 'string'):
            linkList = pagination(datetime, limit, page, collection_id, None, mainSearch.intersects.type, mainSearch.intersects.coordinates)
        else:
            linkList = pagination(datetime, limit, page, collection_id)
        prev = linkList[0]
        next = linkList[1]
        ''' Page pagination - END '''
        
        meta = {'next': next, 'previous': prev, 'count': count, 'limit': limit}
        Dict = {'numberMatched': count, 'numberReturned':returned, 'meta': meta, 'features': features}

        results[collection_id] = Dict

    return results
    
''' *** DEV ROUTES *** '''

@stac_router.post("/dev/spheretest", response_model=returnItems)
async def sphere_query_test(sphereSearch: sphereSearch):
    """[summary]
    Gets all items in spherical range.
    [description]
    Endpoint to retrieve items.
    """
    limit = sphereSearch.limit
    filters = []

    collection_id = sphereSearch.collections

    col = await getDB(collection_id)

    count = 1000
    
    key_filter = {
        "geometry": {"$nearSphere": { "$geometry": { "type": "Point", "coordinates": sphereSearch.point_coordinates}, "$minDistance": 0, "$maxDistance": sphereSearch.distance}}
        #  $geoWithin: { $centerSphere: [ [ -88, 30 ], 10/3963.2 ] } 
    }

    filters.append(key_filter)
    queries = {}
    for filter in filters:
        queries.update(**filter)
    
    item_cursor = col.find(queries).limit(limit)

    ItemA = await item_cursor.to_list(length=limit)

    numReturn = len(ItemA)
    features = ItemA

    Dict = {'numberReturned':numReturn, 'features': features}
    return Dict

@stac_router.post("/dev/searchCloud", response_model=returnItems)
async def query_cloud_cover(cloudSearch: cloudSearch):
    """[summary]
    Search STAC items on cloud cover, bbox and date.
    [description]
    This is not the main search method.
    """
    limit = cloudSearch.limit
    if(cloudSearch.limit == None):
        limit = 10

    filter = {
        "bbox": {"$geoWithin": { "$box": [ [ cloudSearch.bbox[0], cloudSearch.bbox[1]], [cloudSearch.bbox[2], cloudSearch.bbox[3]]]}},
        "properties.datetime": { "$lt":cloudSearch.end_date, "$gte":cloudSearch.start_date}
    }
    filter2 = {
        "properties.eo:cloud_cover": { "$lt":cloudSearch.cloud_cover}
    }
    filter = {**filter, **filter2}
    collection_id = cloudSearch.collection_id

    col = await getDB(collection_id)

    count = await do_count(collection_id, filter, limit)
    item_cursor = col.find(filter).sort("properties.datetime")
    ItemA = await item_cursor.to_list(length=limit)

    features = ItemA

    if(count<limit):
        returned = count
    else:
        returned = limit
    Dict = {'numberMatched': count, 'numberReturned':returned, 'features': features}
    return Dict

@stac_router.post("/dev/addItem", response_model=str)
async def add_item(addItem: addItem):
    """[summary]
    Inserts a new item on the DB.
    [description]
    Endpoint to add a new item.
    """
    collection_id = addItem.collection

    if(collection_id == 'sentinel-s2-l2a-cogs' or collection_id == 'landsat-8-l1-c1'):
        return "cannot add to this collection"
    else:
        col = DB[collection_id]

    item = addItem.item
    with open('tester.json', 'w') as fp:
        json.dump(item, fp)

    stac = stac_validator.StacValidate('tester.json')
    stac.run()
    if stac.message[0]["valid_stac"] == False:
        return "not a valid stac item"
        
    exists = await col.count_documents({'_id': item['id']}) > 0
    if exists > 0:
        return "item already exists"
    else:
        item['_id']= item['id']
        item_op = await col.insert_one(item)
        return "item succesfully added"