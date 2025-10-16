from .collisionShape import Rect
from .coordinateSystem import Vec2
try:
    import ulab as np
except:
    import numpy as np
    
class SpatialHash:
    def __init__(self,width,height,numCols,numRows) -> None:
        self.Rect=Rect(Vec2(0,0),Vec2(width,height))
        self.numCols=numCols
        self.numRows=numRows
        self.tileSize=Vec2(width//numCols,height//numRows)
        self.create_buckets()
        
    def align(self,pos:Vec2):
        x=(pos.x//self.tileSize.x)*self.tileSize.x
        y=(pos.y//self.tileSize.y)*self.tileSize.y
        return Vec2(x,y)
    
    def get_rectilinear_Rect(self,Rect:Rect):
        local=self.tileSize

    def create_buckets(self):
        self.grid= [set() for _ in range(self.numRows*self.numCols)]
    
    def hash(self,pos:Vec2)->int:
        return int((pos.x//self.tileSize.x)+(pos.y//self.tileSize.y)*self.numCols)

    def rect_at_index(self,index:int):
        return Rect(Vec2(self.tileSize.x*(index%self.numCols),self.tileSize.y*(index//self.numRows)),self.tileSize)

    def add(self,item,Rect:Rect):
        indexes=[]
        for x,y in self.areaRange(Rect):
            index=self.flatten_local(x,y)
            self.grid[index].add(item)
            indexes.append(index)
        return indexes
    
    def remove(self,item,Rect:Rect):
        indexes=[]
        for x,y in self.areaRange(Rect):
            index=self.flatten_local(x,y)
            self.grid[index].discard(item)
            indexes.append(index)
        return indexes
    
    def areaRange(self,Rect:Rect):
        local=self.Rect_to_index_Rect(Rect)
        return self.local_areaRange(local)
    
    @staticmethod
    def local_areaRange(local):
        for x in range(local[0][0],local[1][0]+1):
            for y in range(local[0][1],local[1][1]+1):
                yield x,y

    def Rect_to_index_Rect(self,Rect:Rect):
        inside_Rect=Rect.clamp(self.Rect)
        pos=inside_Rect.pos
        end=inside_Rect.end
        return ((int(pos.x//self.tileSize.x),int(pos.y//self.tileSize.y)),
                (int(end.x//self.tileSize.x),int(end.y//self.tileSize.y)))

    def Rect_to_gridAligned_Rect(self,Rect:Rect):
        clone=Rect.clone()
        clone.pos=self.align(Rect.pos)
        end=clone.end
        end=self.align(end)
        clone.end=end
        return clone

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
        if type(key) is Rect:
            res=set()
            for x,y in self.areaRange(key):
                res.update(self.grid[self.flatten_local(x,y)])
            return list(res)            
        if type(key) is int:
            return self.grid[key]
        raise ValueError

    def __repr__(self):
        repr=""
        for y in range(self.numRows):
            
            for x in range(self.numCols):
                repr+="{:<15}".format(str(self.grid[x+y*self.numCols])[:15])+"|"
            repr+="\n"
        return repr

            