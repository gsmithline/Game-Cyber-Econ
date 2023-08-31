import random
import numpy as np
import time
start_time = time.time()

def demand(price):
    return 10 - price

def supply(price, a, b):
    return a + b * price

def profit(price, quantity):
    return price * quantity

# Fitness Function
def evaluate_fitness(a, b, T=10):
    price = 5  # Initial price
    total_profit = 0
    
    for t in range(T):
        quantity_supplied = supply(price, a, b)
        quantity_demanded = demand(price)
        
        price = price + 0.1 * (quantity_demanded - quantity_supplied)
        
        total_profit += profit(price, quantity_supplied)
    
    return total_profit

population_size = 100
generations = 100000
mutation_rate = 0.1

population = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(population_size)]

for generation in range(generations):
    fitness = [evaluate_fitness(a, b) for a, b in population]
    print(f"Generation {generation}: Best Fitness = {max(fitness)}")

    
    selected_indices = np.argsort(fitness)[::-1][:population_size // 2]
    print(f"Generation {generation}: Best Fitness = {max(fitness)} Best Strategy = {population[selected_indices[0]]}")

    selected_population = [population[i] for i in selected_indices]
    
    new_population = []
    
    while len(new_population) < population_size:
        parent1, parent2 = random.choices(selected_population, k=2)
        a1, b1 = parent1
        a2, b2 = parent2
        
        # Crossover Averaging for simplicity
        child_a = (a1 + a2) / 2
        child_b = (b1 + b2) / 2
        
        # Mutation
        if random.random() < mutation_rate:
            child_a += random.uniform(-1, 1)
            child_b += random.uniform(-1, 1)
        
        child_a = max(0, child_a)
        child_b = max(0, child_b)
        
        new_population.append((child_a, child_b))
    
    # Replace old population
    population = new_population


# Find the best strategy after all generations
best_fitness = max([evaluate_fitness(a, b) for a, b in population])
best_strategy = population[np.argmax([evaluate_fitness(a, b) for a, b in population])]
end_time = time.time()

# Calculate and display elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
print(f"Best Strategy: {best_strategy}, Best Fitness: {best_fitness}")