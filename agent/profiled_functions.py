import cProfile
import pstats
import io
import csv

import subprocess
class Profiler:
    def __init__(self, file_name='output.csv'):
        self.file_name = file_name
        self.action_calls = 0 #x-axis
        self.simulations_per_call = [] #y-axis
        self.init_csv_file()  # Intialise the CSV file with headers when Profiler is created

    def init_csv_file(self):
        with open(self.file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Action Call', 'Simulations'])

    def record_action_call(self):
        self.action_calls += 1
        self.simulations_per_call.append(0)

    def record_simulation(self):
        if self.simulations_per_call:  # Check to avoid index error if called before any action
            self.simulations_per_call[-1] += 1

    def export_to_csv(self):
        with open(self.file_name, 'a', newline='') as file:  # Append to existing CSV file
            writer = csv.writer(file)
            last_index = len(self.simulations_per_call) - 1
            writer.writerow([self.action_calls, self.simulations_per_call[last_index] if self.simulations_per_call else 0])



def simulate_game(agent1, agent2):
    print("Running game simulation...")
    command = [
        'python', '-m', 'referee', f'{agent1}', f'{agent2}',
        '--time', '180', '--space', '250']  # '--verbosity', '0'
    subprocess.run(command)
    print("Game simulation completed.")

# Explicit call to export data to CSV
profiler = Profiler()
def profiled_function(func):
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

# Create a program/function that runs agents autmaically
# --> Gather statiscs per game and write it to a file

# python profiled_functions.py

class Profiler2:
    def __init__(self, file_name='output2.csv'):
        self.file_name = file_name
        self.action_calls = 0
        self.nodes_expanded = []
        self.init_csv_file()  # Intialise the CSV file with headers when Profiler is created

    def init_csv_file(self):
        with open(self.file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Action Call', 'Nodes Expanded'])

    def record_action_call(self):
        self.action_calls += 1
        self.nodes_expanded.append(0)

    def record_nodes_expanded(self):
        if self.nodes_expanded:  # Check to avoid index error if called before any action
            self.nodes_expanded[-1] += 1

    def export_to_csv(self):
        with open(self.file_name, 'a', newline='') as file:  # Append to existing CSV file
            writer = csv.writer(file)
            last_index = len(self.nodes_expanded) - 1
            writer.writerow([self.action_calls, self.nodes_expanded[last_index] if self.nodes_expanded else 0])

def simulate_game(agent1, agent2):
    print("Running game simulation...")
    command = [
        'python', '-m', 'referee', f'{agent1}', f'{agent2}',
        '--time', '180', '--space', '250']  # '--verbosity', '0'
    subprocess.run(command)
    print("Game simulation completed.")
profiler2 = Profiler2()

if __name__ == "__main__":
    simulate_game('agent.program', 'testing_agents.mini_max.py')
    profiler.export_to_csv()

import time

class TimeoutException(Exception):
    pass

def time_limited_execution(end_time):
    if time.time() > end_time:
        raise TimeoutException("Time limit exceeded")
    return False