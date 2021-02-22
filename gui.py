import os
from settings import *
from netlist_parser import *
from annealing import *


# Initialize the debug log
debug_log.write("\n\n{}\n".format("="*20))
debug_log.write(time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime()))
debug_log.write("{}\n".format("="*20))


# If only running 1 circuit
if single_circuit:
    
    # Choose circuit
    filename = input("Name of circuit: ")

    # Open circuit
    debug_print("Reading configurations for {}...".format(filename))
    configs, nets = parse_file("./circuits/{}.txt".format(filename))


    simulated_annealing = SimAnneal()
    simulated_annealing.setup(configs, nets)
    simulated_annealing.full_anneal()

else:
    results_file = "results__{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
    initalize_results_file(results_file)
    results_log = open(results_file, "a")

    circuits = [name for name in os.listdir("./circuits")]

    simulated_annealing = SimAnneal()
    
    cumulative_cost = 0
    print("Running simulated annealing for {} benchmark circuits.".format(len(circuits)))

    # Iterate through circuits
    for circuit in circuits:
        
        # Load circuit
        print("Reading configurations for {}...".format(circuit))
        configs, nets = parse_file("./circuits/{}".format(circuit))


        # Set up SA
        simulated_annealing.setup(configs, nets)
        
        cost = simulated_annealing.full_anneal()
        cumulative_cost += cost
                
        # Update cost in results log
        num_iterations = simulated_annealing.iteration
        results_log = open("logs/{}".format(results_file), "a")
        results_log.write("{circuit}\t{cost}\t{it}\n".format(circuit=circuit.replace(".txt", ""), cost=cost, it=num_iterations))
        results_log.close()

    results_log = open("logs/{}".format(results_file), "a")
    results_log.write("Finished at {}\n".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))

    # Calculate average cost
    print("Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)))
    results_log = open("logs/{}".format(results_file), "a")
    results_log.write("\nFinal Average Cost: {}\n".format(float(cumulative_cost) / len(circuits)))
    results_log.close()
    
# Close debug log
debug_log.close()
