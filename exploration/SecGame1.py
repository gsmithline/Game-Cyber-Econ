import random
import matplotlib.pyplot as plt

class SecurityGame:
    def __init__(self, num_targets, k_resources, file, steps):
        assert k_resources < num_targets, "k should be less than n"
        
        self.num_targets = num_targets
        self.k_resources = k_resources
        self.history = []  
        self.belief_type1 = .5
        self.rewards = [random.uniform(1, 10) for _ in range(num_targets)]
        self.penalties = [random.uniform(-10, -1) for _ in range(num_targets)]
        self.file = file
        self.defender_utilities = []
        self.attacker_utilities = []
        self.steps = steps
        self.is_type1 = None
        self.decptive_actions = 0

    
    def defender_strategy(self):
        if self.belief_type1 > .5:  # Defender believes attacker is more likely to be Type 1
            # Prioritize targets based on historical attack frequency
            scores = [self.history.count(i) for i in range(self.num_targets)]
        else:  # Defender believes attacker is more likely to be Type 2
            # Prioritize targets based on their rewards
            scores = self.rewards

        top_k_targets = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k_resources]
        self.file.write(f"Defender defends targets: {top_k_targets}\n")
        return top_k_targets
        
    

    def simulate_attack(self, scenario):
        self.is_type1 = random.random() < self.belief_type1
        if scenario == "Perfect Bayesian":
            defended_targets = self.defender_strategy()
            best_undefended_target = max([i for i in range(self.num_targets) if i not in defended_targets], key=lambda x: self.rewards[x])
            attack_target = best_undefended_target

        elif scenario == "Myopic w/ Learn":
            if self.history:
                last_defended_targets = self.history[-1]
            else:
                last_defended_targets = []
            best_undefended_target = max([i for i in range(self.num_targets) if i not in last_defended_targets], key=lambda x: self.rewards[x])
            attack_target = best_undefended_target
    
        elif scenario == "Deceptive w/ Learn":
            if self.is_type1:
                if random.random() < self.belief_type1:
                    attack_target = random.choice([i for i in range(self.num_targets) if i not in self.defender_strategy()])
                else:
                    attack_target = random.choice(self.defender_strategy())
            else:
                unprotected_targets = [i for i in range(self.num_targets) if i not in self.defender_strategy()]
                attack_target = max(unprotected_targets, key=lambda x: self.rewards[x])


                #unprotected_targets = [i for i in range(self.num_targets) if i not in self.defender_strategy()]
                #attack_target = max(unprotected_targets, key=lambda x: self.rewards[x])
        '''
        elif scenario == "Deceptive w/ Learn":
            if self.is_type1:
                if random.random() < self.belief_type1:
                    attack_target = random.choice([i for i in range(self.num_targets) if i not in self.defender_strategy()])
                else:
                    attack_target = random.choice(self.defender_strategy())
            else:
                if random.random() < self.belief_type1:
                    attack_target = random.choice(self.defender_strategy())
                else:
                    attack_target = random.choice([i for i in range(self.num_targets) if i not in self.defender_strategy()])
        '''

        self.file.write(f"Attacker attacks target: {attack_target}\n")
        return attack_target

    '''
    def update_beliefs(self, target_attacked):
        likelihood = 0.5 if target_attacked not in self.defender_strategy() else 1 - 0.5
        total_prob = self.belief_type1 * likelihood + (1 - self.belief_type1) * (1 - likelihood)
        self.belief_type1 = likelihood * self.belief_type1 / total_prob
        self.history.append(target_attacked)  # Storing attacked target in history
        self.file.write(f"Updated belief of attacker being type 1: {self.belief_type1}\n")
    '''
    def update_beliefs(self, target_attacked):
        likelihood = 0.5 if target_attacked not in self.defender_strategy() else 1 - 0.5
        total_prob = self.belief_type1 * likelihood + (1 - self.belief_type1) * (1 - likelihood)
        self.belief_type1 = likelihood * self.belief_type1 / total_prob
        self.history.append(target_attacked)  # Storing attacked target in history
        self.file.write(f"Updated belief of attacker being type 1: {self.belief_type1}\n")

    def run_single_instance(self, scenario, belief_type1):
        self.belief_type1 = belief_type1
        deceptive_actions = 0
        for _ in range(self.steps):  # Time step of 2
            # 1. Attacker chooses a target to attack
            target_attacked = self.simulate_attack(scenario)
            
            # 2. Defender then chooses targets to defend based on the attacker's choice
            defended_targets = self.defender_strategy()
            
            # 3. Update beliefs and history
            self.update_beliefs(target_attacked)
            self.history.append(defended_targets)  # Storing defended targets in history
            
            if target_attacked in defended_targets:
                self.defender_utilities.append(self.rewards[target_attacked])
                self.attacker_utilities.append(-self.rewards[target_attacked])
            else:
                self.defender_utilities.append(-self.penalties[target_attacked])
                self.attacker_utilities.append(self.penalties[target_attacked])
            
            if self.belief_type1 >= .5 and self.is_type1 == False or self.belief_type1 < .5 and self.is_type1 == True:
                deceptive_actions += 1

        return deceptive_actions / self.steps


    def run_experiment(self, scenario, belief_type1, instances=220):
        total_deceptive_actions = sum([self.run_single_instance(scenario, belief_type1) for _ in range(instances)])
        return {"deceptive actions / instances" : total_deceptive_actions / instances, "defender utilites" : self.defender_utilities, "attacker utilities" : self.attacker_utilities}

