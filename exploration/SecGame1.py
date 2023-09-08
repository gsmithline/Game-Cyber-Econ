import random
import matplotlib.pyplot as plt

class SecurityGame:
    def __init__(self, num_targets, k_resources):
        assert k_resources < num_targets, "k should be less than n"
        
        self.num_targets = num_targets
        self.k_resources = k_resources
        self.history = []  # To store the history of attacks
        self.belief_type1 = 0.5  # Initial belief that the attacker is of type 1
        self.rewards = [random.uniform(1, 10) for _ in range(num_targets)]
        self.penalties = [random.uniform(-10, -1) for _ in range(num_targets)]

    def defender_strategy(self):
        if self.belief_type1 > 0.5:
            return sorted(range(len(self.rewards)), key=lambda i: self.rewards[i])[:self.k_resources]
        else:
            return sorted(range(len(self.rewards)), key=lambda i: self.rewards[i], reverse=True)[:self.k_resources]

    def simulate_attack(self, scenario):
        is_type1 = random.random() < self.belief_type1
        if scenario == "Perfect Bayesian":
            return self.rewards.index(max(self.rewards))
        elif scenario == "Myopic w/ Learn":
            unprotected_targets = [i for i in range(self.num_targets) if i not in self.defender_strategy()]
            return max(unprotected_targets, key=lambda x: self.rewards[x])
        elif scenario == "Deceptive w/ Learn":
            if is_type1:
                if random.random() < self.belief_type1:
                    return random.choice([i for i in range(self.num_targets) if i not in self.defender_strategy()])
                else:
                    return random.choice(self.defender_strategy())
            else:
                unprotected_targets = [i for i in range(self.num_targets) if i not in self.defender_strategy()]
                return max(unprotected_targets, key=lambda x: self.rewards[x])

    def update_beliefs(self, target_attacked):
        likelihood = 0.5 if target_attacked not in self.defender_strategy() else 1 - 0.5
        total_prob = self.belief_type1 * likelihood + (1 - self.belief_type1) * (1 - likelihood)
        self.belief_type1 = likelihood * self.belief_type1 / total_prob

    def run_single_instance(self, scenario):
        deceptive_actions = 0
        for _ in range(2):  
            defended_targets = self.defender_strategy()
            target_attacked = self.simulate_attack(scenario)
            self.history.append(target_attacked)  
            self.update_beliefs(target_attacked)
            if target_attacked not in defended_targets:
                deceptive_actions += 1
        return deceptive_actions / 2

    def run_experiment(self, scenario, instances=220):
        total_deceptive_actions = sum([self.run_single_instance(scenario) for _ in range(instances)])
        return total_deceptive_actions / instances

# Running the experiment
target_options = [4, 6, 8, 10, 12]
k_resources_options = [1, 2, 3, 4, 5]  
scenarios = ["Perfect Bayesian", "Myopic w/ Learn", "Deceptive w/ Learn"]
prior_probs = [i/100 for i in range(0, 101, 5)]

plt.figure(figsize=(15, 9))
for scenario in scenarios:
    for n, k in zip(target_options, k_resources_options):
        avg_deceptive_actions = [SecurityGame(num_targets=n, k_resources=k).run_experiment(scenario) for _ in prior_probs]
        plt.plot(prior_probs, avg_deceptive_actions, label=f'{scenario} N={n}, K={k}')

plt.title("Probability of Deceptive Action for T=2 Time Steps")
plt.xlabel("Prior Probability of Attacker Type 1")
plt.ylabel("Probability of Deceptive Action")
plt.legend()
plt.grid(True)
plt.show()