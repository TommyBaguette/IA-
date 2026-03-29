# Taxi Fleet Simulator

A taxi fleet management simulator built in Python for the Artificial Intelligence course at the University of Minho.

The project uses real map data loaded via **OSMnx** and **NetworkX** to model a city graph, where a fleet of taxis is dispatched to handle incoming ride requests. The core of the project is the implementation and comparison of several graph search algorithms used to compute optimal routes between pickup and drop-off points.

## Algorithms Implemented
- **DFS** (Depth-First Search)
- **BFS** (Breadth-First Search)
- **Greedy Best-First Search**
- **A\*** (A-Star)
- **Dijkstra**

## Features
- Animated simulation with a graphical visualizer
- Benchmark mode to compare algorithm performance (path cost, execution time)
- Fleet analysis tool to compare taxi efficiency across routes
- Dynamic edge weights to simulate traffic conditions
- Request generator to simulate incoming ride demand

## Tech Stack
Python, NetworkX, OSMnx, Matplotlib

## How to Run
It is recommended to use a virtual environment to avoid dependency conflicts:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
