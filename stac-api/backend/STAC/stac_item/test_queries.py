import os
import json
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


DB_CLIENT = AsyncIOMotorClient(
    host=os.environ.get("HOST"),
    port=int(os.environ.get("PORT")),
    username=os.environ.get("USER"),
    password=os.environ.get("PASSWORD"),
)

DB = DB_CLIENT["stac"]


async def query_collection(col, query):
    item_cursor = col.find(query)
    features = await item_cursor.to_list(length=10)
    return features


async def get_features_by_bbox(col, bbox, use_within=False):

    b0 = bbox[0]
    b1 = bbox[1]
    b2 = bbox[2]
    b3 = bbox[3]

    # original/counter-clockwise
    coords = [[[b0, b1], [b2, b1], [b2, b3], [b0, b3], [b0, b1]]]

    # clockwise
    # coords = [[[b0, b1], [b0, b3], [b2, b3], [b2, b1], [b0, b1]]]

    operator = "$geoWithin" if use_within else "$geoIntersects"

    query = {
        "geometry": {
            operator: {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": coords,
                    # NOTES: Uncomment below. This is suppose to fix the big polygon query issues
                    # "crs": {
                    #     "type": "name",
                    #     "properties": {
                    #         "name": "urn:x-mongodb:crs:strictwinding:EPSG:4326"
                    #     }
                    # }
                }
            }
        }
    }

    return await query_collection(col, query)


async def run_tests():

    # find by bbox
    bbox_same_size = [
        -178.739370079,
        -34.858702305,
        178.747602022,
        31.302876776
    ]
    result = await get_features_by_bbox(DB.water_pollution, bbox_same_size)
    print("bbox_same_size:", len(result))

    bbox_smaller = [
        -162.421875,
        -28.92163128242129,
        163.828125,
        25.799891182088334
    ]
    result = await get_features_by_bbox(DB.water_pollution, bbox_smaller)
    print("bbox_smaller:", len(result))

    bbox_smallest = [
        12.65625,
        7.013667927566642,
        15.468749999999998,
        9.102096738726456
    ]
    result = await get_features_by_bbox(DB.water_pollution, bbox_smallest)
    print("bbox_smallest:", len(result))

    bbox_outside = [
        64.6875,
        48.10743118848039,
        68.02734375,
        49.38237278700955
    ]
    result = await get_features_by_bbox(DB.water_pollution, bbox_outside)
    print("bbox_outside:", len(result))

    # find using within
    bbox_using_within = [
        -178.939370079,
        -34.958702305,
        178.947602022,
        31.502876776
    ]
    result = await get_features_by_bbox(
        DB.water_pollution,
        bbox_using_within, use_within=True
    )
    print("bbox_using_within:", len(result))

    # find by ids a.k.a sanity checks
    find_by_id_plum = {
        "id": {
            "$eq": "sed_plume_avg_cog"
        }
    }
    result = await query_collection(DB.water_pollution, find_by_id_plum)
    print("find_by_id_plum:", len(result))

    find_by_id_non_existing = {
        "id": {
            "$eq": "non_existing"
        }
    }
    result = await query_collection(
        DB.water_pollution,
        find_by_id_non_existing
    )
    print("find_by_id_non_existing:", len(result))


if __name__ == "__main__":
    # TO USE:
    # $ docker exec -it backend_stac_server_1 sh
    # $ python stac_item/test_queries.py

    loop = asyncio.get_event_loop()
    features = loop.run_until_complete(run_tests())
    loop.close()
