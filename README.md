# Route Optimization Engine

A comprehensive route optimization system implementing **Dijkstra's Algorithm**, **A\* Algorithm**, and **Genetic Algorithm** for finding optimal paths. Features a Flask-based backend and an interactive web dashboard for real-time visualization and algorithm comparison.

## 🌟 Features

- **Three Powerful Algorithms**:

  - **Dijkstra's Algorithm**: Classic shortest path algorithm
  - **A\* Algorithm**: Heuristic-based pathfinding with improved efficiency
  - **Genetic Algorithm**: Evolutionary approach for multi-waypoint optimization

- **Interactive Dashboard**:

  - Real-time route visualization on interactive maps
  - Side-by-side algorithm comparison
  - Performance metrics and statistics
  - Support for waypoints and intermediate stops
  - Distance and time optimization modes

- **Advanced Features**:
  - Realistic road network simulation
  - Dynamic graph generation
  - Multiple optimization metrics
  - Responsive design for all devices

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- A modern web browser (Chrome, Firefox, Safari, or Edge)

## 🚀 Installation Guide

### Step 1: Download the Project

Create a new folder for your project and organize the files:

```
route-optimization/
├── app.py
├── algorithms.py
├── graph_generator.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

### Step 2: Install Python (if not already installed)

**Windows:**

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

**Mac:**

```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

### Step 3: Verify Python Installation

Open your terminal/command prompt and run:

```bash
python --version
# or
python3 --version
```

You should see something like `Python 3.8.x` or higher.

### Step 4: Create Project Directory

```bash
# Create project folder
mkdir route-optimization
cd route-optimization

# Create necessary subdirectories
mkdir templates
mkdir static
```

### Step 5: Add Project Files

Copy all the provided files to their respective locations:

- `app.py`, `algorithms.py`, `graph_generator.py`, `requirements.txt` → Root directory
- `index.html` → templates/ folder
- `style.css`, `script.js` → static/ folder

### Step 6: Install Dependencies

Open terminal in the project directory and run:

```bash
# Install required packages
pip install -r requirements.txt

# Or if you're using pip3:
pip3 install -r requirements.txt
```

This will install:

- Flask (web framework)
- Flask-CORS (cross-origin resource sharing)
- NumPy (numerical computations)
- Requests (HTTP library)
- Geopy (geographical calculations)

### Step 7: Run the Application

```bash
# Start the Flask server
python app.py

# Or if you're using python3:
python3 app.py
```

You should see output like:

```
Graph initialized with 30 nodes
Starting Flask server...
Visit http://localhost:5000 in your browser
 * Running on http://0.0.0.0:5000
```

### Step 8: Access the Dashboard

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the Route Optimization Dashboard!

## 📖 How to Use

### Basic Route Finding

1. **Select Algorithm**: Choose from Dijkstra, A\*, or Genetic Algorithm
2. **Choose Optimization Metric**: Distance (km) or Time (minutes)
3. **Select Nodes**: Pick start and end points from dropdowns
4. **Find Route**: Click "Find Route" button
5. **View Results**: See the optimal path highlighted on the map with statistics

### Adding Waypoints (Genetic Algorithm Only)

1. Select "Genetic Algorithm" from the algorithm dropdown
2. Waypoint section will appear automatically
3. Click "+ Add Waypoint" to add intermediate stops
4. Select desired waypoints from dropdowns
5. Click "Find Route" to optimize multi-stop route

### Comparing Algorithms

1. Configure start and end nodes
2. Click "Compare All" button
3. All algorithms will run simultaneously
4. Routes displayed in different colors:
   - **Blue**: Dijkstra's Algorithm
   - **Green**: A\* Algorithm
   - **Purple**: Genetic Algorithm
5. View comparison table with detailed metrics

### Using Random Nodes

Click "Random Nodes" button to automatically select random start, end, and waypoint nodes for testing.

### Clearing the Map

Click "Clear Map" to remove all routes and reset the view.

## 🎯 Understanding the Algorithms

### Dijkstra's Algorithm

- **Best for**: Finding guaranteed shortest path
- **Pros**: Always finds optimal solution, well-tested
- **Cons**: Slower for large graphs, explores many nodes
- **Use case**: When you need the absolute shortest path

### A\* Algorithm

- **Best for**: Fast pathfinding with heuristics
- **Pros**: Faster than Dijkstra, still finds optimal path
- **Cons**: Requires coordinate data, slightly complex
- **Use case**: Real-time navigation, interactive systems

### Genetic Algorithm

