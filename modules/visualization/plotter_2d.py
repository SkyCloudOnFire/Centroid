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
        
        # Get vertices
        vertices = shape.get_vertices()
        x = [v[0] for v in vertices]
        y = [v[1] for v in vertices]
        
        # Close the shape
        x.append(x[0])
        y.append(y[0])
        
        # Plot shape
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name='Shape',
            line=dict(color='blue', width=2),
            fill='toself',
            fillcolor='rgba(0, 100, 200, 0.2)'
        ))
        
        # Plot centroid
        fig.add_trace(go.Scatter(
            x=[results['centroid_x']],
            y=[results['centroid_y']],
            mode='markers+text',
            name='Centroid',
            marker=dict(color='red', size=12, symbol='x'),
            text=[f"COM({results['centroid_x']:.2f}, {results['centroid_y']:.2f})"],
            textposition="top right"
        ))
        
        # Layout
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
    
    def plot_composite_with_centroid(self, shapes: List, results: Dict[str, Any]) -> go.Figure:
        """Plot composite 2D shapes with combined centroid"""
        fig = go.Figure()
        
        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        
        for i, shape in enumerate(shapes):
            vertices = shape.get_vertices()
            x = [v[0] for v in vertices]
            y = [v[1] for v in vertices]
            x.append(x[0])
            y.append(y[0])
            
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name=f'Component {i+1}',
                line=dict(color=colors[i % len(colors)], width=2),
                fill='toself',
                fillcolor=f'rgba({(i*50)%255}, {(i*100)%255}, {(i*150)%255}, 0.2)'
            ))
        
        # Plot combined centroid
        fig.add_trace(go.Scatter(
            x=[results['centroid_x']],
            y=[results['centroid_y']],
            mode='markers+text',
            name='Combined Centroid',
            marker=dict(color='red', size=14, symbol='x'),
            text=[f"COM({results['centroid_x']:.2f}, {results['centroid_y']:.2f})"],
            textposition="top right"
        ))
        
        fig.update_layout(
            title="Composite Shape Analysis",
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