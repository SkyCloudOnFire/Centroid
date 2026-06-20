# modules/visualization/plotter_3d.py
"""3D Visualization with Plotly and Trimesh for solid bodies"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any
import trimesh


class Plotter3D:
    """3D Plotly-based visualization engine with Trimesh support"""
    
    def __init__(self):
        self.config = {
            'show_grid': True,
            'show_axes': True,
            'marker_size': 10
        }
    
    def _mesh_to_plotly(self, mesh: trimesh.Trimesh, color='lightblue', opacity=0.7, name='Mesh') -> go.Mesh3d:
        """Convert Trimesh object to Plotly Mesh3d trace"""
        vertices = mesh.vertices
        faces = mesh.faces
        
        return go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            opacity=opacity,
            name=name,
            color=color,
            flatshading=True,
            lighting=dict(
                ambient=0.4,
                diffuse=0.8,
                specular=0.3,
                roughness=0.5
            )
        )
    
    def _add_centroid_marker(self, fig, x: float, y: float, z: float, label: str = "Centroid"):
        """Add centroid marker to figure"""
        fig.add_trace(go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode='markers+text',
            name=label,
            marker=dict(
                color='red', 
                size=self.config['marker_size'],
                symbol='diamond',
                line=dict(color='darkred', width=2)
            ),
            text=[f"{label}\n({x:.1f}, {y:.1f}, {z:.1f})"],
            textposition="top center",
            textfont=dict(size=10, color='red')
        ))
    
    def _get_isometric_layout(self, title: str) -> dict:
        """Get standard isometric layout for engineering views"""
        return dict(
            title=title,
            scene=dict(
                xaxis_title="X (mm)",
                yaxis_title="Y (mm)",
                zaxis_title="Z (mm)",
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.8),  # True isometric
                    up=dict(x=0, y=0, z=1)
                ),
                xaxis=dict(showgrid=True, gridcolor='lightgray'),
                yaxis=dict(showgrid=True, gridcolor='lightgray'),
                zaxis=dict(showgrid=True, gridcolor='lightgray'),
            ),
            showlegend=True,
            template="plotly_white",
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='white',
        )
    
    def plot_3d_shape_with_centroid(self, shape, results: Dict[str, Any]) -> go.Figure:
        """Plot a single 3D shape as solid with centroid"""
        fig = go.Figure()
        
        # Convert shape to Trimesh and plot
        mesh = self._shape_to_trimesh(shape)
        
        if mesh is not None:
            fig.add_trace(self._mesh_to_plotly(
                mesh, 
                color='steelblue', 
                opacity=0.85, 
                name=shape.__class__.__name__
            ))
        else:
            # Fallback to old method
            self._plot_fallback(fig, shape)
        
        # Add centroid
        self._add_centroid_marker(
            fig,
            results['centroid_x'],
            results['centroid_y'],
            results['centroid_z']
        )
        
        # Isometric layout
        fig.update_layout(**self._get_isometric_layout(
            f"3D {shape.__class__.__name__} Analysis"
        ))
        
        return fig
    
    def plot_composite_3d(self, results: Dict[str, Any]) -> go.Figure:
        """
        Plot composite 3D result using Trimesh boolean geometry.
        Pass the results from COMAnalyzer.analyze_composite_3d()
        """
        fig = go.Figure()
        
        trimesh_geom = results.get('trimesh_geometry', None)
        
        if trimesh_geom is not None and isinstance(trimesh_geom, trimesh.Trimesh):
            if trimesh_geom.volume > 0:
                fig.add_trace(self._mesh_to_plotly(
                    trimesh_geom,
                    color='steelblue',
                    opacity=0.85,
                    name='Solid Body'
                ))
        
        # Add centroid
        if results.get('total_volume', 0) > 0:
            self._add_centroid_marker(
                fig,
                results['centroid_x'],
                results['centroid_y'],
                results['centroid_z'],
                label="Net Centroid"
            )
        
        # Isometric layout
        fig.update_layout(**self._get_isometric_layout(
            "Composite 3D Analysis"
        ))
        
        return fig
    
    def plot_mesh_with_centroid(self, mesh_data: Dict[str, Any]) -> go.Figure:
        """Plot an imported STL mesh with its centroid"""
        fig = go.Figure()
        
        vertices = np.array(mesh_data['vertices'])
        faces = np.array(mesh_data['faces'])
        
        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            opacity=0.85,
            name='Imported Mesh',
            color='steelblue',
            flatshading=True,
            lighting=dict(
                ambient=0.4,
                diffuse=0.8,
                specular=0.3,
                roughness=0.5
            )
        ))
        
        # Add centroid
        centroid = mesh_data['centroid']
        self._add_centroid_marker(
            fig,
            centroid[0],
            centroid[1],
            centroid[2],
            label="Centroid"
        )
        
        # Add bounding box wireframe
        if 'bounding_box' in mesh_data:
            self._add_bounding_box(fig, mesh_data['bounding_box'], centroid)
        
        # Isometric layout
        fig.update_layout(**self._get_isometric_layout(
            "STL Mesh Analysis"
        ))
        
        return fig
    
    def _shape_to_trimesh(self, shape) -> trimesh.Trimesh:
        """Convert a 3D shape to Trimesh object"""
        cx, cy, cz = shape.position
        
        if shape.__class__.__name__ == 'Cube':
            l, w, h = shape.length, shape.width, shape.height
            mesh = trimesh.creation.box(extents=(l, w, h))
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Box':
            l, w, h = shape.length, shape.width, shape.height
            mesh = trimesh.creation.box(extents=(l, w, h))
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Sphere':
            mesh = trimesh.creation.icosphere(radius=shape.radius, subdivisions=4)
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Cylinder':
            mesh = trimesh.creation.cylinder(radius=shape.radius, height=shape.height, sections=32)
            mesh.apply_translation([cx, cy, cz])
            return mesh
        
        elif shape.__class__.__name__ == 'Cone':
            mesh = trimesh.creation.cone(radius=shape.radius, height=shape.height, sections=32)
            mesh.apply_translation([cx, cy, cz - shape.height/4])
            return mesh
        
        elif shape.__class__.__name__ == 'Pyramid':
            bl, bw, h = shape.base_length, shape.base_width, shape.height
            vertices = np.array([
                [cx - bl/2, cy - bw/2, cz - h/2],
                [cx + bl/2, cy - bw/2, cz - h/2],
                [cx + bl/2, cy + bw/2, cz - h/2],
                [cx - bl/2, cy + bw/2, cz - h/2],
                [cx, cy, cz + h/2]
            ])
            faces = np.array([
                [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],
                [0, 2, 1], [0, 3, 2]
            ])
            return trimesh.Trimesh(vertices=vertices, faces=faces)
        
        return None
    
    def _add_bounding_box(self, fig, bbox_size, center):
        """Add a wireframe bounding box"""
        l, w, h = bbox_size
        cx, cy, cz = center
        
        x = [cx - l/2, cx + l/2, cx + l/2, cx - l/2, cx - l/2, cx + l/2, cx + l/2, cx - l/2]
        y = [cy - w/2, cy - w/2, cy + w/2, cy + w/2, cy - w/2, cy - w/2, cy + w/2, cy + w/2]
        z = [cz - h/2, cz - h/2, cz - h/2, cz - h/2, cz + h/2, cz + h/2, cz + h/2, cz + h/2]
        
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]
        
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[x[edge[0]], x[edge[1]]],
                y=[y[edge[0]], y[edge[1]]],
                z=[z[edge[0]], z[edge[1]]],
                mode='lines',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ))
    
    def _plot_fallback(self, fig, shape):
        """Fallback plotting for shapes without Trimesh support"""
        if shape.__class__.__name__ == 'Sphere':
            self._plot_sphere(fig, shape)
        elif shape.__class__.__name__ in ['Cube', 'Box']:
            self._plot_cube(fig, shape)
        elif shape.__class__.__name__ == 'Cylinder':
            self._plot_cylinder(fig, shape)
        elif shape.__class__.__name__ == 'Cone':
            self._plot_cone(fig, shape)
    
    def _plot_sphere(self, fig, shape):
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = shape.position[0] + shape.radius * np.cos(u) * np.sin(v)
        y = shape.position[1] + shape.radius * np.sin(u) * np.sin(v)
        z = shape.position[2] + shape.radius * np.cos(v)
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            colorscale='Blues',
            opacity=0.7,
            name='Sphere',
            showscale=False
        ))
    
    def _plot_cube(self, fig, shape):
        cx, cy, cz = shape.position
        if hasattr(shape, 'length'):
            l, w, h = shape.length, shape.width, shape.height
        else:
            l = w = h = getattr(shape, 'length', getattr(shape, 'width', 10))
        
        vertices = np.array([
            [cx-l/2, cy-w/2, cz-h/2], [cx+l/2, cy-w/2, cz-h/2],
            [cx+l/2, cy+w/2, cz-h/2], [cx-l/2, cy+w/2, cz-h/2],
            [cx-l/2, cy-w/2, cz+h/2], [cx+l/2, cy-w/2, cz+h/2],
            [cx+l/2, cy+w/2, cz+h/2], [cx-l/2, cy+w/2, cz+h/2]
        ])
        
        faces = np.array([
            [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
            [1, 2, 6], [1, 6, 5], [0, 3, 7], [0, 7, 4]
        ])
        
        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            opacity=0.7, name=shape.__class__.__name__, color='lightblue'
        ))
    
    def _plot_cylinder(self, fig, shape):
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(shape.position[2]-shape.height/2, 
                        shape.position[2]+shape.height/2, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x = shape.position[0] + shape.radius * np.cos(theta_grid)
        y = shape.position[1] + shape.radius * np.sin(theta_grid)
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z_grid,
            colorscale='Blues', opacity=0.7,
            name='Cylinder', showscale=False
        ))
    
    def _plot_cone(self, fig, shape):
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(shape.position[2]-shape.height/2, 
                        shape.position[2]+shape.height/2, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        r = shape.radius * (1 - (z_grid - shape.position[2] + shape.height/2) / shape.height)
        x = shape.position[0] + r * np.cos(theta_grid)
        y = shape.position[1] + r * np.sin(theta_grid)
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z_grid,
            colorscale='Blues', opacity=0.7,
            name='Cone', showscale=False
        ))