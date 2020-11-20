from typing import Any, Dict
from config.config import DB
from . import settings

async def return_date(datetime):
    x = datetime.split("/")
    start_date = x[0]
    end_date = x[1]
    if(start_date=='..'):
        start_date = '2016-10-01T00:00:00Z'
    if(end_date=='..'):
        end_date = '2020-12-01T12:31:12Z'
    return { "properties.datetime": { "$lt":end_date, "$gte":start_date} }

'''count documents - presently stops counting at 1000'''
async def do_count(collection_id, query, limit):
    # if limit<1000:
    #     limit = 1000
    limit = limit * 10
    col = await getDB(collection_id)
    n = await col.count_documents(query, limit=limit)
    return n

async def getDB(collection_id):
    if(collection_id == 'sentinel-s2-l2a-cogs'):
        col = DB.sentinel_cogs
    elif(collection_id == 'dhw'):
        col = DB.DHW
    elif(collection_id == 'npp'):
        col = DB.NPP
    elif(collection_id == 'water_pollution'):
        col = DB.water_pollution
    elif(collection_id == 'digitalglobe'):
        col = DB.digitalglobe
    elif(collection_id == 'sentinel-2-l1c'):
        col = DB.sentinel_cogs
    elif(collection_id == 'radarsat-1'):
        col = DB.radarsat1
    else:
        col = DB.landsat
    return col

# sentinel-s2-l2a-cogs sentinel-2-l1c radarsat-1
def bbox2poly(b0, b1, b2, b3):
    poly = [[
        [b0,b1],[b2,b1],[b2,b3],[b0,b3],[b0,b1]
    ]]
    return poly

def poly2bbox(example):
    # b0 = 1
    # b1 = 2
    # b2 = 3
    # b3 = 4
    # example = [[b0,b1],[b2,b1],[b2,b3],[b0,b3],[b0,b1]]
    # print(example[0][0])
    # print(example[0][1])
    # print(example[2][0])
    # print(example[2][1])

    bbox = [example[0][0], example[0][1], example[2][0], example[2][1]]

    return bbox
    # print(bbox)

async def generate_dynamic_links(item: Dict[str, Any]) -> Dict[str, Any]:
    self_url = None
    for link in item["links"]:
        if link["rel"] == "self":
            self_url = link["href"]
            break

    for asset_id, asset in item["assets"].items():
        item["links"].append({
                "title": asset.get("title"),
                "rel": "tms",
                "href": settings.TITILER_ENDPOINT + "/stac/tiles/{z}/{x}/{y}.png?url=" + self_url + "&asset=" + asset_id
            }
        )

        item["links"].append({
                "title": asset.get("title"),
                "rel": "numpy",
                "href": settings.TITILER_ENDPOINT + "/stac/tiles/{z}/{x}/{y}.npy?url=" + self_url + "&asset=" + asset_id
            }
        )
    return item