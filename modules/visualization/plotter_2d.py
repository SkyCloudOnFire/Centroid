# modules/visualization/plotter_2d.py
"""2D Visualization with Plotly"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Tuple, Dict, Any


class Plotter2D:
    """2D Plotly-based visualization engine"""
    
    def __init__(self):
        self.config = {
            'show_grid': True,
            'show_axes': True,
            'marker_size': 10,
            'marker_color': 'red'
        }
    
    def plot_shape_with_centroid(self, shape, results: Dict[str, Any]) -> go.Figure:
        """Plot a 2D shape with its centroid"""
        fig = go.Figure()
        
        vertices = shape.get_vertices()
        x = [v[0] for v in vertices]
        y = [v[1] for v in vertices]
        x.append(x[0])
        y.append(y[0])
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='Shape',
            line=dict(color='blue', width=2),
            fill='toself',
            fillcolor='rgba(0, 100, 200, 0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=[results['centroid_x']],
            y=[results['centroid_y']],
            mode='markers+text',
            name='Centroid',
            marker=dict(color='red', size=12, symbol='x'),
            text=[f"COM({results['centroid_x']:.2f}, {results['centroid_y']:.2f})"],
            textposition="top right"
        ))
        
        fig.update_layout(
            title="2D Shape Analysis",
            xaxis_title="X (mm)",
            yaxis_title="Y (mm)",
            showlegend=True,
            hovermode='closest',
            xaxis=dict(scaleanchor="y", scaleratio=1),
            template="plotly_white"
        )
        
        return fig
    
    def plot_composite_with_centroid(self, shapes: List, results: Dict[str, Any], operations: List[str] = None) -> go.Figure:
        """Plot composite 2D shapes with combined centroid and add/cut coloring"""
        fig = go.Figure()
        
        if operations is None:
            operations = ['add'] * len(shapes)
        
        for i, (shape, op) in enumerate(zip(shapes, operations)):
            vertices = shape.get_vertices()
            x = [v[0] for v in vertices]
            y = [v[1] for v in vertices]
            x.append(x[0])
            y.append(y[0])
            
            if op == 'add':
                color = 'rgba(0, 180, 100, 0.35)'  # Green for add
                line_color = 'green'
                name = f'Add: {shape.__class__.__name__}'
            else:
                color = 'rgba(255, 255, 255, 0.9)'  # White/empty for cut (hole)
                line_color = 'red'
                name = f'Cut: {shape.__class__.__name__}'
            
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name=name,
                line=dict(color=line_color, width=2, dash='dash' if op == 'cut' else 'solid'),
                fill='toself',
                fillcolor=color
            ))
        
        # Plot combined centroid
        if results['total_area'] > 0:
            fig.add_trace(go.Scatter(
                x=[results['centroid_x']],
                y=[results['centroid_y']],
                mode='markers+text',
                name='Net Centroid',
                marker=dict(color='red', size=14, symbol='x'),
                text=[f"COM({results['centroid_x']:.2f}, {results['centroid_y']:.2f})"],
                textposition="top right"
            ))
        
        fig.update_layout(
            title="Composite Shape Analysis (Green=Add, Red Dash=Cut)",
            xaxis_title="X (mm)",
            yaxis_title="Y (mm)",
            showlegend=True,
            xaxis=dict(scaleanchor="y", scaleratio=1),
            template="plotly_white"
        )
        
        return fig
    
    def plot_polygon_with_centroid(self, coordinates: List[List[float]], results: Dict[str, Any]) -> go.Figure:
        """Plot a polygon with its centroid"""
        fig = go.Figure()
        
        x = [c[0] for c in coordinates] + [coordinates[0][0]]
        y = [c[1] for c in coordinates] + [coordinates[0][1]]
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines+markers',
            name='Polygon',
            line=dict(color='blue', width=2),
            fill='toself',
            fillcolor='rgba(0, 100, 200, 0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=[results['centroid_x']],
            y=[results['centroid_y']],
            mode='markers+text',
            name='Centroid',
            marker=dict(color='red', size=12, symbol='x'),
            text=[f"COM({results['centroid_x']:.2f}, {results['centroid_y']:.2f})"],
            textposition="top right"
        ))
        
        fig.update_layout(
            title="Polygon Analysis",
            xaxis_title="X (mm)",
            yaxis_title="Y (mm)",
            showlegend=True,
            xaxis=dict(scaleanchor="y", scaleratio=1),
            template="plotly_white"
        )
        
        return fig