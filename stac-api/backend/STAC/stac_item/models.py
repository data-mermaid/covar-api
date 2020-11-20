# from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import json

class GeoJSON(BaseModel):
    """[summary]
        GeoJSON abstraction model.
    [description]
        Used to abstract out GeoJson fields.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    type: str = None
    coordinates: List = None

class STACSearch(BaseModel):
    """[summary]
        GeoJSON abstraction model.
    [description]
        Used to abstract out GeoJson fields.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    # count: int = None
    stac_version: str = None
    stac_extensions: List[str] = None
    type: str = Field(None, title="STAC item type", max_length=124)
    id: str = Field(None, title="id of STAC item", max_length=124)
    bbox: List[float] = None
    geometry: dict = None
    properties: dict = None
    collection: str = None
    links: List[dict] = None
    assets: dict = None

class addItem(BaseModel):
    collection: str = None
    item: dict = None

class metaModel(BaseModel):
    next: str = None
    previous: str = None
    count: int = None
    limit: int = None

class returnItems(BaseModel):
    numberMatched: int = None
    numberReturned: int = None
    type: str = "FeatureCollection"
    meta: metaModel = None
    features: List[STACSearch] = None

class RootGet(BaseModel):
    """[summary]
        Root collections.
    [description]
        Used to return root collections.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    title: str = None
    description: str = None
    links: List[dict] = None
    stac_version: str = None
    id: str = None

class sphereSearch(BaseModel):
    """[summary]
        Search dates.
    [description]
        Used to return root collections.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    limit: int = None
    collections: str = None
    point_coordinates: List[int] = None
    distance: int = None

class lessmoreModel(BaseModel):
    gt: int = None
    lt: int = None

class queryModel(BaseModel):
    """[summary]
        Search cloud cover, bbox, dates etc.
    [description]
        Used to return items.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    searchKey: str = None
    searchValStr: str = None
    searchValInt: lessmoreModel = None

class sortResults(BaseModel):
    field: str = None
    direction: str = None

class mainSearch(BaseModel):
    """[summary]
        Search cloud cover, bbox, dates etc.
    [description]
        Used to return items.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    bbox: List[float] = None
    datetime: str = None
    time: str = None
    intersects: GeoJSON = None
    collections: List[str] = None
    ids: List[str] = None
    limit: int = None
    properties: dict = None
    query: dict = None
    sortby: List[sortResults] = None

class cloudSearch(BaseModel):
    """[summary]
        Search cloud cover, bbox, dates.
    [description]
        Used to return items.
    Arguments:
        BaseModel {[type]} -- [description]
    """
    collection_id: str = None
    limit: int = None
    cloud_cover: int = None
    bbox: List[float] = None
    start_date: str = None
    end_date: str = None
