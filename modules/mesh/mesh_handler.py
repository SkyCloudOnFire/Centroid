# modules/mesh/mesh_handler.py
"""STL and mesh handling module"""

import numpy as np
import trimesh
from typing import Dict, Any, Tuple
import io


class MeshHandler:
    """Handle STL and mesh operations"""
    
    def load_stl(self, file_obj) -> Dict[str, Any]:
        """Load and analyze STL file"""
        try:
            # Read file bytes
            if isinstance(file_obj, str):
                # File path
                mesh = trimesh.load(file_obj)
            else:
                # File upload object
                file_bytes = file_obj.read()
                mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
            
            if not isinstance(mesh, trimesh.Trimesh):
                raise ValueError("Invalid STL file")
            
            # Calculate properties
            volume = mesh.volume
            centroid = mesh.center_mass
            
            # Get vertices and faces
            vertices = mesh.vertices
            faces = mesh.faces
            
            # Calculate additional statistics
            surface_area = mesh.area
            bounding_box = mesh.bounding_box.extents
            
            return {
                'volume': volume,
                'centroid': centroid,
                'surface_area': surface_area,
                'num_vertices': len(vertices),
                'num_faces': len(faces),
                'vertices': vertices.tolist(),
                'faces': faces.tolist(),
                'bounding_box': bounding_box.tolist(),
                'is_watertight': mesh.is_watertight,
                'is_convex': mesh.is_convex
            }
            
        except Exception as e:
            raise ValueError(f"Error processing STL file: {str(e)}")
    
    def validate_mesh(self, mesh_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate mesh for common issues"""
        issues = []
        
        if mesh_data['num_faces'] == 0:
            issues.append("Mesh has no faces")
        
        if mesh_data['volume'] <= 0:
            issues.append("Invalid or zero volume")
        
        if not mesh_data['is_watertight']:
            issues.append("Mesh is not watertight (has holes)")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Mesh is valid"