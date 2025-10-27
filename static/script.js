// Global variables
let map;
let graphData = null;
let positionsData = null;
let roadGeometries = null;
let allNodes = [];
let routeLayers = [];
let markerLayers = [];
let graphLayers = [];

// API base URL
const API_BASE = window.location.origin;

// Color scheme for different algorithms
const algorithmColors = {
  dijkstra: '#2563eb',
  astar: '#10b981',
  genetic: '#8b5cf6',
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  initializeMap();
  loadGraphData();
  setupEventListeners();
});

// Initialize Leaflet map
function initializeMap() {
  map = L.map('map').setView([28.6139, 77.209], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);
}

// Load graph data from API
async function loadGraphData() {
  try {
    showLoading(true);
    const response = await fetch(`${API_BASE}/api/graph`);
    const data = await response.json();

    graphData = data.graph;
    positionsData = data.positions;
    allNodes = data.nodes;

    populateNodeSelectors();
    renderGraphNetwork();
    showLoading(false);
  } catch (error) {
    console.error('Error loading graph:', error);
    showError('Failed to load graph data');
    showLoading(false);
  }
}

// Populate node selector dropdowns
function populateNodeSelectors() {
  const startSelect = document.getElementById('start');
  const endSelect = document.getElementById('end');

  startSelect.innerHTML = '';
  endSelect.innerHTML = '';

  allNodes.forEach((node) => {
    const option1 = new Option(node, node);
    const option2 = new Option(node, node);
    startSelect.add(option1);
    endSelect.add(option2);
  });

  // Set default values
  if (allNodes.length >= 2) {
    startSelect.value = allNodes[0];
    endSelect.value = allNodes[Math.floor(allNodes.length / 2)];
  }
}

// Render the entire graph network
function renderGraphNetwork() {
  if (!graphData || !positionsData) return;

  // Clear existing graph layers
  graphLayers.forEach((layer) => map.removeLayer(layer));
  graphLayers = [];

  // Draw all edges in the graph - MAKE THEM VERY VISIBLE
  const drawnEdges = new Set(); // Prevent drawing duplicate edges

  Object.keys(graphData).forEach((nodeId) => {
    const neighbors = graphData[nodeId];
    const [lat1, lon1] = positionsData[nodeId];

    Object.keys(neighbors).forEach((neighborId) => {
      const edgeKey = [nodeId, neighborId].sort().join('-');

      if (!drawnEdges.has(edgeKey)) {
        drawnEdges.add(edgeKey);

        const [lat2, lon2] = positionsData[neighborId];

        const edge = L.polyline(
          [
            [lat1, lon1],
            [lat2, lon2],
          ],
          {
            color: '#94a3b8',
            weight: 4,
            opacity: 0.6,
            className: 'graph-edge',
          }
        )
          .bindTooltip(
            `Road: ${nodeId} ↔ ${neighborId}<br>Distance: ${neighbors[neighborId].distance} km`,
            {
              sticky: true,
            }
          )
          .addTo(map);

        graphLayers.push(edge);
      }
    });
  });

  // Draw all nodes - MAKE THEM BIGGER AND MORE VISIBLE
  Object.keys(positionsData).forEach((nodeId) => {
    const [lat, lon] = positionsData[nodeId];

    const node = L.circleMarker([lat, lon], {
      radius: 6,
      fillColor: '#64748b',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
      className: 'graph-node',
    })
      .bindTooltip(`<b>${nodeId}</b>`, {
        permanent: false,
        direction: 'top',
        offset: [0, -10],
      })
      .addTo(map);

    graphLayers.push(node);
  });

  console.log(
    `Rendered ${Object.keys(graphData).length} nodes and their connections`
  );
}

