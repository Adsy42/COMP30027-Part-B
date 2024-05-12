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
    agent: 'Agent'  # Assuming 'Agent' is defined elsewhere and is compatible
    compute_exploration_constant: callable  # This is a function that takes two parameters

def exploration_function(param1, param2):
    """ A sample function that computes an exploration constant based on two parameters. """
    # An example computation, this should be replaced with your actual logic
    return param1 * 2 + param2

def initialise_population(size):
    print("Initializing population...")
    return [GeneticAgent(Agent(PlayerColor.RED), lambda p1, p2: exploration_function(random.uniform(0, 1), random.uniform(0, 1))) for _ in range(size)]

def simulate_game(agent):
    print(f"Running game simulation for agent with exploration function...")
    # Placeholder command setup; replace with your actual Monte-Carlo simulation command
    command = ['python', '-m', 'referee', 'agent.program:Agent', 'agent.program:Monte_Carlo_Agent',
               '--time', '180', '--space', '250']
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        score = parse_game_result(result.stdout)
        print(f"Game simulation completed with score: {score}")
    except subprocess.CalledProcessError as e:
        print("Error during game simulation:", e)
        score = 0
    return score

def parse_game_result(output):
    print("Parsing game result...")
    result = output.strip().split('\n')[-1]
    match = re.search(r'Winning player: (\d)', result)
    win = 1 if match and match.group(1) == '2' else 0
    print(f"Game result parsed: {win}")
    return win

def evaluate_agents(population):
    print("Evaluating agents...")
    fitness_scores = []
    for agent in population:
        score = simulate_game(agent)
        fitness_scores.append(score)
    print("All agents evaluated.")
    return fitness_scores

def mutate(agent, mutation_rate=0.05):
    """ Randomly adjust the parameters of the exploration function """
    print("Mutating agent...")
    def mutated_function(param1, param2):
        new_param1 = param1 + random.uniform(-0.05, 0.05) if random.random() < mutation_rate else param1
        new_param2 = param2 + random.uniform(-0.05, 0.05) if random.random() < mutation_rate else param2
        return agent.compute_exploration_constant(new_param1, new_param2)
    agent.compute_exploration_constant = lambda p1, p2: mutated_function(p1, p2)
    print("Mutation completed.")

def crossover(parent1, parent2):
    print("Performing crossover...")
    # Simple crossover: take one part from each parent
    child1 = GeneticAgent(Agent(PlayerColor.RED), lambda p1, p2: parent1.compute_exploration_constant(p1, p2))
    child2 = GeneticAgent(Agent(PlayerColor.RED), lambda p1, p2: parent2.compute_exploration_constant(p1, p2))
    print("Crossover completed.")
    return child1, child2

def genetic_algorithm(population_size=10, num_generations=10):
    population = initialise_population(population_size)
    for generation in range(num_generations):
        print(f"Generation {generation + 1}")
        fitness_scores = evaluate_agents(population)
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
