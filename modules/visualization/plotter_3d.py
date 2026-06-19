# modules/visualization/plotter_3d.py
"""3D Visualization with Plotly"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any


class Plotter3D:
    """3D Plotly-based visualization engine"""
    
    def __init__(self):
        self.config = {
            'show_grid': True,
            'show_axes': True,
            'marker_size': 10
        }
    
    def plot_3d_shape_with_centroid(self, shape, results: Dict[str, Any]) -> go.Figure:
        """Plot a 3D shape with its centroid"""
        fig = go.Figure()
        
        # Generate shape mesh based on type
        if shape.__class__.__name__ == 'Sphere':
            self._plot_sphere(fig, shape)
        elif shape.__class__.__name__ == 'Cube':
            self._plot_cube(fig, shape)
        elif shape.__class__.__name__ == 'Cylinder':
            self._plot_cylinder(fig, shape)
        elif shape.__class__.__name__ == 'Cone':
            self._plot_cone(fig, shape)
        
        # Plot centroid
        fig.add_trace(go.Scatter3d(
            x=[results['centroid_x']],
            y=[results['centroid_y']],
            z=[results['centroid_z']],
            mode='markers+text',
            name='Centroid',
            marker=dict(color='red', size=8),
            text=[f"COM({results['centroid_x']:.1f}, {results['centroid_y']:.1f}, {results['centroid_z']:.1f})"],
            textposition="top center"
        ))
        
        # Layout
        fig.update_layout(
            title="3D Shape Analysis",
            scene=dict(
                xaxis_title="X (mm)",
                yaxis_title="Y (mm)",
                zaxis_title="Z (mm)",
                aspectmode='data'
            ),
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def plot_mesh_with_centroid(self, mesh_data: Dict[str, Any]) -> go.Figure:
        """Plot a mesh with its centroid"""
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
            opacity=0.7,
            name='Mesh',
            color='lightblue'
        ))
        
        # Plot centroid
        centroid = mesh_data['centroid']
        fig.add_trace(go.Scatter3d(
            x=[centroid[0]],
            y=[centroid[1]],
            z=[centroid[2]],
            mode='markers+text',
            name='Centroid',
            marker=dict(color='red', size=8),
            text=[f"COM({centroid[0]:.1f}, {centroid[1]:.1f}, {centroid[2]:.1f})"],
            textposition="top center"
        ))
        
        fig.update_layout(
            title="Mesh Analysis",
            scene=dict(
                xaxis_title="X (mm)",
                yaxis_title="Y (mm)",
                zaxis_title="Z (mm)",
                aspectmode='data'
            ),
            template="plotly_white"
        )
        
        return fig
    
    def _plot_sphere(self, fig, shape):
        """Add sphere to figure"""
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
        """Add cube to figure using mesh3d"""
        cx, cy, cz = shape.position
        l, w, h = shape.length, shape.width, shape.height
        
        # Define 8 vertices of the cube
        vertices = np.array([
            [cx-l/2, cy-w/2, cz-h/2],
            [cx+l/2, cy-w/2, cz-h/2],
            [cx+l/2, cy+w/2, cz-h/2],
            [cx-l/2, cy+w/2, cz-h/2],
            [cx-l/2, cy-w/2, cz+h/2],
            [cx+l/2, cy-w/2, cz+h/2],
            [cx+l/2, cy+w/2, cz+h/2],
            [cx-l/2, cy+w/2, cz+h/2]
        ])
        
        # Define 12 triangles (2 per face)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 5, 6], [4, 6, 7],  # top
            [0, 1, 5], [0, 5, 4],  # front
            [2, 3, 7], [2, 7, 6],  # back
            [1, 2, 6], [1, 6, 5],  # right
            [0, 3, 7], [0, 7, 4]   # left
        ])
        
        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            opacity=0.7,
            name='Cube',
            color='lightblue'
        ))
    
    def _plot_cylinder(self, fig, shape):
        """Add cylinder to figure"""
        # Simplified cylinder representation
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(shape.position[2]-shape.height/2, 
                        shape.position[2]+shape.height/2, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        
        x = shape.position[0] + shape.radius * np.cos(theta_grid)
        y = shape.position[1] + shape.radius * np.sin(theta_grid)
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z_grid,
            colorscale='Blues',
            opacity=0.7,
            name='Cylinder',
            showscale=False
        ))
    
    def _plot_cone(self, fig, shape):
        """Add cone to figure"""
        # Simplified cone representation
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(shape.position[2]-shape.height/2, 
                        shape.position[2]+shape.height/2, 10)
        theta_grid, z_grid = np.meshgrid(theta, z)
        
        # Radius varies with height
        r = shape.radius * (1 - (z_grid - shape.position[2] + shape.height/2) / shape.height)
        
        x = shape.position[0] + r * np.cos(theta_grid)
        y = shape.position[1] + r * np.sin(theta_grid)
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z_grid,
            colorscale='Blues',
            opacity=0.7,
            name='Cone',
            showscale=False
        ))