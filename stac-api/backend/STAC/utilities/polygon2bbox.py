import geojson

def bbox(coord_list):
     box = []
     for i in (0,1):
         res = sorted(coord_list, key=lambda x:x[i])
         box.append((res[0][i],res[-1][i]))
     ret = f"({box[0][0]} {box[1][0]}, {box[0][1]} {box[1][1]})"
     return ret

# obviously you need to parse your json here
poly=geojson.Polygon([[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.38, 57.322)]])
line = bbox(list(geojson.utils.coords(poly)))
print(line)