// Setup event listeners
function setupEventListeners() {
  const algorithmSelect = document.getElementById('algorithm');
  algorithmSelect.addEventListener('change', () => {
    const waypointsContainer = document.getElementById('waypointsContainer');
    if (algorithmSelect.value === 'genetic') {
      waypointsContainer.style.display = 'block';
      if (document.getElementById('waypointsList').children.length === 0) {
        addWaypoint();
        addWaypoint();
      }
    } else {
      waypointsContainer.style.display = 'none';
    }
  });
}

// Add waypoint selector
function addWaypoint() {
  const waypointsList = document.getElementById('waypointsList');
  const waypointItem = document.createElement('div');
  waypointItem.className = 'waypoint-item';

  const select = document.createElement('select');
  select.className = 'input-field';

  allNodes.forEach((node) => {
    const option = new Option(node, node);
    select.add(option);
  });

  const removeBtn = document.createElement('button');
  removeBtn.textContent = 'Remove';
  removeBtn.onclick = () => waypointItem.remove();

  waypointItem.appendChild(select);
  waypointItem.appendChild(removeBtn);
  waypointsList.appendChild(waypointItem);
}

// Get selected waypoints
function getWaypoints() {
  const waypointsList = document.getElementById('waypointsList');
  const waypoints = [];

  Array.from(waypointsList.children).forEach((item) => {
    const select = item.querySelector('select');
    if (select && select.value) {
      waypoints.push(select.value);
    }
  });

  return waypoints;
}

// Find route using selected algorithm
async function findRoute() {
  const algorithm = document.getElementById('algorithm').value;
  const start = document.getElementById('start').value;
  const end = document.getElementById('end').value;
  const metric = document.getElementById('metric').value;
  const waypoints = algorithm === 'genetic' ? getWaypoints() : [];

  if (!start || !end) {
    showError('Please select start and end nodes');
    return;
  }

  if (start === end) {
    showError('Start and end nodes must be different');
    return;
  }

  try {
    showLoading(true);
    clearPreviousRoutes();

    const response = await fetch(`${API_BASE}/api/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        algorithm,
        start,
        end,
        waypoints,
        metric,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      if (data.path && data.path.length > 0) {
        displayRouteAlongGraph(data, algorithm);
        displayResults(data);
      } else {
        showError('No path found between selected nodes');
      }
    } else {
      showError(data.error || 'Failed to find route');
    }

    showLoading(false);
  } catch (error) {
    console.error('Error finding route:', error);
    showError('Failed to compute route');
    showLoading(false);
  }
}

// Compare all algorithms
async function compareAlgorithms() {
  const start = document.getElementById('start').value;
  const end = document.getElementById('end').value;
  const metric = document.getElementById('metric').value;
  const waypoints = getWaypoints();

  if (!start || !end) {
    showError('Please select start and end nodes');
    return;
  }

  try {
    showLoading(true);
    clearPreviousRoutes();

    const response = await fetch(`${API_BASE}/api/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start,
        end,
        waypoints,
        metric,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      displayComparisonResults(data);
    } else {
      showError(data.error || 'Failed to compare algorithms');
    }

    showLoading(false);
  } catch (error) {
    console.error('Error comparing algorithms:', error);
    showError('Failed to compare algorithms');
    showLoading(false);
  }
}

