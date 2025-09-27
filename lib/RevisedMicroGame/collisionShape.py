from typing import Self,TYPE_CHECKING # type: ignore
import math
from .coordinateSystem import Vec2
if TYPE_CHECKING:
    from .coordinateSystem import VectorMapFactory

class Shape:
    def __init__(self,pos:Vec2, on_update=lambda:None) -> None:
        super().__init__()
        self.pos=Vec2(0,0)
        self.pos.on_update=self._on_update
        self.on_update=on_update

    def transform(self,transform:VectorMapFactory):
        clone=self.clone()
        clone.pos=transform.map(self.pos)
        return clone
    
    def _on_update(self):
        self.on_update(self.clone())

    def overlaps(self, other: "Shape") -> bool:
        raise NotImplementedError

    # Helper methods for double-dispatch
    def overlaps_circle(self, circle: "Circle") -> bool:
        raise NotImplementedError

    def overlaps_square(self, square: Self) -> bool:
        raise NotImplementedError

    def clone(self) -> Self:
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, pos:Vec2, radius):
        super().__init__(pos)
        self.radius = radius

    def overlaps(self, other: Shape) -> bool:
        return other.overlaps_circle(self)

    def overlaps_circle(self, circle) -> bool:
        dx = self.pos.x - circle.pos.x
        dy = self.pos.y - circle.pos.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.radius + circle.radius

    def overlaps_square(self, square) -> bool:
        # Clamp circle center to square bounds
        closest_x = max(square.pos.x, min(self.pos.x, square.pos.x + square.size))
        closest_y = max(square.pos.y, min(self.pos.y, square.pos.y + square.size))
        dx = self.pos.x - closest_x
        dy = self.pos.y - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius
    
    def clone(self):
        return Circle(self.pos.clone(), self.radius)


class BBox(Shape):
    def __init__(self, pos:Vec2, dimensions:Vec2, on_update=lambda:None):
        super().__init__(pos,on_update)
        self.size=dimensions
        self.size.on_update=self._on_update

    def overlaps(self, other) -> bool:
        return other.overlaps_square(self)

    def overlaps_circle(self, circle) -> bool:
        # Reuse circle's logic (symmetry)
        return circle.overlaps_square(self)

    def overlaps_square(self, square) -> bool:
        return not (
            square.pos.x + square.dimensions.x < self.pos.x or
            square.pos.x > self.pos.x + self.size.x or
            square.pos.y + square.dimensions.x < self.pos.y or
            square.pos.y > self.pos.y + self.size.y
        )

    def clone(self):
        return BBox(self.pos.clone(), self.size.clone())

    def clamp(self, clamp_box: "BBox") -> "BBox":
        """
        Clamp this BBox inside the clamp_box.
        Modifies in place and returns self for chaining.
        """
        # Clamp position
        new_x = max(clamp_box.pos.x, min(self.pos.x, clamp_box.pos.x + clamp_box.size.x))
        new_y = max(clamp_box.pos.y, min(self.pos.y, clamp_box.pos.y + clamp_box.size.y))

        # Clamp size so the bbox does not exceed the clamp_box
        new_w = min(self.size.x, (clamp_box.pos.x + clamp_box.size.x) - new_x)
        new_h = min(self.size.y, (clamp_box.pos.y + clamp_box.size.y) - new_y)

        self.pos = Vec2(new_x, new_y)
        self.size = Vec2(new_w, new_h)
        return self

    def __repr__(self) -> str:
        return f"BBox: [pos {self.pos}, size {self.size}]"
