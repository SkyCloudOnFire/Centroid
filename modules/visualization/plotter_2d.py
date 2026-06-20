# modules/visualization/plotter_2d.py
"""2D Visualization with Matplotlib for proper solid shapes with holes"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
from typing import List, Tuple, Dict, Any
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import MultiPolygon
import streamlit as st
from io import BytesIO


class Plotter2D:
    """2D Matplotlib-based visualization engine for solid shapes with holes"""
    
    def __init__(self):
        self.config = {
            'show_grid': True,
            'show_axes': True,
            'marker_size': 10,
            'marker_color': '#FF0000',
            'solid_color': '#4A90D9',
            'solid_alpha': 0.7,
            'edge_color': '#1a1a1a',
            'edge_width': 1.5,
            'cut_color': '#FFFFFF',
            'grid_color': '#CCCCCC',
            'bg_color': '#F8F9FA'
        }
    
    def _shapely_to_patches(self, geometry, color='#4A90D9', alpha=0.7, edge_color='#1a1a1a', edge_width=1.5):
        """Convert Shapely geometry to Matplotlib patches"""
        patches_list = []
        
        if geometry is None or geometry.is_empty:
            return patches_list
        
        # Handle MultiPolygon
        if geometry.geom_type == 'MultiPolygon':
            for geom in geometry.geoms:
                patches_list.extend(self._shapely_to_patches(geom, color, alpha, edge_color, edge_width))
            return patches_list
        
        # Handle single Polygon
        if geometry.geom_type == 'Polygon':
            # Exterior
            exterior_coords = list(geometry.exterior.coords)
            exterior_path = Path(exterior_coords, closed=True)
            
            # Interiors (holes)
            interiors = []
            for interior in geometry.interiors:
                hole_coords = list(interior.coords)
                interiors.append(hole_coords)
            
            # Create PathPatch with holes
            if interiors:
                # Matplotlib PathPatch with holes
                all_verts = exterior_coords
                codes = [Path.MOVETO] + [Path.LINETO] * (len(exterior_coords) - 1)
                
                for hole in interiors:
                    all_verts.extend(hole)
                    codes.extend([Path.MOVETO] + [Path.LINETO] * (len(hole) - 1))
                
                path = Path(all_verts, codes)
                patch = PathPatch(path, facecolor=color, edgecolor=edge_color, 
                                  linewidth=edge_width, alpha=alpha)
            else:
                # Simple polygon without holes
                patch = patches.Polygon(
                    exterior_coords, 
                    closed=True,
                    facecolor=color, 
                    edgecolor=edge_color,
                    linewidth=edge_width,
                    alpha=alpha
                )
            
            patches_list.append(patch)
        
        return patches_list
    
    def _create_figure(self, title="2D Analysis"):
        """Create a clean Matplotlib figure"""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
        fig.patch.set_facecolor(self.config['bg_color'])
        ax.set_facecolor(self.config['bg_color'])
        
        if self.config['show_grid']:
            ax.grid(True, alpha=0.3, color=self.config['grid_color'], linestyle='--', linewidth=0.5)
        
        if self.config['show_axes']:
            ax.axhline(y=0, color='#666666', linewidth=1, alpha=0.5)
            ax.axvline(x=0, color='#666666', linewidth=1, alpha=0.5)
        
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold', fontsize=14, pad=15)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        
        return fig, ax
    
    def _fig_to_bytes(self, fig) -> BytesIO:
        """Convert figure to bytes for Streamlit"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                    facecolor=fig.get_facecolor(), edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf
    
    def plot_shape_with_centroid(self, shape, results: Dict[str, Any]) -> bytes:
        """Plot a single 2D shape as a solid with centroid marker"""
        fig, ax = self._create_figure("Single Shape Analysis")
        
        # Get vertices
        vertices = shape.get_vertices()
        
        # Draw solid shape
        polygon = patches.Polygon(
            vertices, 
            closed=True,
            facecolor=self.config['solid_color'],
            edgecolor=self.config['edge_color'],
            linewidth=self.config['edge_width'],
            alpha=self.config['solid_alpha']
        )
        ax.add_patch(polygon)
        
        # Draw centroid
        cx, cy = results['centroid_x'], results['centroid_y']
        ax.plot(cx, cy, 'x', color=self.config['marker_color'], 
                markersize=self.config['marker_size'], markeredgewidth=3,
                label=f'Centroid ({cx:.2f}, {cy:.2f})')
        ax.legend(loc='upper right')
        
        # Auto-scale
        all_x = [v[0] for v in vertices]
        all_y = [v[1] for v in vertices]
        margin = max(max(all_x) - min(all_x), max(all_y) - min(all_y)) * 0.2 + 1
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        return self._fig_to_bytes(fig)
    
    def plot_composite_with_centroid(self, shapes: List, results: Dict[str, Any], operations: List[str] = None) -> bytes:
        """
        Plot composite 2D shapes as solid with holes.
        Uses Shapely geometry from results for proper hole rendering.
        """
        fig, ax = self._create_figure("Composite Shape Analysis")
        
        if operations is None:
            operations = ['add'] * len(shapes)
        
        # Check if we have Shapely geometry from analyzer
        shapely_geom = results.get('shapely_geometry', None)
        
        if shapely_geom is not None and not shapely_geom.is_empty:
            # Use Shapely geometry for perfect rendering with holes
            patches_list = self._shapely_to_patches(
                shapely_geom,
                color=self.config['solid_color'],
                alpha=self.config['solid_alpha'],
                edge_color=self.config['edge_color'],
                edge_width=self.config['edge_width']
            )
            
            for patch in patches_list:
                ax.add_patch(patch)
            
            # Auto-scale based on geometry bounds
            bounds = shapely_geom.bounds  # (minx, miny, maxx, maxy)
            margin = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 0.2 + 1
            ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
            ax.set_ylim(bounds[1] - margin, bounds[3] + margin)
        
        else:
            # Fallback: draw individual shapes
            all_x, all_y = [], []
            
            for shape, op in zip(shapes, operations):
                vertices = shape.get_vertices()
                x = [v[0] for v in vertices]
                y = [v[1] for v in vertices]
                all_x.extend(x)
                all_y.extend(y)
                
                if op == 'add':
                    polygon = patches.Polygon(
                        vertices, closed=True,
                        facecolor=self.config['solid_color'],
                        edgecolor=self.config['edge_color'],
                        linewidth=self.config['edge_width'],
                        alpha=self.config['solid_alpha']
                    )
                    ax.add_patch(polygon)
                else:
                    # Draw cut as white with dashed border
                    polygon = patches.Polygon(
                        vertices, closed=True,
                        facecolor='white',
                        edgecolor='red',
                        linewidth=self.config['edge_width'],
                        linestyle='--',
                        alpha=1.0
                    )
                    ax.add_patch(polygon)
            
            margin = max(max(all_x) - min(all_x), max(all_y) - min(all_y)) * 0.2 + 1
            ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
            ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        # Draw centroid
        if results['total_area'] > 0:
            cx, cy = results['centroid_x'], results['centroid_y']
            ax.plot(cx, cy, 'x', color=self.config['marker_color'],
                    markersize=self.config['marker_size'] + 4, markeredgewidth=3,
                    label=f'Net Centroid ({cx:.2f}, {cy:.2f})')
            ax.legend(loc='upper right')
        
        return self._fig_to_bytes(fig)
    
    def plot_polygon_with_centroid(self, coordinates: List[List[float]], results: Dict[str, Any]) -> bytes:
        """Plot a polygon as solid shape with centroid"""
        fig, ax = self._create_figure("Polygon Analysis")
        
        # Draw solid polygon
        polygon = patches.Polygon(
            coordinates, 
            closed=True,
            facecolor=self.config['solid_color'],
            edgecolor=self.config['edge_color'],
            linewidth=self.config['edge_width'],
            alpha=self.config['solid_alpha']
        )
        ax.add_patch(polygon)
        
        # Draw vertices
        x_coords = [c[0] for c in coordinates]
        y_coords = [c[1] for c in coordinates]
        ax.scatter(x_coords, y_coords, color='#333333', s=30, zorder=5, label='Vertices')
        
        # Draw centroid
        cx, cy = results['centroid_x'], results['centroid_y']
        ax.plot(cx, cy, 'x', color=self.config['marker_color'],
                markersize=self.config['marker_size'], markeredgewidth=3,
                label=f'Centroid ({cx:.2f}, {cy:.2f})')
        ax.legend(loc='upper right')
        
        # Auto-scale
        margin = max(max(x_coords) - min(x_coords), max(y_coords) - min(y_coords)) * 0.2 + 1
        ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
        ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
        return self._fig_to_bytes(fig)