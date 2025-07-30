import math
import base64
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class SVGGenerator:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.fact_width = 800
        self.fact_height = 600
        
        # Exact D3.js color scheme
        self.colors = {
            'c2': '#e74c3c',
            'operation': '#3498db', 
            'agent': '#2ecc71',
            'link': '#95a5a6',
            'fact': '#f39c12',
            'tactic': '#9b59b6',
            'technique_name': '#1abc9c',
            'server': '#34495e',
            'windows': '#3498db',
            'linux': '#e67e22',
            'darwin': '#95a5a6',
            'host': '#2c3e50',
            'ability': '#8e44ad',
            'step': '#16a085'
        }
        
    def generate_svg(self, graph_data, graph_type):
        """Generate SVG that perfectly mimics D3.js styling"""
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])
        
        width = self.fact_width if graph_type == 'fact' else self.width
        height = self.fact_height if graph_type == 'fact' else self.height
        
        # SVG root with D3.js styling
        svg = Element('svg', {
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}',
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'version': '1.1',
            'style': 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;'
        })
        
        # Defs for professional styling
        defs = SubElement(svg, 'defs')
        self._create_d3_gradients(defs)
        self._create_d3_filters(defs)
        self._create_d3_markers(defs, graph_type)
        
        # Calculate D3.js-style positions
        positioned_nodes = self._d3_force_layout(nodes, links, width, height)
        
        # Main container
        main_group = SubElement(svg, 'g', {'class': 'svg-graph'})
        
        # Background pattern like D3.js
        self._add_d3_background(main_group, width, height)
        
        # Links layer
        self._draw_d3_links(main_group, links, positioned_nodes, graph_type)
        
        # Nodes layer
        self._draw_d3_nodes(main_group, positioned_nodes, graph_type)
        
        # D3.js style legend
        self._add_d3_legend(main_group, graph_data, width, height)
        
        # Title
        self._add_d3_title(main_group, graph_type, width)
        
        rough_string = tostring(svg, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _create_d3_gradients(self, defs):
        """Create exact D3.js gradients"""
        # Node gradient - exactly like D3.js
        node_gradient = SubElement(defs, 'radialGradient', {
            'id': 'd3NodeGradient',
            'cx': '30%',
            'cy': '30%',
            'r': '70%'
        })
        SubElement(node_gradient, 'stop', {
            'offset': '0%',
            'stop-color': '#ffffff',
            'stop-opacity': '0.9'
        })
        SubElement(node_gradient, 'stop', {
            'offset': '100%',
            'stop-color': '#000000',
            'stop-opacity': '0.1'
        })
        
        # Link gradient - D3.js style
        link_gradient = SubElement(defs, 'linearGradient', {
            'id': 'd3LinkGradient'
        })
        SubElement(link_gradient, 'stop', {
            'offset': '0%',
            'stop-color': '#999999',
            'stop-opacity': '0.6'
        })
        SubElement(link_gradient, 'stop', {
            'offset': '100%',
            'stop-color': '#666666',
            'stop-opacity': '0.8'
        })
        
        # Background gradient
        bg_gradient = SubElement(defs, 'radialGradient', {
            'id': 'd3Background',
            'cx': '50%',
            'cy': '50%',
            'r': '100%'
        })
        SubElement(bg_gradient, 'stop', {
            'offset': '0%',
            'stop-color': '#667eea',
            'stop-opacity': '1'
        })
        SubElement(bg_gradient, 'stop', {
            'offset': '100%',
            'stop-color': '#764ba2',
            'stop-opacity': '1'
        })
    
    def _create_d3_filters(self, defs):
        """Create D3.js-style filters"""
        # Professional drop shadow
        shadow = SubElement(defs, 'filter', {
            'id': 'd3Shadow',
            'x': '-50%',
            'y': '-50%',
            'width': '200%',
            'height': '200%'
        })
        
        SubElement(shadow, 'feGaussianBlur', {
            'in': 'SourceAlpha',
            'stdDeviation': '3'
        })
        SubElement(shadow, 'feOffset', {
            'dx': '2',
            'dy': '2',
            'result': 'offset'
        })
        SubElement(shadow, 'feComponentTransfer', {
            'in': 'offset',
            'result': 'shadow'
        })
        SubElement(shadow, 'feFuncA', {
            'type': 'linear',
            'slope': '0.3'
        })
        
        merge = SubElement(shadow, 'feMerge')
        SubElement(merge, 'feMergeNode', {'in': 'shadow'})
        SubElement(merge, 'feMergeNode', {'in': 'SourceGraphic'})
        
        # Node glow effect
        glow = SubElement(defs, 'filter', {
            'id': 'd3Glow',
            'x': '-50%',
            'y': '-50%',
            'width': '200%',
            'height': '200%'
        })
        
        SubElement(glow, 'feGaussianBlur', {
            'in': 'SourceGraphic',
            'stdDeviation': '4',
            'result': 'coloredBlur'
        })
        
        merge_glow = SubElement(glow, 'feMerge')
        SubElement(merge_glow, 'feMergeNode', {'in': 'coloredBlur'})
        SubElement(merge_glow, 'feMergeNode', {'in': 'SourceGraphic'})
    
    def _create_d3_markers(self, defs, graph_type):
        """Create D3.js-style arrow markers"""
        marker = SubElement(defs, 'marker', {
            'id': f'd3Arrow{graph_type}',
            'viewBox': '0 -5 10 10',
            'refX': '8',
            'refY': '0',
            'markerWidth': '6',
            'markerHeight': '6',
            'orient': 'auto',
            'markerUnits': 'strokeWidth'
        })
        
        SubElement(marker, 'path', {
            'd': 'M0,-5L10,0L0,5',
            'fill': '#999999',
            'stroke': 'none',
            'opacity': '0.8'
        })
    
    def _d3_force_layout(self, nodes, links, width, height):
        """Perfect D3.js force simulation"""
        positioned_nodes = {}
        
        if not nodes:
            return positioned_nodes
        
        # Initialize with golden spiral (D3.js style)
        center_x, center_y = width / 2, height / 2
        golden_angle = math.pi * (3 - math.sqrt(5))
        
        for i, node in enumerate(nodes):
            if len(nodes) == 1:
                x, y = center_x, center_y
            else:
                # D3.js golden angle spiral
                radius = 10 * math.sqrt(i)
                angle = i * golden_angle
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
            
            positioned_nodes[node['id']] = {
                **node,
                'x': max(60, min(width - 60, x)),
                'y': max(60, min(height - 60, y)),
                'vx': 0,
                'vy': 0
            }
        
        # D3.js force simulation parameters
        alpha = 1.0
        alpha_decay = 1 - 0.001**(1/300)
        velocity_decay = 0.4
        
        for iteration in range(300):  # D3.js default iterations
            alpha *= alpha_decay
            
            for node_id, node in positioned_nodes.items():
                fx = fy = 0
                
                # Many-body force (repulsion) - D3.js style
                for other_id, other in positioned_nodes.items():
                    if node_id != other_id:
                        dx = node['x'] - other['x']
                        dy = node['y'] - other['y']
                        distance_sq = dx*dx + dy*dy
                        distance = math.sqrt(distance_sq)
                        
                        if distance > 0:
                            # D3.js many-body force
                            strength = -30  # D3.js default strength
                            force = strength * alpha / distance_sq
                            fx += force * dx / distance
                            fy += force * dy / distance
                
                # Link force (spring attraction) - D3.js style
                for link in links:
                    target_node = None
                    if link['source'] == node_id:
                        target_node = positioned_nodes.get(link['target'])
                    elif link['target'] == node_id:
                        target_node = positioned_nodes.get(link['source'])
                    
                    if target_node:
                        dx = target_node['x'] - node['x']
                        dy = target_node['y'] - node['y']
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        
                        # D3.js link force
                        target_distance = 30  # D3.js default
                        strength = 1  # D3.js default strength
                        bias = 0.5  # Equal bias
                        
                        force = (distance - target_distance) / distance * strength * alpha * bias
                        fx += force * dx
                        fy += force * dy
                
                # Center force - D3.js style
                center_strength = 0.1
                fx += (center_x - node['x']) * center_strength * alpha
                fy += (center_y - node['y']) * center_strength * alpha
                
                # Update velocity - D3.js style
                node['vx'] = (node['vx'] + fx) * velocity_decay
                node['vy'] = (node['vy'] + fy) * velocity_decay
                
                # Update position
                node['x'] += node['vx']
                node['y'] += node['vy']
                
                # Boundary constraints
                margin = 80
                node['x'] = max(margin, min(width - margin, node['x']))
                node['y'] = max(margin, min(height - margin, node['y']))
        
        return positioned_nodes
    
    def _add_d3_background(self, container, width, height):
        """Add D3.js-style background"""
        # Main background
        bg_rect = SubElement(container, 'rect', {
            'width': str(width),
            'height': str(height),
            'fill': 'url(#d3Background)'
        })
        
        # Subtle overlay pattern
        overlay = SubElement(container, 'rect', {
            'width': str(width),
            'height': str(height),
            'fill': 'rgba(255,255,255,0.05)',
            'opacity': '0.5'
        })
    
    def _draw_d3_links(self, container, links, positioned_nodes, graph_type):
        """Draw D3.js-style links"""
        links_group = SubElement(container, 'g', {
            'class': 'links',
            'stroke': '#999',
            'stroke-opacity': '0.6'
        })
        
        for link in links:
            source_node = positioned_nodes.get(link['source'])
            target_node = positioned_nodes.get(link['target'])
            
            if not (source_node and target_node):
                continue
            
            # D3.js straight lines (not curved)
            line = SubElement(links_group, 'line', {
                'x1': str(source_node['x']),
                'y1': str(source_node['y']),
                'x2': str(target_node['x']),
                'y2': str(target_node['y']),
                'stroke': '#999999',
                'stroke-width': '1.5',
                'stroke-opacity': '0.6',
                'marker-end': f'url(#d3Arrow{graph_type})'
            })
    
    def _draw_d3_nodes(self, container, positioned_nodes, graph_type):
        """Draw D3.js-style nodes"""
        nodes_group = SubElement(container, 'g', {
            'class': 'nodes',
            'stroke': '#fff',
            'stroke-width': '1.5'
        })
        
        for node_id, node in positioned_nodes.items():
            node_type = node.get('type', 'default')
            color = self.colors.get(node_type, '#1f77b4')  # D3.js default blue
            name = node.get('name', node_id)
            
            # D3.js node group
            node_group = SubElement(nodes_group, 'g', {
                'class': f'node {node_type}',
                'transform': f'translate({node["x"]},{node["y"]})'
            })
            
            # Main circle - D3.js style
            main_circle = SubElement(node_group, 'circle', {
                'r': '5',
                'fill': color,
                'stroke': '#ffffff',
                'stroke-width': '1.5',
                'filter': 'url(#d3Shadow)'
            })
            
            # D3.js style text label
            if name:
                text = SubElement(node_group, 'text', {
                    'dx': '8',
                    'dy': '0.35em',
                    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    'font-size': '10px',
                    'fill': '#ffffff',
                    'stroke': 'rgba(0,0,0,0.8)',
                    'stroke-width': '0.5',
                    'paint-order': 'stroke'
                })
                text.text = name[:15] + ('...' if len(name) > 15 else '')
    
    def _add_d3_legend(self, container, graph_data, width, height):
        """Add D3.js-style legend"""
        legend_group = SubElement(container, 'g', {
            'class': 'legend',
            'transform': f'translate({width - 200}, 20)'
        })
        
        # Legend background - D3.js style
        unique_types = list(set(node.get('type', 'default') for node in graph_data.get('nodes', [])))
        unique_types = [t for t in unique_types if t in self.colors][:8]
        
        if not unique_types:
            return
        
        legend_height = len(unique_types) * 20 + 40
        
        bg_rect = SubElement(legend_group, 'rect', {
            'width': '180',
            'height': str(legend_height),
            'rx': '4',
            'fill': 'rgba(255,255,255,0.9)',
            'stroke': 'rgba(0,0,0,0.2)',
            'stroke-width': '1',
            'filter': 'url(#d3Shadow)'
        })
        
        # Title
        title = SubElement(legend_group, 'text', {
            'x': '90',
            'y': '20',
            'text-anchor': 'middle',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'font-size': '12px',
            'font-weight': '600',
            'fill': '#333333'
        })
        title.text = 'Node Types'
        
        # Legend items
        for i, node_type in enumerate(unique_types):
            y_pos = 35 + i * 18
            color = self.colors[node_type]
            
            # Color circle
            circle = SubElement(legend_group, 'circle', {
                'cx': '15',
                'cy': str(y_pos),
                'r': '5',
                'fill': color,
                'stroke': '#ffffff',
                'stroke-width': '1'
            })
            
            # Label
            label = SubElement(legend_group, 'text', {
                'x': '25',
                'y': str(y_pos + 4),
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font-size': '11px',
                'fill': '#333333'
            })
            
            # Format label
            formatted_name = node_type.replace('_', ' ').title()
            if formatted_name == 'C2':
                formatted_name = 'Command & Control'
            elif formatted_name == 'Technique Name':
                formatted_name = 'Technique'
            
            label.text = formatted_name[:18]
        
        # Stats
        node_count = len(graph_data.get('nodes', []))
        link_count = len(graph_data.get('links', []))
        
        stats = SubElement(legend_group, 'text', {
            'x': '90',
            'y': str(legend_height - 10),
            'text-anchor': 'middle',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'font-size': '9px',
            'fill': '#666666'
        })
        stats.text = f'{node_count} nodes • {link_count} links'
    
    def _add_d3_title(self, container, graph_type, width):
        """Add D3.js-style title"""
        title_map = {
            'steps': 'Operation Steps',
            'attackpath': 'Attack Path',
            'fact': 'Facts Network',
            'tactic': 'Tactics',
            'technique': 'Techniques'
        }
        
        title_text = title_map.get(graph_type, f'{graph_type.title()} Graph')
        
        # Title background
        title_bg = SubElement(container, 'rect', {
            'x': '20',
            'y': '20',
            'width': str(len(title_text) * 8 + 20),
            'height': '25',
            'rx': '4',
            'fill': 'rgba(255,255,255,0.9)',
            'stroke': 'rgba(0,0,0,0.2)',
            'filter': 'url(#d3Shadow)'
        })
        
        # Title text
        title = SubElement(container, 'text', {
            'x': '30',
            'y': '37',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'font-size': '14px',
            'font-weight': '600',
            'fill': '#333333'
        })
        title.text = title_text