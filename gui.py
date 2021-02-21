import os
from settings import *
from netlist_parser import *
from annealing import *

debug_log.write("\n\n{}\n".format("="*20))
debug_log.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
debug_log.write("{}\n".format("="*20))


if single_circuit:
    filename = input("Name of circuit: ")

    debug_print("Reading configurations for {}...".format(filename))
    configs, nets = parse_file("./circuits/{}.txt".format(filename))


    simulated_annealing = SimAnneal()
    simulated_annealing.setup(configs, nets)
    simulated_annealing.full_anneal()

else:
    results_file = "logs/results__{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
    results_log = open(results_file, "w+")

    results_log.write("\n\n{}\n".format("="*20))
    results_log.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
    results_log.write("{}\n".format("="*20))

    results_log.write("Settings\n")
    results_log.write("Starting Temperature: {}\n".format(start_temperature))
    results_log.write("Temperature Rate: {}\n".format(temperature_rate))
    results_log.write("Exit Criteria: {}\n".format(exit_criteria))
    results_log.write("Exit Temperature: {}\n".format(exit_temperature))
    results_log.write("Exit Iterations: {}\n".format(exit_iterations))
    results_log.write("Dynamic Moves Per Temperature: {}\n".format(dynamic_n_moves))
    results_log.write("Moves Per Temperature: {}\n".format(n_moves))
    results_log.write("k (Moves Per Temperature): {}\n".format(k_n_moves))
    results_log.write("\n{}\n\n".format("*"*50))

    results_log.close()
    results_log = open(results_file, "a")


    circuits = [name for name in os.listdir("./circuits")]

    simulated_annealing = SimAnneal()
    
    cumulative_cost = 0
    print("Running simulated annealing for {} benchmark circuits.".format(len(circuits)))

    for circuit in circuits:
        
        print("Reading configurations for {}...".format(circuit))
        configs, nets = parse_file("./circuits/{}".format(circuit))


        simulated_annealing.setup(configs, nets)
        
        cost = simulated_annealing.full_anneal()
        cumulative_cost += cost
        
        results_log.write("{circuit}\t{cost}\n".format(circuit=circuit.replace(".txt", ""), cost=cost))

    results_log.write("Finished at {}\n".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))

    print("Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)))
    results_log.write("\nFinal Average Cost: {}\n".format(float(cumulative_cost) / len(circuits)))
    results_log.close()
    
debug_log.close()
