import heapq
import math
import random
from typing import List, Dict, Tuple, Optional
import time

class RouteOptimizer:
    """Main class for route optimization algorithms"""
    
    def __init__(self, graph: Dict[str, Dict[str, Dict[str, float]]]):
        """
        Initialize with a graph structure.
        Graph format: {node_id: {neighbor_id: {'distance': float, 'time': float}, ...}, ...}
        """
        self.graph = graph
        self.nodes = list(graph.keys())
        
    def heuristic(self, node1: str, node2: str, positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate Euclidean distance heuristic for A*"""
        x1, y1 = positions[node1]
        x2, y2 = positions[node2]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def dijkstra(self, start: str, end: str, metric: str = 'distance') -> Tuple[List[str], float, Dict]:
        """
        Dijkstra's algorithm for shortest path
        
        Args:
            start: Starting node ID
            end: Destination node ID
            metric: 'distance' or 'time' to optimize for
            
        Returns:
            Tuple of (path, cost, stats)
        """
        start_time = time.time()
        
        # Priority queue: (cost, node, path)
        pq = [(0, start, [start])]
        visited = set()
        costs = {start: 0}
        nodes_explored = 0
        
        while pq:
            current_cost, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            nodes_explored += 1
            
            if current_node == end:
                execution_time = time.time() - start_time
                return path, current_cost, {
                    'nodes_explored': nodes_explored,
                    'execution_time': execution_time,
                    'algorithm': 'Dijkstra'
                }
            
            if current_node not in self.graph:
                continue
                
            for neighbor, edge_data in self.graph[current_node].items():
                if neighbor not in visited:
                    cost = edge_data.get(metric, float('inf'))
                    new_cost = current_cost + cost
                    
                    if neighbor not in costs or new_cost < costs[neighbor]:
                        costs[neighbor] = new_cost
                        heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
        
        execution_time = time.time() - start_time
        return [], float('inf'), {
            'nodes_explored': nodes_explored,
            'execution_time': execution_time,
            'algorithm': 'Dijkstra',
            'error': 'No path found'
        }
    
    def a_star(self, start: str, end: str, positions: Dict[str, Tuple[float, float]], 
               metric: str = 'distance') -> Tuple[List[str], float, Dict]:
        """
        A* algorithm for shortest path with heuristic
        
        Args:
            start: Starting node ID
            end: Destination node ID
            positions: Dictionary mapping node IDs to (lat, lon) coordinates
            metric: 'distance' or 'time' to optimize for
            
        Returns:
            Tuple of (path, cost, stats)
        """
        start_time = time.time()
        
        # Priority queue: (f_score, g_score, node, path)
        pq = [(0, 0, start, [start])]
        visited = set()
        g_scores = {start: 0}
        nodes_explored = 0
        
        while pq:
            f_score, g_score, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            nodes_explored += 1
            
            if current_node == end:
                execution_time = time.time() - start_time
                return path, g_score, {
                    'nodes_explored': nodes_explored,
                    'execution_time': execution_time,
                    'algorithm': 'A*'
                }
            
            if current_node not in self.graph:
                continue
                
            for neighbor, edge_data in self.graph[current_node].items():
                if neighbor not in visited:
                    cost = edge_data.get(metric, float('inf'))
                    tentative_g = g_score + cost
                    
                    if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                        g_scores[neighbor] = tentative_g
                        h_score = self.heuristic(neighbor, end, positions)
                        f_score = tentative_g + h_score
                        heapq.heappush(pq, (f_score, tentative_g, neighbor, path + [neighbor]))
        
        execution_time = time.time() - start_time
        return [], float('inf'), {
            'nodes_explored': nodes_explored,
            'execution_time': execution_time,
            'algorithm': 'A*',
            'error': 'No path found'
        }
    
    def genetic_algorithm(self, start: str, end: str, intermediate_points: List[str],
                         metric: str = 'distance', population_size: int = 50, 
                         generations: int = 100, mutation_rate: float = 0.2) -> Tuple[List[str], float, Dict]:
        """
        Genetic Algorithm for route optimization with waypoints
        
        Args:
            start: Starting node ID
            end: Destination node ID
            intermediate_points: List of waypoints to visit
            metric: 'distance' or 'time' to optimize for
            population_size: Number of chromosomes in population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            
        Returns:
            Tuple of (path, cost, stats)
        """
        start_time = time.time()
        
        if not intermediate_points:
            # If no intermediate points, just use Dijkstra
            return self.dijkstra(start, end, metric)
        
        # Create initial population of random orderings
        population = []
        for _ in range(population_size):
            chromosome = intermediate_points.copy()
            random.shuffle(chromosome)
            population.append(chromosome)
        
        best_fitness = float('inf')
        best_chromosome = None
        generation_stats = []
        
        for gen in range(generations):
            # Evaluate fitness for each chromosome
            fitness_scores = []
            for chromosome in population:
                fitness = self._evaluate_route_fitness([start] + chromosome + [end], metric)
                fitness_scores.append(fitness)
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_chromosome = chromosome.copy()
            
            generation_stats.append({
                'generation': gen,
                'best_fitness': best_fitness,
                'avg_fitness': sum(fitness_scores) / len(fitness_scores)
            })
            
            # Selection (Tournament selection)
            new_population = []
            for _ in range(population_size):
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                child = self._ordered_crossover(parent1, parent2)
                
                # Mutation
                if random.random() < mutation_rate:
                    child = self._swap_mutation(child)
                
                new_population.append(child)
            
            population = new_population
        
        # Build final path using best chromosome
        full_route = [start] + best_chromosome + [end]
        detailed_path = []
        total_cost = 0
        
        for i in range(len(full_route) - 1):
            segment_path, segment_cost, _ = self.dijkstra(full_route[i], full_route[i+1], metric)
            if segment_path:
                if detailed_path:
                    detailed_path.extend(segment_path[1:])  # Avoid duplicating nodes
                else:
                    detailed_path.extend(segment_path)
                total_cost += segment_cost
            else:
                total_cost = float('inf')
                break
        
        execution_time = time.time() - start_time
        
        return detailed_path, total_cost, {
            'algorithm': 'Genetic Algorithm',
            'execution_time': execution_time,
            'generations': generations,
            'population_size': population_size,
            'best_fitness': best_fitness,
            'generation_stats': generation_stats[:10]  # Return first 10 for visualization
        }
    
    def _evaluate_route_fitness(self, route: List[str], metric: str) -> float:
        """Calculate total cost of a route"""
        total_cost = 0
        for i in range(len(route) - 1):
            if route[i] in self.graph and route[i+1] in self.graph[route[i]]:
                total_cost += self.graph[route[i]][route[i+1]].get(metric, float('inf'))
            else:
                # Use Dijkstra for disconnected segments
                _, segment_cost, _ = self.dijkstra(route[i], route[i+1], metric)
                total_cost += segment_cost
        return total_cost
    
    def _tournament_selection(self, population: List[List[str]], 
                             fitness_scores: List[float], tournament_size: int = 3) -> List[str]:
        """Tournament selection for genetic algorithm"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
        return population[winner_idx].copy()
    
    def _ordered_crossover(self, parent1: List[str], parent2: List[str]) -> List[str]:
        """Ordered crossover for genetic algorithm"""
        size = len(parent1)
        if size < 2:
            return parent1.copy()
        
        start, end = sorted(random.sample(range(size), 2))
        child = [None] * size
        
        # Copy segment from parent1
        child[start:end] = parent1[start:end]
        
        # Fill remaining from parent2
        pointer = end
        for gene in parent2[end:] + parent2[:end]:
            if gene not in child:
                if pointer >= size:
                    pointer = 0
                child[pointer] = gene
                pointer += 1
        
        return child
    
    def _swap_mutation(self, chromosome: List[str]) -> List[str]:
        """Swap mutation for genetic algorithm"""
        if len(chromosome) < 2:
            return chromosome
        
        mutated = chromosome.copy()
        idx1, idx2 = random.sample(range(len(mutated)), 2)
        mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
        return mutated