// Display route following graph edges
function displayRouteAlongGraph(data, algorithm) {
  if (!data.path || data.path.length === 0) {
    showError('No valid path found');
    return;
  }

  const color = algorithmColors[algorithm] || '#2563eb';
  const path = data.path;

  console.log(`Drawing route with ${path.length} nodes for ${algorithm}`);

  // Draw route segment by segment following the actual path - THICK AND VISIBLE
  for (let i = 0; i < path.length - 1; i++) {
    const node1 = path[i];
    const node2 = path[i + 1];

    if (positionsData[node1] && positionsData[node2]) {
      const [lat1, lon1] = positionsData[node1];
      const [lat2, lon2] = positionsData[node2];

      const segment = L.polyline(
        [
          [lat1, lon1],
          [lat2, lon2],
        ],
        {
          color: color,
          weight: 6,
          opacity: 0.9,
          className: `route-${algorithm}`,
          dashArray: '10, 5',
        }
      )
        .bindPopup(`${node1} → ${node2}`)
        .addTo(map);

      routeLayers.push(segment);

      // Add arrow markers to show direction
      const midLat = (lat1 + lat2) / 2;
      const midLon = (lon1 + lon2) / 2;

      const arrow = L.circleMarker([midLat, midLon], {
        radius: 4,
        fillColor: color,
        color: 'white',
        weight: 1,
        opacity: 1,
        fillOpacity: 1,
      }).addTo(map);

      routeLayers.push(arrow);
    }
  }

  // Add markers for start and end
  const startCoord = positionsData[path[0]];
  const endCoord = positionsData[path[path.length - 1]];

  if (startCoord) {
    const startMarker = L.circleMarker([startCoord[0], startCoord[1]], {
      radius: 10,
      fillColor: '#10b981',
      color: 'white',
      weight: 3,
      opacity: 1,
      fillOpacity: 1,
    })
      .bindPopup(`<b>Start:</b> ${path[0]}`)
      .addTo(map);

    markerLayers.push(startMarker);
  }

  if (endCoord) {
    const endMarker = L.circleMarker([endCoord[0], endCoord[1]], {
      radius: 10,
      fillColor: '#ef4444',
      color: 'white',
      weight: 3,
      opacity: 1,
      fillOpacity: 1,
    })
      .bindPopup(`<b>End:</b> ${path[path.length - 1]}`)
      .addTo(map);

    markerLayers.push(endMarker);
  }

  // Add waypoint markers for genetic algorithm
  if (algorithm === 'genetic') {
    const waypoints = getWaypoints();
    waypoints.forEach((waypoint) => {
      if (positionsData[waypoint]) {
        const [lat, lon] = positionsData[waypoint];
        const waypointMarker = L.circleMarker([lat, lon], {
          radius: 8,
          fillColor: '#f59e0b',
          color: 'white',
          weight: 3,
          opacity: 1,
          fillOpacity: 1,
        })
          .bindPopup(`<b>Waypoint:</b> ${waypoint}`)
          .addTo(map);

        markerLayers.push(waypointMarker);
      }
    });
  }

  // Fit map to show entire route
  if (routeLayers.length > 0) {
    const group = L.featureGroup(routeLayers);
    map.fitBounds(group.getBounds().pad(0.1));
  }
}

// Display results in panel
function displayResults(data) {
  const resultsDiv = document.getElementById('results');
  const metricLabel = data.metric === 'distance' ? 'km' : 'min';

  let html = `
        <div class="alert alert-success">
            <strong>✓ Route Found!</strong>
        </div>
        
        <div class="result-item">
            <strong>Algorithm:</strong> ${capitalizeFirst(data.algorithm)}
        </div>
        
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-label">Total ${capitalizeFirst(
                  data.metric
                )}</div>
                <div class="stat-value">${data.cost.toFixed(
                  2
                )} ${metricLabel}</div>
            </div>
            
            <div class="stat-item">
                <div class="stat-label">Path Length</div>
                <div class="stat-value">${data.path.length} nodes</div>
            </div>
            
            <div class="stat-item">
                <div class="stat-label">Nodes Explored</div>
                <div class="stat-value">${
                  data.stats.nodes_explored || 'N/A'
                }</div>
            </div>
            
            <div class="stat-item">
                <div class="stat-label">Execution Time</div>
                <div class="stat-value">${(
                  data.stats.execution_time * 1000
                ).toFixed(2)} ms</div>
            </div>
        </div>
        
        <div class="result-item">
            <strong>Path:</strong><br>
            <small style="word-break: break-all;">${data.path.join(
              ' → '
            )}</small>
        </div>
    `;

  if (data.stats.generation_stats) {
    html += `
            <div class="result-item">
                <strong>Genetic Algorithm Details:</strong><br>
                Generations: ${data.stats.generations}<br>
                Population Size: ${data.stats.population_size}<br>
                Best Fitness: ${data.stats.best_fitness.toFixed(2)}
            </div>
        `;
  }

  resultsDiv.innerHTML = html;
  document.getElementById('comparisonCard').style.display = 'none';
}

