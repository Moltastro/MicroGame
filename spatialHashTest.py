from lib.RevisedMicroGame.spatialHash import SpatialHash
from lib.RevisedMicroGame.collisionShape import BBox
from lib.RevisedMicroGame.coordinateSystem import Vec2
print("test")

hash=SpatialHash(16,16,4,4)
hash.add("Item1",BBox(Vec2(0,0),Vec2(9,9)))
print(hash.bbox_to_index_bbox(BBox(Vec2(0,0),Vec2(1,1))))
for x,y in hash.areaRange(BBox(Vec2(0,0),Vec2(1,1))):
    print(x,y)
print(hash)

hash_bbox=BBox(Vec2(0,0),Vec2(8,8))
item_bbox=BBox(Vec2(9,9),Vec2(9,9))
item_bbox.clamp(hash_bbox)
print(item_bbox)