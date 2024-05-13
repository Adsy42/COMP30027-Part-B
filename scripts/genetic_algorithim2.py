from dataclasses import dataclass
import random
import subprocess
import os  # Import os module to use environment variables
import re
@dataclass
class GeneticAgent:
    param1: float
    param2: float
    param3: float
    param4: float

def initialise_population(size):
    print("Initializing population...")
    return [GeneticAgent(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)) for _ in range(size)]


def simulate_game(agent):    
    print(f"Running game simulation for agent with params: {agent.param1}, {agent.param2}, {agent.param3}, {agent.param4}")

    # Set environment variables
    os.environ['PARAM1'] = str(agent.param1)
    os.environ['PARAM2'] = str(agent.param2)
    os.environ['PARAM3'] = str(agent.param3)
    os.environ['PARAM4'] = str(agent.param4)

    command = ['python', '-m', 'referee', 'agent.program', 'testing_agents.mini_max', '--time', '180']
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        score = parse_game_result(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during game simulation:", e)
        score = 0
    return score

def parse_game_result(output):
    print("Parsing game result...")
    result = output.strip().split('\n')[-1]
    match = re.search(r'Winning player: (\d)', result)
    win = 1 if match and match.group(1) == '2' else 0
    return win

def mutate(agent, mutation_rate=0.1):
    print("Mutating agent...")
    if random.random() < mutation_rate:
        agent.param1 += random.uniform(-0.05, 0.05)
        agent.param2 += random.uniform(-0.05, 0.05)
    print(f"Agent mutated to params: {agent.param1}, {agent.param2}")

def crossover(parent1, parent2):
    print("Performing crossover...")
    child1_param1 = (parent1.param1 + parent2.param1) / 2
    child1_param2 = (parent1.param2 + parent2.param2) / 2
    child1 = GeneticAgent(child1_param1, child1_param2)
    print("Crossover completed.")
    return child1

def genetic_algorithm(population_size=10, num_generations=10):
    population = initialise_population(population_size)
    for generation in range(num_generations):
        print(f"Generation {generation + 1}")
        fitness_scores = [simulate_game(agent) for agent in population]
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True, key=lambda pair: pair[0])]
        parents = sorted_population[:2]  # Select the two best agents

        new_population = []
        for _ in range(population_size // 2):
            child1 = crossover(parents[0], parents[1])
            mutate(child1)
            new_population.extend([child1, child1])  # Adding mutated child1 twice for simplicity

        population = new_population
        print(f"Best fitness score in generation {generation + 1}: {max(fitness_scores)}")

if __name__ == "__main__":
    genetic_algorithm()
