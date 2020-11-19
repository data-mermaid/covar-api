from .utils import return_date, do_count, getDB, bbox2poly, poly2bbox

def pagination(datetime, limit, page, collection_id, bbox=None, intersects=None, coordinates=None):
# def pagination(mainSearch, limit, page, collection_id):    
    searchStr = "http://discovery-cosmos.azurewebsites.net/stac/search"
    limitStr = "&limit=" +str(limit)
    next = searchStr +"?page=" + str(page + 1) +limitStr
    ''' Page pagination - START '''
    if(datetime and datetime != 'string' and bbox and bbox[0] != 0):
        # bbox = mainSearch.bbox
        # datetime = mainSearch.datetime
        bboxStr = "&bbox0=" +str(bbox[0]) +"&bbox1=" +str(bbox[1]) +"&bbox2=" +str(bbox[2]) +"&bbox3=" +str(bbox[3]) +"&collections=" +collection_id
        dateStr = "&datetime=" +datetime
        next = next +dateStr +bboxStr
    
        if(page > 2):
            prev = searchStr +"?page=" + str(page - 1) +limitStr +dateStr +bboxStr
        elif(page == 2):
            prev = searchStr +limitStr +dateStr +bboxStr
        else:
            prev = None
      
    elif(datetime and datetime != 'string' and intersects != None and intersects == 'Box'):
        if(intersects=="Box"):   
            bboxX = coordinates
            interStr = "&bbox0=" +str(bboxX[0]) +"&bbox1=" +str(bboxX[1]) +"&bbox2=" +str(bboxX[2]) +"&bbox3=" +str(bboxX[3]) +"&collections=" +collection_id
            dateStr = "&datetime=" +datetime
            next = next +dateStr +interStr
            # [[b0,b1],[b2,b1],[b2,b3],[b0,b3],[b0,b1]]
            if(page > 2):
                prev = searchStr +"?page=" + str(page - 1) +limitStr +dateStr +interStr
            elif(page == 2):
                prev = searchStr +limitStr +dateStr +interStr
            else:
                prev = None

    elif(datetime and datetime != 'string' and intersects != None and intersects == 'Polygon'):
        if(intersects=="Polygon"):   
            bboxX = poly2bbox(coordinates[0])
            interStr = "&bbox0=" +str(bboxX[0]) +"&bbox1=" +str(bboxX[1]) +"&bbox2=" +str(bboxX[2]) +"&bbox3=" +str(bboxX[3]) +"&collections=" +collection_id
            dateStr = "&datetime=" +datetime
            next = next +dateStr +interStr
            # [[b0,b1],[b2,b1],[b2,b3],[b0,b3],[b0,b1]]
            if(page > 2):
                prev = searchStr +"?page=" + str(page - 1) +limitStr +dateStr +interStr
            elif(page == 2):
                prev = searchStr +limitStr +dateStr +interStr
            else:
                prev = None

    elif(datetime and datetime != 'string' and intersects != None and intersects == "Point"):
        pointX = coordinates
        interStr = "&ptIntersectA=" +str(pointX[0]) +"&ptIntersectB=" +str(pointX[1]) +"&collections=" +collection_id
        dateStr = "&datetime=" +datetime
        next = next +dateStr +interStr
        # [[b0,b1],[b2,b1],[b2,b3],[b0,b3],[b0,b1]]
        if(page > 2):
            prev = searchStr +"?page=" + str(page - 1) +limitStr +dateStr +interStr
        elif(page == 2):
            prev = searchStr +limitStr +dateStr +interStr
        else:
            prev = None
    
    elif(datetime and datetime != 'string'):
        dateStr = "&datetime=" +datetime
        next = next +dateStr
        
        if(page > 2):
            prev = searchStr +"?page=" + str(page - 1) +limitStr +dateStr
        elif(page == 2):
            prev = searchStr +limitStr +dateStr
        else:
            prev = None
    else:   
        if(page > 2):
            prev = searchStr +"?page=" + str(page - 1) +limitStr
        elif(page == 2):
            prev = searchStr +limitStr
        else:
            prev = None

    linkedList = [prev, next]
    return linkedList