# modules/analysis/com_analyzer.py
"""Center of Mass Analyzer - Uses Shapely for 2D, Trimesh for 3D"""

import numpy as np
from typing import Dict, Any, List, Tuple
from modules.geometry.shapes_2d import Shape2D
from modules.geometry.shapes_3d import Shape3D
from shapely.geometry import Polygon, Point, box as shapely_box
from shapely.ops import unary_union
import trimesh


class COMAnalyzer:
    """Center of Mass Analysis Engine with Boolean Operations"""
    
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
    
    def shape2d_to_shapely(self, shape: Shape2D):
        """Convert any 2D shape to a Shapely polygon"""
        if shape.__class__.__name__ == 'Rectangle':
            cx, cy = shape.get_centroid()
            w2, h2 = shape.width / 2, shape.height / 2
            return shapely_box(cx - w2, cy - h2, cx + w2, cy + h2)
        
        elif shape.__class__.__name__ == 'Circle':
            cx, cy = shape.get_centroid()
            return Point(cx, cy).buffer(shape.radius)
        
        elif shape.__class__.__name__ == 'Triangle':
            vertices = shape.get_vertices()
            return Polygon(vertices)
        
        elif shape.__class__.__name__ == 'Polygon':
            vertices = shape.get_vertices()
            return Polygon(vertices)
        
        else:
            # Generic: use vertices
            vertices = shape.get_vertices()
            return Polygon(vertices)
    
    def analyze_composite_2d(self, shapes: List[Shape2D], operations: List[str] = None) -> Dict[str, Any]:
        """
        Analyze composite 2D shapes with add/cut operations.
        Uses Shapely for proper boolean geometry.
        
        operations: list of 'add' or 'cut' for each shape
        """
        if operations is None:
            operations = ['add'] * len(shapes)
        
        if len(shapes) == 0:
            return {
                'total_area': 0,
                'centroid_x': 0,
                'centroid_y': 0,
                'components': [],
                'shapely_geometry': None
            }
        
        # Separate add and cut shapes
        add_shapes = []
        cut_shapes = []
        
        for shape, op in zip(shapes, operations):
            shapely_geom = self.shape2d_to_shapely(shape)
            if op == 'add':
                add_shapes.append(shapely_geom)
            else:
                cut_shapes.append(shapely_geom)
        
        # Start with union of all add shapes
        if add_shapes:
            result = unary_union(add_shapes)
        else:
            result = add_shapes[0] if add_shapes else None
        
        # Subtract all cut shapes
        if result is not None and cut_shapes:
            for cut_geom in cut_shapes:
                result = result.difference(cut_geom)
        
        # Handle edge cases
        if result is None or result.is_empty:
            return {
                'total_area': 0,
                'centroid_x': 0,
                'centroid_y': 0,
                'components': [],
                'shapely_geometry': None
            }
        
        # Get correct area and centroid from Shapely
        total_area = result.area
        centroid = result.centroid
        
        individual_results = []
        for i, (shape, op) in enumerate(zip(shapes, operations)):
            individual_results.append({
                'shape': shape.__class__.__name__,
                'area': shape.get_area(),
                'centroid': shape.get_centroid(),
                'operation': op
            })
        
        return {
            'total_area': total_area,
            'centroid_x': centroid.x,
            'centroid_y': centroid.y,
            'components': individual_results,
            'shapely_geometry': result  # Pass back for visualization
        }
    
    def shape3d_to_trimesh(self, shape: Shape3D):
        """Convert any 3D shape to a Trimesh object"""
        if shape.__class__.__name__ == 'Cube':
            cx, cy, cz = shape.get_centroid()
            l, w, h = shape.length, shape.width, shape.height
            return trimesh.creation.box(extents=(l, w, h), transform=trimesh.transformations.translation_matrix([cx, cy, cz]))
        
        elif shape.__class__.__name__ == 'Box':
            cx, cy, cz = shape.get_centroid()
            l, w, h = shape.length, shape.width, shape.height
            return trimesh.creation.box(extents=(l, w, h), transform=trimesh.transformations.translation_matrix([cx, cy, cz]))
        
        elif shape.__class__.__name__ == 'Sphere':
            cx, cy, cz = shape.get_centroid()
            mesh = trimesh.creation.icosphere(radius=shape.radius, subdivisions=3)
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Cylinder':
            cx, cy, cz = shape.get_centroid()
            mesh = trimesh.creation.cylinder(radius=shape.radius, height=shape.height, sections=32)
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Cone':
            cx, cy, cz = shape.get_centroid()
            mesh = trimesh.creation.cone(radius=shape.radius, height=shape.height, sections=32)
            mesh.apply_translation([cx, cy, cz - shape.height/4])  # Adjust for cone centroid offset
            return mesh
        
        elif shape.__class__.__name__ == 'Pyramid':
            # Create pyramid as a box
            cx, cy, cz = shape.get_centroid()
            bl, bw, h = shape.base_length, shape.base_width, shape.height
            # Use trimesh to create pyramid approximation
            vertices = np.array([
                [cx - bl/2, cy - bw/2, cz - h/2],
                [cx + bl/2, cy - bw/2, cz - h/2],
                [cx + bl/2, cy + bw/2, cz - h/2],
                [cx - bl/2, cy + bw/2, cz - h/2],
                [cx, cy, cz + h/2]  # apex
            ])
            faces = np.array([
                [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],
                [0, 1, 2], [0, 2, 3]  # base
            ])
            return trimesh.Trimesh(vertices=vertices, faces=faces)
        
        return None
    
    def analyze_3d(self, shape: Shape3D) -> Dict[str, Any]:
        """Analyze single 3D shape"""
        volume = shape.get_volume()
        centroid = shape.get_centroid()
        
        mass = volume  # density = 1
        
        return {
            'volume': volume,
            'mass': mass,
            'centroid_x': centroid[0],
            'centroid_y': centroid[1],
            'centroid_z': centroid[2],
            'shape_type': shape.__class__.__name__
        }
    
    def analyze_composite_3d(self, shapes: List[Shape3D], operations: List[str] = None) -> Dict[str, Any]:
        """
        Analyze composite 3D shapes with add/cut operations.
        Uses Trimesh for boolean geometry.
        """
        if operations is None:
            operations = ['add'] * len(shapes)
        
        if len(shapes) == 0:
            return {
                'total_volume': 0,
                'mass': 0,
                'centroid_x': 0,
                'centroid_y': 0,
                'centroid_z': 0,
                'trimesh_geometry': None
            }
        
        # Separate add and cut meshes
        add_meshes = []
        cut_meshes = []
        
        for shape, op in zip(shapes, operations):
            mesh = self.shape3d_to_trimesh(shape)
            if mesh is not None:
                if op == 'add':
                    add_meshes.append(mesh)
                else:
                    cut_meshes.append(mesh)
        
        # Start with union of all add meshes
        if add_meshes:
            result = add_meshes[0]
            for mesh in add_meshes[1:]:
                try:
                    result = result.union(mesh)
                except:
                    # Fallback: simple concatenation
                    result = trimesh.util.concatenate([result, mesh])
        else:
            return {
                'total_volume': 0,
                'mass': 0,
                'centroid_x': 0,
                'centroid_y': 0,
                'centroid_z': 0,
                'trimesh_geometry': None
            }
        
        # Subtract all cut meshes
        if cut_meshes:
            for cut_mesh in cut_meshes:
                try:
                    result = result.difference(cut_mesh)
                except:
                    pass  # Skip if boolean fails
        
        # Get volume and centroid from Trimesh
        if result is not None and result.volume > 0:
            total_volume = result.volume
            centroid = result.center_mass
        else:
            total_volume = 0
            centroid = [0, 0, 0]
        
        return {
            'total_volume': total_volume,
            'mass': total_volume,
            'centroid_x': centroid[0],
            'centroid_y': centroid[1],
            'centroid_z': centroid[2],
            'trimesh_geometry': result
        }