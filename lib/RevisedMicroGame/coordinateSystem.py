import math

DEBUG = False

class Vec2:
    def __init__(self, x=0.0, y=0.0, on_update=None):
        self._x = float(x)
        self._y = float(y)
        self.on_update = on_update
        if DEBUG: print(f"[Vec2] Created ({self._x}, {self._y})")

    # --- Properties ---
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = float(value)
        if self.on_update: self.on_update()

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = float(value)
        if self.on_update: self.on_update()
    
    @property
    def angle(self):
        """Angle in degrees (0° = right, 90° = down)"""
        return math.degrees(math.atan2(self.y, self.x))
    
    @angle.setter
    def angle(self, angle_degrees):
        """Set angle in degrees (0° = right, 90° = down), keeping magnitude."""
        mag = self.magnitude()
        theta = math.radians(angle_degrees)
        self.x = mag * math.cos(theta)
        self.y = mag * math.sin(theta)
        if self.on_update: self.on_update()
    
    @property
    def speed(self):
        return self.magnitude()
    @speed.setter
    def speed(self, new_speed):
        angle_rad = math.radians(self.angle)
        self.x = new_speed * math.cos(angle_rad)
        self.y = new_speed * math.sin(angle_rad)
        if self.on_update: self.on_update()

    # --- Operator Overloads (Immutable) ---
    def __add__(self, other: "Vec2") -> "Vec2":
        if DEBUG: print(f"[Vec2] Adding {self} + {other}")
        return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other: "Vec2") -> "Vec2":
        if DEBUG: print(f"[Vec2] Subtracting {self} - {other}")
        return Vec2(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar: float) -> "Vec2":
        if DEBUG: print(f"[Vec2] Multiplying {self} * {scalar}")
        return Vec2(self.x * scalar, self.y * scalar)
    def __rmul__(self, scalar: float) -> "Vec2":
        return self.__mul__(scalar)
    def __truediv__(self, scalar: float) -> "Vec2":
        if DEBUG: print(f"[Vec2] Dividing {self} / {scalar}")
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide Vector2 by zero.")
        return Vec2(self.x / scalar, self.y / scalar)
    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)

    # --- In-Place Operator Overloads (Mutable) ---
    def __iadd__(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self
    def __isub__(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self
    def __imul__(self, scalar: float) -> "Vec2":
        self.x *= scalar
        self.y *= scalar
        return self
    def __itruediv__(self, scalar: float) -> "Vec2":
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide Vector2 by zero.")
        self.x /= scalar
        self.y /= scalar
        return self

    # --- Comparisons ---
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec2):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    # --- Vector Operations ---
    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    def normalize(self) -> "Vec2":
        if DEBUG: print(f"[Vec2] Normalizing {self}")
        norm = self.magnitude()
        if norm != 0:
            self.x /= norm
            self.y /= norm
        return self  # Mutates self instead of returning a new Vector2
    def rotate(self, angle_degrees: float) -> "Vec2":
        if DEBUG: print(f"[Vec2] Rotating {self} by {angle_degrees} degrees")
        """Rotate vector by angle in degrees (counterclockwise, mutating)."""
        theta = math.radians(angle_degrees)
        c, s = math.cos(theta), math.sin(theta)
        x_new = c * self.x - s * self.y
        y_new = s * self.x + c * self.y
        self.x, self.y = x_new, y_new
        return self
    def perpendicular(self) -> "Vec2":
        """Return a new vector perpendicular to this one (90° CCW)."""
        return Vec2(-self.y, self.x)
    
    def clone(self) -> "Vec2":
        if DEBUG: print(f"[Vec2] Cloning {self}")
        return Vec2(self.x, self.y)
    
    def toInt(self) -> tuple[int,int]:
        return (int(self.x),int(self.y))
    # --- Representation ---
    def __repr__(self):
        return f"(x={self.x:.3f}, y={self.y:.3f})"

class VectorMapFactory:
    def __init__(self,x_map=lambda x:x,y_map=lambda y:y):
        if DEBUG: print("[VectorMapFactory] Created")
        self.x_map=x_map
        self.y_map=y_map

    def map(self,vec:Vec2)->Vec2:
        if DEBUG: print(f"[VectorMapFactory] Mapping {vec}")
        return Vec2(self.x_map(vec.x),self.y_map(vec.y))
    
    def __repr__(self):
        return f"VectorMapFactory(x_map={self.x_map}, y_map={self.y_map})"

