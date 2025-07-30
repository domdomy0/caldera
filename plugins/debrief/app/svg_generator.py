import math
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class SVGGenerator:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.fact_width = 800
        self.fact_height = 600
        
        # Load icon paths
        self.icon_paths = {
            'server': '/debrief/img/cloud.svg',
            'operation': '/debrief/img/operation.svg',
            'link': '/debrief/img/link.svg',
            'fact': '/debrief/img/star.svg',
            'darwin': '/debrief/img/darwin.svg',
            'windows': '/debrief/img/windows.svg',
            'linux': '/debrief/img/linux.svg',
            'tactic': '/debrief/img/tactic.svg',
            'technique_name': '/debrief/img/technique.svg',
        }
        
    def generate_svg(self, graph_data, graph_type):
        """Generate SVG from D3.js graph data"""
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])
        
        # Set dimensions based on graph type
        width = self.fact_width if graph_type == 'fact' else self.width
        height = self.fact_height if graph_type == 'fact' else self.height
        
        # Create SVG root element
        svg = Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg',
            'version': '1.1'
        })
        
        # Add background
        background = SubElement(svg, 'rect', {
            'width': str(width),
            'height': str(height),
            'fill': 'black'
        })
        
        # Create defs for markers and icons
        defs = SubElement(svg, 'defs')
        self._add_arrow_marker(defs, graph_type)
        self._load_icons(defs)
        
        # Calculate node positions using force simulation approximation
        positioned_nodes = self._calculate_positions(nodes, links, width, height)
        
        # Create main container group
        container = SubElement(svg, 'g', {'class': 'container'})
        graph_container = SubElement(container, 'g', {'class': 'graphContainer'})
        
        # Draw links
        self._draw_links(graph_container, links, positioned_nodes)
        
        # Draw nodes
        self._draw_nodes(graph_container, positioned_nodes)
        
        # Add legend
        self._add_legend(container, graph_data, width, height)
        
        # Convert to string
        rough_string = tostring(svg, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _calculate_positions(self, nodes, links, width, height):
        """Simple force simulation approximation for node positioning"""
        positioned_nodes = {}
        
        # Initialize positions
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            radius = min(width, height) / 4
            x = width / 2 + radius * math.cos(angle)
            y = height / 2 + radius * math.sin(angle)
            
            positioned_nodes[node['id']] = {
                **node,
                'x': x,
                'y': y
            }
        
        # Apply simple force simulation
        for iteration in range(50):  # 50 iterations
            # Repulsion between nodes
            for node_id, node in positioned_nodes.items():
                fx, fy = 0, 0
                for other_id, other in positioned_nodes.items():
                    if node_id != other_id:
                        dx = node['x'] - other['x']
                        dy = node['y'] - other['y']
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance > 0:
                            force = 1000 / (distance * distance)
                            fx += force * dx / distance
                            fy += force * dy / distance
                
                # Attraction to center
                center_x, center_y = width / 2, height / 2
                dx = center_x - node['x']
                dy = center_y - node['y']
                fx += dx * 0.001
                fy += dy * 0.001
                
                # Update position
                node['x'] += fx * 0.1
                node['y'] += fy * 0.1
                
                # Keep within bounds
                node['x'] = max(50, min(width - 50, node['x']))
                node['y'] = max(50, min(height - 50, node['y']))
        
        return positioned_nodes
    
    def _add_arrow_marker(self, defs, graph_type):
        """Add arrow marker for links"""
        marker = SubElement(defs, 'marker', {
            'id': f'arrowhead{graph_type}',
            'viewBox': '-0 -5 10 10',
            'refX': '30',
            'refY': '0',
            'orient': 'auto',
            'markerWidth': '8',
            'markerHeight': '8'
        })
        
        SubElement(marker, 'path', {
            'd': 'M 0,-5 L 10 ,0 L 0,5',
            'fill': '#999',
            'stroke': 'none'
        })
    
    def _load_icons(self, defs):
        """Load icon definitions"""
        # For now, create simple colored circles for different node types
        # In a full implementation, you'd load actual SVG icons
        colors = {
            'c2': '#ff6b6b',
            'operation': '#4ecdc4',
            'agent': '#45b7d1',
            'link': '#96ceb4',
            'fact': '#feca57',
            'tactic': '#ff9ff3',
            'technique_name': '#54a0ff'
        }
        
        for node_type, color in colors.items():
            circle = SubElement(defs, 'circle', {
                'id': f'{node_type}-icon',
                'r': '8',
                'fill': color
            })
    
    def _draw_links(self, container, links, positioned_nodes):
        """Draw links between nodes"""
        links_group = SubElement(container, 'g', {'class': 'links'})
        
        for link in links:
            source_node = positioned_nodes.get(link['source'])
            target_node = positioned_nodes.get(link['target'])
            
            if source_node and target_node:
                line = SubElement(links_group, 'line', {
                    'x1': str(source_node['x']),
                    'y1': str(source_node['y']),
                    'x2': str(target_node['x']),
                    'y2': str(target_node['y']),
                    'stroke': '#aaa',
                    'stroke-width': '2',
                    'class': f"link {link.get('type', '')}"
                })
    
    def _draw_nodes(self, container, positioned_nodes):
        """Draw nodes"""
        nodes_group = SubElement(container, 'g', {'class': 'nodes'})
        
        for node_id, node in positioned_nodes.items():
            node_group = SubElement(nodes_group, 'g', {
                'class': f"node {node.get('type', '')}",
                'transform': f"translate({node['x']},{node['y']})"
            })
            
            # Node circle
            circle = SubElement(node_group, 'circle', {
                'r': '16',
                'fill': '#efefef',
                'stroke': '#424242',
                'stroke-width': '1'
            })
            
            # Node icon (use colored circle for now)
            icon = SubElement(node_group, 'use', {
                'href': f"#{node.get('type', 'unknown')}-icon"
            })
            
            # Node label
            if node.get('name'):
                text = SubElement(node_group, 'text', {
                    'x': '18',
                    'y': '8',
                    'fill': 'white',
                    'font-size': '12px',
                    'class': 'label'
                })
                text.text = node['name']
    
    def _add_legend(self, container, graph_data, width, height):
        """Add legend to SVG"""
        legend_group = SubElement(container, 'g', {'class': 'legend'})
        
        # Legend background
        legend_rect = SubElement(legend_group, 'rect', {
            'x': str(width - 193),
            'y': '10',
            'width': '183',
            'height': '100',
            'rx': '6',
            'fill': 'rgba(170, 170, 170, 0.5)'
        })
        
        # Legend title
        title = SubElement(legend_group, 'text', {
            'x': str(width - 130),
            'y': '35',
            'fill': 'white',
            'font-weight': 'bold'
        })
        title.text = 'Legend'
        
        # Legend items (simplified)
        unique_types = set(node.get('type') for node in graph_data.get('nodes', []))
        for i, node_type in enumerate(unique_types):
            y_pos = 55 + i * 20
            
            # Icon
            icon = SubElement(legend_group, 'use', {
                'href': f'#{node_type}-icon',
                'x': str(width - 180),
                'y': str(y_pos)
            })
            
            # Label
            label = SubElement(legend_group, 'text', {
                'x': str(width - 160),
                'y': str(y_pos + 5),
                'fill': 'white',
                'font-size': '13px'
            })
            label.text = node_type.capitalize()