- **Best for**: Multi-waypoint route optimization
- **Pros**: Handles complex constraints, good for TSP-like problems
- **Cons**: May not find absolute optimum, slower execution
- **Use case**: Delivery routes, tour planning with multiple stops

## 🔧 Configuration Options

### Modifying Graph Parameters

Edit `app.py` to change graph generation:

```python
def initialize_graph():
    graph_data, positions_data = GraphGenerator.generate_city_graph(
        num_nodes=30,        # Change number of nodes
        density=0.3,         # Connection density (0-1)
        city_center=(28.6139, 77.2090)  # City coordinates
    )
```

### Genetic Algorithm Parameters

In `app.py`, modify genetic algorithm settings:

```python
path, cost, stats = optimizer.genetic_algorithm(
    start, end, waypoints, metric,
    population_size=50,      # Population size
    generations=100,         # Number of generations
    mutation_rate=0.2        # Mutation probability
)
```

## 📊 Understanding the Results

### Performance Metrics

- **Total Distance/Time**: Overall cost of the route
- **Path Length**: Number of nodes in the route
- **Nodes Explored**: Number of nodes algorithm visited
- **Execution Time**: Time taken to compute route (milliseconds)

### Comparison Table

When comparing algorithms, the table shows:

- Algorithm name with color-coded badge
- Total cost (distance or time)
- Number of nodes in path
- Nodes explored during computation
- Execution time

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'flask'"**

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. "Address already in use" or "Port 5000 is busy"**

```bash
# Solution: Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**3. Map not displaying**

- Check your internet connection (map tiles need to load)
- Clear browser cache and reload
- Check browser console for errors (F12)

**4. "Python not recognized"**

- Python not added to PATH
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python39\python.exe app.py`

**5. Blank page or styling issues**

- Ensure `templates/` and `static/` folders exist
- Check file names match exactly (case-sensitive)
- Look for errors in terminal

### Debug Mode

Flask runs in debug mode by default, showing detailed errors. If you encounter issues:

1. Check the terminal where Flask is running
2. Look for error messages
3. Check browser console (F12 → Console tab)

## 🔒 Security Notes

This is a **development server** suitable for:

- ✅ Local testing
- ✅ Learning and experimentation
- ✅ Algorithm development

**NOT suitable for:**

- ❌ Production deployment
- ❌ Public internet exposure
- ❌ Handling sensitive data

For production, use a proper WSGI server like Gunicorn or uWSGI.

## 📈 Performance Tips

1. **Reduce Nodes**: Lower `num_nodes` for faster computation
2. **Adjust Density**: Lower density means fewer connections
3. **GA Parameters**: Reduce `generations` or `population_size` for faster GA
4. **Disable Debug**: Set `debug=False` in production

## 🎨 Customization

### Changing Colors

Edit `static/style.css`:

```css
:root {
  --primary-color: #2563eb; /* Change main color */
  --success-color: #10b981; /* Change success color */
}
```

### Modifying Map Style

Edit `static/script.js` to change map provider:

```javascript
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  // Change to other tile providers like:
  // 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
});
```

## 📚 Learning Resources

- **Dijkstra's Algorithm**: [Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- **A\* Algorithm**: [Red Blob Games Tutorial](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- **Genetic Algorithms**: [Introduction to GA](https://towardsdatascience.com/introduction-to-genetic-algorithms-including-example-code-e396e98d8bf3)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)

## 🤝 Support

If you encounter issues:

1. Check this README thoroughly
2. Review error messages carefully
3. Ensure all files are in correct locations
4. Verify Python and package versions
5. Check terminal output for clues

## 📝 Project Structure Explained

```
route-optimization/
│
├── app.py                 # Flask web server and API endpoints
├── algorithms.py          # Implementation of all three algorithms
├── graph_generator.py     # Graph generation and utilities
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/
│   └── index.html        # Main dashboard HTML structure
│
└── static/
    ├── style.css         # All styling and animations
    └── script.js         # Frontend logic and map interactions
```

## 🎓 Educational Value

This project demonstrates:

- Algorithm implementation and comparison
- Graph theory concepts
- Web application development
- API design
- Data visualization
- Real-world problem solving

Perfect for:

- Computer Science students
- Algorithm enthusiasts
- Web developers learning backend
- Anyone interested in optimization

## 🚀 Next Steps

After getting it running:

1. Experiment with different algorithms
2. Try various graph sizes and densities
3. Compare performance on different routes
4. Modify parameters to see their effects
5. Add your own features!

## 📄 License

This project is provided as-is for educational purposes.

---

**Happy Optimizing! 🗺️✨**

For questions or improvements, feel free to extend and modify the code!
