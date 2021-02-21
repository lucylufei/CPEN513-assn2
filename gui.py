import os
import time
from tkinter import *
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
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


    root = Tk()
    grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
    grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()

    c.create_text(
        grid["left"],
        20,
        text="Circuit: {}".format(filename),
        fill="black",
        font=('Arial',20,'bold'),
        anchor=W
    )

    debug_print("Drawing grid...")
    for y in range(configs["rows"] * 2):
        c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
    for x in range(configs["cols"] + 1):
        for y in range(configs["rows"]):
            c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)
        
    fig = Figure()
    ax = fig.add_subplot(111)

    simulated_annealing = SimAnneal(c, ax)
    simulated_annealing.setup(configs, nets)

    button_frame = Frame(root, width=screensize["width"])
    place_button = Button(button_frame, text ="Randomly Place", command=simulated_annealing.random_placement)
    it_button = Button(button_frame, text ="Iterate", command=simulated_annealing.anneal)
    anneal_button = Button(button_frame, text ="Run Simulated Annealing", command=simulated_annealing.full_anneal)

    button_frame.grid(row=1, column=0)
    place_button.grid(row=0, column=0)
    it_button.grid(row=0, column=1)
    anneal_button.grid(row=0, column=2)

    graphFrame = Frame(root, width=screensize["width"])
    graphFrame.grid(row=0, column=1)
    graph = FigureCanvasTkAgg(fig, graphFrame)
    graph.draw()
    graph.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=graph_delay, blit=False)


    # Run GUI
    root.mainloop()
    
else:
    results_log = open("logs/results__{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())), "w+")

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

    circuits = [name for name in os.listdir("./circuits")]
    
    root = Tk()
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()
            
    fig = Figure()
    ax = fig.add_subplot(111)
    
    graphFrame = Frame(root, width=screensize["width"])
    graphFrame.grid(row=0, column=1)
    graph = FigureCanvasTkAgg(fig, graphFrame)
    graph.draw()
    graph.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    simulated_annealing = SimAnneal(c, ax)

    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=graph_delay, blit=False)
    
    cumulative_cost = 0
    print("Running simulated annealing for {} benchmark circuits.".format(len(circuits)))

    for circuit in circuits:
        
        print("Reading configurations for {}...".format(circuit))
        configs, nets = parse_file("./circuits/{}".format(circuit))

        grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
        grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)

        simulated_annealing.setup(configs, nets)
        
        c.create_text(
            grid["left"],
            20,
            text="Circuit: {}".format(circuit.replace(".txt", "")),
            fill="black",
            font=('Arial',20,'bold'),
            anchor=W
        )
        debug_print("Drawing grid...")
        for y in range(configs["rows"] * 2):
            c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
        for x in range(configs["cols"] + 1):
            for y in range(configs["rows"]):
                c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)

        cost = simulated_annealing.full_anneal()
        cumulative_cost += cost
        
        results_log.write("{circuit}\t{cost}\n".format(circuit=circuit.replace(".txt", ""), cost=cost))
        
        c.postscript(file="photos/{circuit}_{time}.ps".format(circuit=circuit.replace(".txt", ""), time=time.strftime("%Y-%m-%d_%H-%M", time.localtime())), colormode='color')
        
        c.delete("all")


    print("Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)))
    results_log.write("\nFinal Average Cost: {}\n".format(float(cumulative_cost) / len(circuits)))
    ax.clear()
    c.create_text(
        screensize["width"] / 2,
        screensize["height"] / 2,
        text="Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)),
        fill="black",
        font=('Arial',30,'bold')
    )
    results_log.close()
    
debug_log.close()

# Run GUI
root.mainloop()