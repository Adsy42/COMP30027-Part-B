import subprocess
from .program import Agent
import random
import re
from dataclasses import dataclass
from referee.game import PlayerColor
TESTING_AGENTS = ["testing_agents.greedy_search.py", "testing_agents.random_bot.py", "testing_agents.mini_max.py"]
MATCH_WINNING_PLAYER = r"player (\d+)"

@dataclass
class GeneticAgent:
    agent: Agent
    param_a: float
    param_b: float

def initialise_population(size):
    print("Initializing population...")
    return [GeneticAgent(Agent(PlayerColor.RED), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)) for _ in range(size)]

def evaluate_agents(population):
    print("Evaluating agents...")
    fitness_scores = []
    for agent in population:
        print(f"Simulating game for agent: {agent}")
        score = simulate_game(agent)
        fitness_scores.append(score)
        print(f"Agent scored: {score}")
    print("All agents evaluated.")
    return fitness_scores

def select_parents(population, fitness_scores, num_parents=2):
    print("Selecting parents...")
    total_fitness = sum(fitness_scores)
    selection_probs = [score / total_fitness for score in fitness_scores]
    parents = random.choices(population, weights=selection_probs, k=num_parents)
    print(f"Selected {num_parents} parents.")
    return parents

def mutate(agent, mutation_rate=0.1):
    print(f"Mutating agent with initial params: {agent.param_a}, {agent.param_b}")
    if random.random() < mutation_rate:
        agent.param_a += random.uniform(-0.1, 0.1)
        agent.param_b += random.uniform(-0.1, 0.1)
    print(f"Mutated agent to params: {agent.param_a}, {agent.param_b}")

def crossover(parent1, parent2):
    print("Performing crossover...")
    child1 = GeneticAgent(Agent(PlayerColor.RED), parent1.param_a, parent2.param_b)
    child2 = GeneticAgent(Agent(PlayerColor.RED), parent2.param_a, parent1.param_b)
    print("Crossover completed.")
    return child1, child2

def simulate_game(agent):
    print("Running game simulation...")
    command = [
        'python', '-m', 'referee', 'agent.program:Agent', 'agent.program:Monte_Carlo_Agent',
        '--time', '180', '--space', '250'] #, '--verbosity', '0'    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    score = parse_game_result(result.stdout)
    print("Game simulation completed.")
    return score

def parse_game_result(output):
    print("Parsing game result...")
    result = output.strip().split('\n')[-1]
    match = re.search(MATCH_WINNING_PLAYER, result)
    win = 1 if match and match.group(1) == '2' else 0
    print(f"Game result parsed: {win}")
    return win

def genetic_algorithm(population_size=10, num_generations=100):
    population = initialise_population(population_size)
    for generation in range(num_generations):
        print(f"Generation {generation + 1}")
        fitness_scores = [simulate_game(agent) for agent in population]
        parents = random.choices(population, weights=fitness_scores, k=2)
        new_population = []
        for _ in range(population_size // 2):
            child1, child2 = crossover(parents[0], parents[1])
            mutate(child1)
            mutate(child2)
            new_population.extend([child1, child2])
        population = new_population
        print(f"Best fitness score in generation {generation + 1}: {max(fitness_scores)}")

if __name__ == "__main__":
    genetic_algorithm()
