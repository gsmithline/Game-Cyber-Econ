import matplotlib.pyplot as plt
from SecGame1 import SecurityGame

def StartExperiment1():
    with open("output.txt", "w") as file:
        # Running the experiment
        target_options = [4, 6, 8, 10, 12]
        attacker_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}
        defender_results_per_scenario = {"Perfect Bayesian": [], "Myopic w/ Learn": [], "Deceptive w/ Learn": []}

        k_resources_options = [2, 3, 4, 5, 6]  # Ensure k < n for each n in target_options
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

StartExperiment1()