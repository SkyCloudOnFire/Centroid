# modules/analysis/com_analyzer.py
"""Center of Mass Analyzer"""

import numpy as np
from typing import Dict, Any, List, Tuple
from modules.geometry.shapes_2d import Shape2D
from modules.geometry.shapes_3d import Shape3D


class COMAnalyzer:
    """Center of Mass Analysis Engine"""
    
    def analyze_2d(self, shape: Shape2D) -> Dict[str, Any]:
        """Analyze single 2D shape"""
        area = shape.get_area()
        centroid = shape.get_centroid()
        
        return {
            'area': area,
            'centroid_x': centroid[0],
            'centroid_y': centroid[1],
            'shape_type': shape.__class__.__name__
        }
    
    def analyze_composite_2d(self, shapes: List[Shape2D]) -> Dict[str, Any]:
        """Analyze composite 2D shapes"""
        total_area = 0
        weighted_x = 0
        weighted_y = 0
        
        individual_results = []
        
        for shape in shapes:
            area = shape.get_area()
            centroid = shape.get_centroid()
            
            total_area += area
            weighted_x += area * centroid[0]
            weighted_y += area * centroid[1]
            
            individual_results.append({
                'shape': shape.__class__.__name__,
                'area': area,
                'centroid': centroid
            })
        
        if total_area > 0:
            centroid_x = weighted_x / total_area
            centroid_y = weighted_y / total_area
        else:
            centroid_x = centroid_y = 0
        
        return {
            'total_area': total_area,
            'centroid_x': centroid_x,
            'centroid_y': centroid_y,
            'components': individual_results
        }
    
    def analyze_3d(self, shape: Shape3D) -> Dict[str, Any]:
        """Analyze single 3D shape"""
        volume = shape.get_volume()
        centroid = shape.get_centroid()
        
        # Assume uniform density = 1
        mass = volume
        
        return {
            'volume': volume,
            'mass': mass,
            'centroid_x': centroid[0],
            'centroid_y': centroid[1],
            'centroid_z': centroid[2],
            'shape_type': shape.__class__.__name__
        }
    
    def analyze_composite_3d(self, shapes: List[Shape3D]) -> Dict[str, Any]:
        """Analyze composite 3D shapes"""
        total_volume = 0
        weighted_x = 0
        weighted_y = 0
        weighted_z = 0
        
        for shape in shapes:
            volume = shape.get_volume()
            centroid = shape.get_centroid()
            
            total_volume += volume
            weighted_x += volume * centroid[0]
            weighted_y += volume * centroid[1]
            weighted_z += volume * centroid[2]
        
        if total_volume > 0:
            centroid_x = weighted_x / total_volume
            centroid_y = weighted_y / total_volume
            centroid_z = weighted_z / total_volume
        else:
            centroid_x = centroid_y = centroid_z = 0
        
        return {
            'total_volume': total_volume,
            'mass': total_volume,  # density = 1
            'centroid_x': centroid_x,
            'centroid_y': centroid_y,
            'centroid_z': centroid_z
        }