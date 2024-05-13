import cProfile
import pstats
import io
import csv
import subprocess

class PerformanceProfiler:
    """Tracks the simulations over actions played"""
    def __init__(self, filename='csv_data/monte_carlo_simulations.csv'):
        self.filename = filename
        self.action_count = 0 
        self.simulations_count = []  
        self.initialize_csv()  

    def initialize_csv(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Action Call', 'Simulations'])

    def record_action(self):
        self.action_count += 1
        self.simulations_count.append(0)

    def record_simulation(self):
        if self.simulations_count: 
            self.simulations_count[-1] += 1

    def export_to_csv(self):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            last_index = len(self.simulations_count) - 1
            writer.writerow([self.action_count, self.simulations_count[last_index] if self.simulations_count else 0])

class ActionProfiler:
    """Tracks Nodes expanded over actions played"""
    def __init__(self, filename='csv_data/mini_max_simulations.csv'):
        self.filename = filename
        self.action_count = 0
        self.nodes_expanded = []
        self.initialize_csv()

    def initialize_csv(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Action Call', 'Nodes Expanded'])

    def record_action(self):
        self.action_count += 1
        self.nodes_expanded.append(0)

    def record_node_expansion(self):
        if self.nodes_expanded:
            self.nodes_expanded[-1] += 1

    def export_to_csv(self):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            last_index = len(self.nodes_expanded) - 1
            writer.writerow([self.action_count, self.nodes_expanded[last_index] if self.nodes_expanded else 0])

def simulate_game(agent1, agent2):
    print("Running game simulation...")
    command = ['python', '-m', 'referee', agent1, agent2, '--time', '180', '--space', '250']
    subprocess.run(command)
    print("Game simulation completed.")

if __name__ == "__main__":
    print("ADJUST THIS FUNCTION TO GATHER RELEVANT PROFILERS")

# Time Profiler
def profiled_function(func):
    """Tracks time performance after every action move"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return result
    return wrapper
