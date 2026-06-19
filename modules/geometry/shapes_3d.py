# modules/geometry/shapes_3d.py
"""3D Geometry Classes"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, List


class Shape3D(ABC):
    """Abstract base class for 3D shapes"""
    
    def __init__(self):
        self.position = (0, 0, 0)
    
    @abstractmethod
    def get_volume(self) -> float:
        """Calculate volume of the shape"""
        pass
    
    @abstractmethod
    def get_centroid(self) -> Tuple[float, float, float]:
        """Calculate centroid coordinates"""
        pass
    
    def set_position(self, x: float, y: float, z: float):
        """Set shape position"""
        self.position = (x, y, z)


class Cube(Shape3D):
    """Cube shape"""
    
    def __init__(self, length: float, width: float, height: float, 
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.length = length
        self.width = width
        self.height = height
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return self.length * self.width * self.height
    
    def get_centroid(self) -> Tuple[float, float, float]:
        return self.position


class Box(Shape3D):
    """Box shape - rectangular prism (alias for Cube with clearer naming)"""
    
    def __init__(self, length: float, width: float, height: float,
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.length = length
        self.width = width
        self.height = height
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return self.length * self.width * self.height
    
    def get_centroid(self) -> Tuple[float, float, float]:
        return self.position


class Sphere(Shape3D):
    """Sphere shape"""
    
    def __init__(self, radius: float, pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.radius = radius
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return (4/3) * np.pi * self.radius ** 3
    
    def get_centroid(self) -> Tuple[float, float, float]:
        return self.position


class Cylinder(Shape3D):
    """Cylinder shape"""
    
    def __init__(self, radius: float, height: float, 
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.radius = radius
        self.height = height
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return np.pi * self.radius ** 2 * self.height
    
    def get_centroid(self) -> Tuple[float, float, float]:
        return self.position


class Cone(Shape3D):
    """Cone shape"""
    
    def __init__(self, radius: float, height: float,
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.radius = radius
        self.height = height
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return (1/3) * np.pi * self.radius ** 2 * self.height
    
    def get_centroid(self) -> Tuple[float, float, float]:
        # Centroid of cone is at h/4 from base
        cx, cy, cz = self.position
        return (cx, cy, cz + self.height / 4)


class Pyramid(Shape3D):
    """Pyramid shape with rectangular base"""
    
    def __init__(self, base_length: float, base_width: float, height: float,
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0):
        super().__init__()
        self.base_length = base_length
        self.base_width = base_width
        self.height = height
        self.set_position(pos_x, pos_y, pos_z)
    
    def get_volume(self) -> float:
        return (1/3) * self.base_length * self.base_width * self.height
    
    def get_centroid(self) -> Tuple[float, float, float]:
        # Centroid of pyramid is at h/4 from base
        cx, cy, cz = self.position
        return (cx, cy, cz + self.height / 4)