with open("output.txt", "w") as file:
    # Running the experiment
    target_options = [4, 6, 8, 10, 12]
    attacker_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}
    defender_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}

    k_resources_options = [1, 2, 3, 4, 5]  # Ensure k < n for each n in target_options
    prior_probs = [i/100 for i in range(0, 101, 5)]
    scenarios = ["Perfect Bayesian", "Myopic w/ Learn", "Deceptive w/ Learn"]
    # 2 step game
    plt.figure(figsize=(15, 9))
    for n, k in zip(target_options, k_resources_options):
        avg_deceptive_actions_over_scenarios = []
        for p in prior_probs:
            avg_deceptive_actions_for_prior = []
            for scenario in scenarios:
                game = SecurityGame(num_targets=n, k_resources=k, file=file, steps=2).run_experiment(scenario, p)
                avg_deceptive_actions_for_prior.append(game.get("deceptive actions / instances"))
                attacker_results_per_scenario[scenario].append(game.get("attacker utilities"))
                defender_results_per_scenario[scenario].append(game.get("defender utilites"))


            avg_deceptive_actions_over_scenarios.append(sum(avg_deceptive_actions_for_prior) / len(scenarios))
        plt.plot(prior_probs, avg_deceptive_actions_over_scenarios, label=f'N={n}')
    
    plt.title("Probability of Deceptive Action for T=2 Time Steps")
    plt.xlabel("Prior Probability of Attacker Type 1")
    plt.ylabel("Probability of Deceptive Action")
    plt.legend()
    plt.grid(True)
    plt.show()
    #plot utilities for attacker and defene
    '''
    plt.figure(figsize=(15, 9))
    holder = []
    for scenario in attacker_results_per_scenario.keys():
        for result in attacker_results_per_scenario.get(scenario):
            for val in result:
                holder.append(val)
        plt.plot(holder, label=scenario)
        holder = []
    
    plt.title("Attacker Utilities for T=2 Time Steps")
    plt.xlabel("Prior Probability of Attacker Type 1")
    plt.ylabel("Attacker Utility")
    plt.legend()
    plt.grid(True)
    plt.show()
    '''


    #reset utilities
    attacker_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}
    defender_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}
    # 3 step game
    plt.figure(figsize=(15, 9))
    for n, k in zip(target_options, k_resources_options):
        avg_deceptive_actions_over_scenarios = []
        for p in prior_probs:
            avg_deceptive_actions_for_prior = []
            for scenario in scenarios:
                avg_deceptive_actions_for_prior.append(SecurityGame(num_targets=n, k_resources=k, file=file, steps=3).run_experiment(scenario, p).get("deceptive actions / instances"))
            avg_deceptive_actions_over_scenarios.append(sum(avg_deceptive_actions_for_prior) / len(scenarios))
        plt.plot(prior_probs, avg_deceptive_actions_over_scenarios, label=f'N={n}')

    plt.title("Probability of Deceptive Action for T=3 Time Steps")
    plt.xlabel("Prior Probability of Attacker Type 1")
    plt.ylabel("Probability of Deceptive Action")
    plt.legend()
    plt.grid(True)
    plt.show()

