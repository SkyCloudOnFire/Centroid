# modules/geometry/shapes_2d.py
"""2D Geometry Classes"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, List


class Shape2D(ABC):
    """Abstract base class for 2D shapes"""
    
    def __init__(self):
        self.position = (0, 0)
    
    @abstractmethod
    def get_area(self) -> float:
        """Calculate area of the shape"""
        pass
    
    @abstractmethod
    def get_centroid(self) -> Tuple[float, float]:
        """Calculate centroid coordinates"""
        pass
    
    @abstractmethod
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Get vertices for plotting"""
        pass
    
    def set_position(self, x: float, y: float):
        """Set shape position"""
        self.position = (x, y)


class Rectangle(Shape2D):
    """Rectangle shape"""
    
    def __init__(self, width: float, height: float, center_x: float = 0, center_y: float = 0):
        super().__init__()
        self.width = width
        self.height = height
        self.set_position(center_x, center_y)
    
    def get_area(self) -> float:
        return self.width * self.height
    
    def get_centroid(self) -> Tuple[float, float]:
        return (self.position[0], self.position[1])
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        cx, cy = self.position
        w2, h2 = self.width / 2, self.height / 2
        return [
            (cx - w2, cy - h2),
            (cx + w2, cy - h2),
            (cx + w2, cy + h2),
            (cx - w2, cy + h2)
        ]


class Circle(Shape2D):
    """Circle shape"""
    
    def __init__(self, radius: float, center_x: float = 0, center_y: float = 0):
        super().__init__()
        self.radius = radius
        self.set_position(center_x, center_y)
    
    def get_area(self) -> float:
        return np.pi * self.radius ** 2
    
    def get_centroid(self) -> Tuple[float, float]:
        return (self.position[0], self.position[1])
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        # Generate points for circle approximation
        theta = np.linspace(0, 2 * np.pi, 100)
        x = self.position[0] + self.radius * np.cos(theta)
        y = self.position[1] + self.radius * np.sin(theta)
        return list(zip(x, y))


class Triangle(Shape2D):
    """Triangle shape"""
    
    def __init__(self, base: float, height: float, center_x: float = 0, center_y: float = 0):
        super().__init__()
        self.base = base
        self.height = height
        self.set_position(center_x, center_y)
    
    def get_area(self) -> float:
        return 0.5 * self.base * self.height
    
    def get_centroid(self) -> Tuple[float, float]:
        # Centroid of triangle is at 1/3 height from base
        cx = self.position[0]
        cy = self.position[1] + self.height / 3
        return (cx, cy)
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        cx, cy = self.position
        b2 = self.base / 2
        return [
            (cx, cy + self.height / 2),
            (cx - b2, cy - self.height / 2),
            (cx + b2, cy - self.height / 2)
        ]


class Polygon(Shape2D):
    """Custom polygon from coordinates"""
    
    def __init__(self, vertices: List[Tuple[float, float]]):
        super().__init__()
        self.vertices = vertices
    
    def get_area(self) -> float:
        """Calculate polygon area using shoelace formula"""
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        return 0.5 * abs(sum(x[i] * y[(i + 1) % len(y)] - x[(i + 1) % len(x)] * y[i] 
                            for i in range(len(x))))
    
    def get_centroid(self) -> Tuple[float, float]:
        """Calculate polygon centroid"""
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        n = len(x)
        
        area = self.get_area()
        if area == 0:
            return (0, 0)
        
        cx = sum((x[i] + x[(i + 1) % n]) * (x[i] * y[(i + 1) % n] - x[(i + 1) % n] * y[i]) 
                 for i in range(n)) / (6 * area)
        cy = sum((y[i] + y[(i + 1) % n]) * (x[i] * y[(i + 1) % n] - x[(i + 1) % n] * y[i]) 
                 for i in range(n)) / (6 * area)
        
        return (cx, cy)
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        return self.vertices