// Display comparison results
function displayComparisonResults(data) {
  const results = data.results;

  // Draw all routes with different colors
  Object.keys(results).forEach((algorithm) => {
    const result = results[algorithm];
    if (result.path && result.path.length > 0) {
      displayRouteAlongGraph(result, algorithm);
    }
  });

  // Create comparison table
  let tableHTML = `
        <div class="comparison-table">
            <table>
                <thead>
                    <tr>
                        <th>Algorithm</th>
                        <th>${capitalizeFirst(data.metric)}</th>
                        <th>Nodes</th>
                        <th>Explored</th>
                        <th>Time (ms)</th>
                    </tr>
                </thead>
                <tbody>
    `;

  Object.keys(results).forEach((algorithm) => {
    const result = results[algorithm];
    const metricUnit = data.metric === 'distance' ? 'km' : 'min';

    if (!result.error && result.path) {
      tableHTML += `
                <tr>
                    <td><span class="algorithm-badge badge-${algorithm}">${capitalizeFirst(
        algorithm
      )}</span></td>
                    <td>${result.cost.toFixed(2)} ${metricUnit}</td>
                    <td>${result.path.length}</td>
                    <td>${result.stats.nodes_explored || 'N/A'}</td>
                    <td>${(result.stats.execution_time * 1000).toFixed(2)}</td>
                </tr>
            `;
    }
  });

  tableHTML += `
                </tbody>
            </table>
        </div>
    `;

  document.getElementById('comparisonTable').innerHTML = tableHTML;
  document.getElementById('comparisonCard').style.display = 'block';

  // Update results panel
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>ℹ Comparison Complete!</strong><br>
            All algorithms executed successfully. See comparison table below.
        </div>
    `;
}

// Get random nodes
async function randomNodes() {
  try {
    const algorithm = document.getElementById('algorithm').value;
    const numWaypoints = algorithm === 'genetic' ? 2 : 0;

    const response = await fetch(
      `${API_BASE}/api/random-nodes?waypoints=${numWaypoints}`
    );
    const data = await response.json();

    if (response.ok) {
      document.getElementById('start').value = data.start;
      document.getElementById('end').value = data.end;

      if (algorithm === 'genetic' && data.waypoints) {
        const waypointsList = document.getElementById('waypointsList');
        waypointsList.innerHTML = '';

        data.waypoints.forEach((waypoint) => {
          addWaypoint();
          const lastSelect = waypointsList.lastChild.querySelector('select');
          lastSelect.value = waypoint;
        });
      }
    }
  } catch (error) {
    console.error('Error getting random nodes:', error);
    showError('Failed to get random nodes');
  }
}

// Clear map routes
function clearMap() {
  clearPreviousRoutes();
  document.getElementById('results').innerHTML = `
        <p class="text-muted">Configure route and click "Find Route" to see results</p>
    `;
  document.getElementById('comparisonCard').style.display = 'none';
}

// Clear previous routes and markers
function clearPreviousRoutes() {
  routeLayers.forEach((layer) => map.removeLayer(layer));
  markerLayers.forEach((layer) => map.removeLayer(layer));
  routeLayers = [];
  markerLayers = [];
}

// Show/hide loading overlay
function showLoading(show) {
  const loading = document.getElementById('loading');
  if (show) {
    loading.classList.add('active');
  } else {
    loading.classList.remove('active');
  }
}

// Show error message
function showError(message) {
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = `
        <div class="alert alert-error">
            <strong>✗ Error:</strong> ${message}
        </div>
    `;
}

// Utility function to capitalize first letter
function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
