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

    # Initialize GUI
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
        
    # Initialize graphing
    fig = Figure()
    ax = fig.add_subplot(111)

    # Initialize annealing
    simulated_annealing = SimAnneal(c, ax)
    simulated_annealing.setup(configs, nets)

    # Add buttons
    button_frame = Frame(root, width=screensize["width"])
    place_button = Button(button_frame, text ="Randomly Place", command=simulated_annealing.random_placement)
    it_button = Button(button_frame, text ="Iterate", command=simulated_annealing.anneal)
    anneal_button = Button(button_frame, text ="Run Simulated Annealing", command=simulated_annealing.full_anneal)

    button_frame.grid(row=1, column=0)
    place_button.grid(row=0, column=0)
    it_button.grid(row=0, column=1)
    anneal_button.grid(row=0, column=2)
    
    # Add graph
    graphFrame = Frame(root, width=screensize["width"])
    graphFrame.grid(row=0, column=1)
    graph = FigureCanvasTkAgg(fig, graphFrame)
    graph.draw()
    graph.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=graph_delay, blit=False)

    # Run GUI
    root.mainloop()


# Otherwise, run "benchmark"
else:
    
    # Initialize results log
    results_file = "results__{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))

    # Get list of benchmark circuits
    circuits = [name for name in os.listdir("./circuits")]
    
    # Initialize GUI
    root = Tk()
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()
            
    fig = Figure()
    ax = fig.add_subplot(111)
    
    # Initialize graph
    graphFrame = Frame(root, width=screensize["width"])
    graphFrame.grid(row=0, column=1)
    graph = FigureCanvasTkAgg(fig, graphFrame)
    graph.draw()
    graph.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    # Initalize SA
    simulated_annealing = SimAnneal(c, ax)

    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=graph_delay, blit=False)
    
    cumulative_cost = 0
    print("Running simulated annealing for {} benchmark circuits.".format(len(circuits)))

    # Iterate through circuits
    for circuit in circuits:
        
        # Load circuit
        print("Reading configurations for {}...".format(circuit))
        configs, nets = parse_file("./circuits/{}".format(circuit))

        # Update GUI grid
        grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
        grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)

        # Set up SA
        simulated_annealing.setup(configs, nets)
        
        # Add circuit label to GUI
        c.create_text(
            grid["left"],
            20,
            text="Circuit: {}".format(circuit.replace(".txt", "")),
            fill="black",
            font=('Arial',20,'bold'),
            anchor=W
        )
        
        # Update GUI
        debug_print("Drawing grid...")
        for y in range(configs["rows"] * 2):
            c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
        for x in range(configs["cols"] + 1):
            for y in range(configs["rows"]):
                c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)

        # Run SA and track cost
        cost = simulated_annealing.full_anneal()
        cumulative_cost += cost
        
        # Update cost in results log
        results_log = open("logs/{}".format(results_file), "a")
        results_log.write("{circuit}\t{cost}\n".format(circuit=circuit.replace(".txt", ""), cost=cost))
        results_log.close()
        
        # Save an image of the output
        c.postscript(file="photos/{circuit}_{time}.ps".format(circuit=circuit.replace(".txt", ""), time=time.strftime("%Y-%m-%d_%H-%M", time.localtime())), colormode='color')
        
        # Clear the canvas
        c.delete("all")


    # Calculate average cost
    print("Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)))
    results_log.write("\nFinal Average Cost: {}\n".format(float(cumulative_cost) / len(circuits)))
    ax.clear()
    
    # Update the GUI with final result
    c.create_text(
        screensize["width"] / 2,
        screensize["height"] / 2,
        text="Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)),
        fill="black",
        font=('Arial',30,'bold')
    )
    
# Close debug log
debug_log.close()

# Run GUI
root.mainloop()