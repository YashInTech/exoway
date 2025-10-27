from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
from algorithms import RouteOptimizer
from graph_generator import GraphGenerator

app = Flask(__name__)
CORS(app)

# Global variables to store graph data
graph_data = None
positions_data = None
road_geometries = None
optimizer = None

def initialize_graph():
    """Initialize the graph with sample data"""
    global graph_data, positions_data, road_geometries, optimizer
    
    # Try to generate graph with real OSM data first
    print("Attempting to fetch real OpenStreetMap data...")
    graph_data, positions_data, road_geometries = GraphGenerator.generate_city_graph_with_osm(
        center_point=(28.6139, 77.2090),  # Delhi, India coordinates
        distance=2000,  # 2km radius
        network_type='drive'
    )
    
    # If OSM fails, it will automatically fallback to synthetic graph
    optimizer = RouteOptimizer(graph_data)
    print(f"Graph initialized with {len(graph_data)} nodes")

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Return the graph structure and positions"""
    if graph_data is None:
        initialize_graph()
    
    # Convert graph to serializable format
    serializable_graph = {}
    for node, neighbors in graph_data.items():
        serializable_graph[node] = {
            neighbor: {
                'distance': edge_data['distance'],
                'time': edge_data['time']
            }
            for neighbor, edge_data in neighbors.items()
        }
    
    return jsonify({
        'graph': serializable_graph,
        'positions': positions_data,
        'nodes': list(graph_data.keys())
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    """
    Optimize route using specified algorithm
    
    Expected JSON payload:
    {
        "algorithm": "dijkstra" | "astar" | "genetic",
        "start": "node_id",
        "end": "node_id",
        "waypoints": ["node_id1", "node_id2", ...],
        "metric": "distance" | "time"
    }
    """
    if graph_data is None:
        initialize_graph()
    
    data = request.get_json()
    algorithm = data.get('algorithm', 'dijkstra').lower()
    start = data.get('start')
    end = data.get('end')
    waypoints = data.get('waypoints', [])
    metric = data.get('metric', 'distance')
    
    # Validate inputs
    if not start or not end:
        return jsonify({'error': 'Start and end nodes are required'}), 400
    
    if start not in graph_data or end not in graph_data:
        return jsonify({'error': 'Invalid start or end node'}), 400
    
    try:
        if algorithm == 'dijkstra':
            path, cost, stats = optimizer.dijkstra(start, end, metric)
        elif algorithm == 'astar':
            path, cost, stats = optimizer.a_star(start, end, positions_data, metric)
        elif algorithm == 'genetic':
            path, cost, stats = optimizer.genetic_algorithm(
                start, end, waypoints, metric,
                population_size=50,
                generations=100,
                mutation_rate=0.2
            )
        else:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        # Calculate path coordinates
        path_coordinates = []
        if path:
            path_coordinates = [
                {'lat': positions_data[node][0], 'lon': positions_data[node][1], 'node': node}
                for node in path
            ]
        
        return jsonify({
            'path': path,
            'cost': cost,
            'metric': metric,
            'stats': stats,
            'coordinates': path_coordinates,
            'algorithm': algorithm
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    """
    Compare all three algorithms for the same route
    
    Expected JSON payload:
    {
        "start": "node_id",
        "end": "node_id",
        "waypoints": ["node_id1", "node_id2", ...],
        "metric": "distance" | "time"
    }
    """
    if graph_data is None:
        initialize_graph()
    
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    waypoints = data.get('waypoints', [])
    metric = data.get('metric', 'distance')
    
    # Validate inputs
    if not start or not end:
        return jsonify({'error': 'Start and end nodes are required'}), 400
    
    results = {}
    
    # Run Dijkstra
    try:
        path, cost, stats = optimizer.dijkstra(start, end, metric)
        results['dijkstra'] = {
            'path': path,
            'cost': cost,
            'stats': stats,
            'coordinates': [
                {'lat': positions_data[node][0], 'lon': positions_data[node][1], 'node': node}
                for node in path
            ] if path else []
        }
    except Exception as e:
        results['dijkstra'] = {'error': str(e)}
    
    # Run A*
    try:
        path, cost, stats = optimizer.a_star(start, end, positions_data, metric)
        results['astar'] = {
            'path': path,
            'cost': cost,
            'stats': stats,
            'coordinates': [
                {'lat': positions_data[node][0], 'lon': positions_data[node][1], 'node': node}
                for node in path
            ] if path else []
        }
    except Exception as e:
        results['astar'] = {'error': str(e)}
    
    # Run Genetic Algorithm (only if waypoints provided)
    if waypoints:
        try:
            path, cost, stats = optimizer.genetic_algorithm(
                start, end, waypoints, metric,
                population_size=50,
                generations=100,
                mutation_rate=0.2
            )
            results['genetic'] = {
                'path': path,
                'cost': cost,
                'stats': stats,
                'coordinates': [
                    {'lat': positions_data[node][0], 'lon': positions_data[node][1], 'node': node}
                    for node in path
                ] if path else []
            }
        except Exception as e:
            results['genetic'] = {'error': str(e)}
    
    return jsonify({
        'metric': metric,
        'results': results
    })

@app.route('/api/random-nodes', methods=['GET'])
def get_random_nodes():
    """Get random start, end, and waypoint nodes"""
    if graph_data is None:
        initialize_graph()
    
    num_waypoints = int(request.args.get('waypoints', 2))
    nodes = list(graph_data.keys())
    
    if len(nodes) < num_waypoints + 2:
        return jsonify({'error': 'Not enough nodes in graph'}), 400
    
    selected = random.sample(nodes, num_waypoints + 2)
    
    return jsonify({
        'start': selected[0],
        'end': selected[1],
        'waypoints': selected[2:]
    })

if __name__ == '__main__':
    initialize_graph()
    print("Starting Flask server...")
    print("Visit http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)