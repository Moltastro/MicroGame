from .collisionShape import BBox
from .coordinateSystem import Vec2

class SpatialHash:
    def __init__(self,width,height,numCols,numRows) -> None:
        self.numCols=numCols
        self.numRows=numRows
        self.tileSize=Vec2(width//numCols,height//numRows)
        self.create_buckets()
        self.align=lambda x,y:((x//self.tileSize.x)*self.tileSize.x,(y//self.tileSize.y)*self.tileSize.y)
    def get_rectilinear_bbox(self,bbox:BBox):
        local=self.tileSize

    def create_buckets(self):
        self.grid= [set() for _ in range(self.numRows*self.numCols)]
    
    def hash(self,pos:Vec2)->int:
        return int((pos.x//self.tileSize.x)+(pos.y//self.tileSize.y)*self.numCols)

    def add(self,item,bbox:BBox):
        for x,y in self.areaRange(bbox):
            self.grid[self.flatten_local(x,y)].add(item)
    
    def remove(self,item,bbox:BBox):
        for x,y in self.areaRange(bbox):
            self.grid[self.flatten_local(x,y)].discard(item)
    
    def areaRange(self,bbox:BBox):
        local=self.bbox_to_index_bbox(bbox)
        return self.local_areaRange(local)
    
    @staticmethod
    def local_areaRange(local):
        for x in range(local[0][0],local[1][0]):
            for y in range(local[0][1],local[1][1]):
                yield x,y

    def bbox_to_index_bbox(self,bbox:BBox):
        pos=bbox.pos
        end=bbox.end
        return ((int(pos.x//self.tileSize.x),int(pos.y//self.tileSize.y)),
                (int(end.x//self.tileSize.x),int(end.y//self.tileSize.y)))

    def bbox_to_gridAligned_bbox(self,bbox:BBox):
        pos=Vec2(*self.align(bbox.pos.x,bbox.pos.y))
        clone=bbox.clone()
        clone.pos=pos
        end=clone.end
        end=end.move(*self.align(end.x,end.y))
        clone.end=end

    def flatten_local(self,x,y):
        return x+y*self.numCols 
    
    def get_with_local(self,localCoord):
        res=set()
        for x,y in self.local_areaRange(localCoord):
            res.update(self.grid[self.flatten_local(x,y)])
        return res
    def __getitem__(self,key):
        if type(key) is tuple:
            if len(key)>2:
                key=Vec2(key[0],key[1])
        if type(key) is Vec2:
            return self.grid[self.hash(key)]
        if type(key) is BBox:
            res=set()
            for x,y in self.areaRange(key):
                res.update(self.grid[self.flatten_local(x,y)])
            return list(res)            
        raise ValueError
