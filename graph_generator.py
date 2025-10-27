import random
import math
import json
from typing import Dict, Tuple, List

class GraphGenerator:
    """Generate realistic road network graphs for testing"""
    
    @staticmethod
    def generate_city_graph_with_osm(center_point: Tuple[float, float] = (28.6139, 77.2090), 
                                     distance: int = 2000,
                                     network_type: str = 'drive') -> Tuple[Dict, Dict, Dict]:
        """
        Generate a road network using real OpenStreetMap data
        
        Args:
            center_point: (latitude, longitude) of city center
            distance: radius in meters to fetch roads
            network_type: 'drive', 'walk', 'bike', or 'all'
            
        Returns:
            Tuple of (graph, positions, road_geometries)
        """
        try:
            import osmnx as ox
            import networkx as nx
            
            print(f"Fetching real road network from OpenStreetMap around {center_point}...")
            
            # Download street network from OpenStreetMap
            G = ox.graph_from_point(center_point, dist=distance, network_type=network_type, simplify=True)
            
            print(f"Downloaded {len(G.nodes)} nodes and {len(G.edges)} edges from OSM")
            
            # Convert to our format
            graph = {}
            positions = {}
            road_geometries = {}
            
            # Extract node positions
            for node, data in G.nodes(data=True):
                positions[str(node)] = (data['y'], data['x'])  # (lat, lon)
            
            # Extract edges with geometries
            for u, v, key, data in G.edges(keys=True, data=True):
                u_str = str(u)
                v_str = str(v)
                
                if u_str not in graph:
                    graph[u_str] = {}
                
                # Calculate distance and time
                length = data.get('length', 0) / 1000  # Convert to km
                
                # Estimate time based on speed limit or default speed
                maxspeed = data.get('maxspeed', 40)
                if isinstance(maxspeed, list):
                    maxspeed = maxspeed[0]
                if isinstance(maxspeed, str):
                    try:
                        maxspeed = int(maxspeed.split()[0])
                    except:
                        maxspeed = 40
                
                travel_time = (length / maxspeed) * 60  # minutes
                
                graph[u_str][v_str] = {
                    'distance': round(length, 3),
                    'time': round(travel_time, 2)
                }
                
                # Store geometry if available
                if 'geometry' in data:
                    edge_key = f"{u_str}_{v_str}"
                    coords = []
                    for point in data['geometry'].coords:
                        coords.append([point[1], point[0]])  # [lat, lon]
                    road_geometries[edge_key] = coords
                else:
                    # Use straight line if no geometry
                    edge_key = f"{u_str}_{v_str}"
                    road_geometries[edge_key] = [
                        [positions[u_str][0], positions[u_str][1]],
                        [positions[v_str][0], positions[v_str][1]]
                    ]
            
            print(f"Processed graph with {len(graph)} nodes")
            return graph, positions, road_geometries
            
        except ImportError:
            print("OSMnx not available, falling back to synthetic graph")
            return GraphGenerator.generate_city_graph()
        except Exception as e:
            print(f"Error fetching OSM data: {e}")
            print("Falling back to synthetic graph")
            return GraphGenerator.generate_city_graph()
    
    @staticmethod
    def generate_city_graph(num_nodes: int = 30, density: float = 0.3, 
                           city_center: Tuple[float, float] = (28.6139, 77.2090)) -> Tuple[Dict, Dict, Dict]:
        """
        Generate a realistic city road network graph (FALLBACK)
        
        Args:
            num_nodes: Number of intersections/nodes
            density: Connection density (0-1)
            city_center: (latitude, longitude) of city center
            
        Returns:
            Tuple of (graph, positions, road_geometries)
        """
        graph = {}
        positions = {}
        road_geometries = {}
        
        # Generate node positions in a realistic pattern
        lat_base, lon_base = city_center
        spread = 0.05  # ~5km spread
        
        for i in range(num_nodes):
            node_id = f"node_{i}"
            
            # Create clusters with some randomness
            cluster = i // (num_nodes // 4) if num_nodes >= 4 else 0
            cluster_offset_lat = (cluster % 2) * spread * 0.5
            cluster_offset_lon = (cluster // 2) * spread * 0.5
            
            lat = lat_base + cluster_offset_lat + random.uniform(-spread/2, spread/2)
            lon = lon_base + cluster_offset_lon + random.uniform(-spread/2, spread/2)
            
            positions[node_id] = (lat, lon)
            graph[node_id] = {}
        
        # Create connections based on proximity
        node_list = list(graph.keys())
        
        for i, node1 in enumerate(node_list):
            # Calculate distances to all other nodes
            distances = []
            for j, node2 in enumerate(node_list):
                if i != j:
                    dist = GraphGenerator._haversine_distance(
                        positions[node1], positions[node2]
                    )
                    distances.append((node2, dist))
            
            # Sort by distance and connect to nearest neighbors
            distances.sort(key=lambda x: x[1])
            num_connections = max(2, int(num_nodes * density * random.uniform(0.5, 1.5)))
            
            for node2, dist in distances[:num_connections]:
                if node2 not in graph[node1]:
                    # Calculate realistic travel time (assume 40 km/h average speed)
                    avg_speed_kmh = random.uniform(30, 50)
                    travel_time = (dist / avg_speed_kmh) * 60  # minutes
                    
                    # Add some randomness to simulate traffic
                    traffic_factor = random.uniform(0.9, 1.3)
                    
                    graph[node1][node2] = {
                        'distance': round(dist, 2),
                        'time': round(travel_time * traffic_factor, 2)
                    }
                    
                    # Store straight line geometry
                    edge_key = f"{node1}_{node2}"
                    road_geometries[edge_key] = [
                        [positions[node1][0], positions[node1][1]],
                        [positions[node2][0], positions[node2][1]]
                    ]
                    
                    # Make bidirectional with slight variations
                    graph[node2][node1] = {
                        'distance': round(dist, 2),
                        'time': round(travel_time * random.uniform(0.95, 1.05), 2)
                    }
                    
                    edge_key_reverse = f"{node2}_{node1}"
                    road_geometries[edge_key_reverse] = [
                        [positions[node2][0], positions[node2][1]],
                        [positions[node1][0], positions[node1][1]]
                    ]
        
        return graph, positions, road_geometries
    
    @staticmethod
    def _haversine_distance(coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            coord1: (latitude, longitude) of first point
            coord2: (latitude, longitude) of second point
            
        Returns:
            Distance in kilometers
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def get_sample_waypoints(positions: Dict[str, Tuple[float, float]], 
                            num_waypoints: int = 3) -> List[str]:
        """
        Get random waypoints from the graph
        
        Args:
            positions: Dictionary of node positions
            num_waypoints: Number of waypoints to return
            
        Returns:
            List of node IDs
        """
        nodes = list(positions.keys())
        if len(nodes) <= num_waypoints + 2:
            return random.sample(nodes[1:-1], max(0, len(nodes) - 2))
        return random.sample(nodes, num_waypoints)