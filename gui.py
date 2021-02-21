import os
from tkinter import *
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from settings import *
from netlist_parser import *
from annealing import *

if single_circuit:
    # filename = input("Name of circuit: ")
    filename = "alu2"

    print("Reading configurations for {}...".format(filename))
    configs, nets = parse_file("./circuits/{}.txt".format(filename))


    root = Tk()
    grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
    grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)
    frame = Frame(root, width=screensize["width"], height=screensize["height"])
    frame.grid(row=0, column=0)
    c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
    c.pack()


    print("Drawing grid...")
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
    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=200, blit=False)


    # Run GUI
    root.mainloop()
    
else:
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

    configs, nets = parse_file("./circuits/alu2.txt")
    simulated_annealing = SimAnneal(c, ax)

    ani = FuncAnimation(fig, simulated_annealing.animate, np.arange(1, 200), interval=200, blit=False)
    
    cumulative_cost = 0
    print("Running simulated annealing for {} benchmark circuits.".format(len(circuits)))

    for circuit in circuits:
        
        print("Reading configurations for {}...".format(circuit))
        configs, nets = parse_file("./circuits/{}".format(circuit))

        grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
        grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)

        simulated_annealing.setup(configs, nets)
        
        print("Drawing grid...")
        for y in range(configs["rows"] * 2):
            c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
        for x in range(configs["cols"] + 1):
            for y in range(configs["rows"]):
                c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)

        cost = simulated_annealing.full_anneal()
        
        print("Final Cost: {}".format(cost))
        cumulative_cost += cost
        
        c.delete("all")


    print("Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)))
    ax.clear()
    c.create_text(
        10,
        10,
        text="Final Average Cost: {}".format(float(cumulative_cost) / len(circuits)),
        fill="black",
        font=('Arial',30,'bold')
    )
    
    # Run GUI
    root.mainloop()