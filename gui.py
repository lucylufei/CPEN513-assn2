import os
from tkinter import *
from tkinter.ttk import *
from settings import *
from netlist_parser import *
from annealing import *


# filename = input("Name of circuit: ")
filename = "simpletest"

print("Reading configurations for {}...".format(filename))
configs, nets = parse_file("./circuits/{}.txt".format(filename))


root = Tk()
grid["x"] = (grid["right"] - grid["left"]) / configs["cols"]
grid["y"] = (grid["bottom"] - grid["top"]) / (configs["rows"] * 2 - 1)
frame = Frame(root, width=screensize["width"], height=screensize["height"])
frame.pack()
c = Canvas(frame, bg=background_colour, width=screensize["width"], height=screensize["height"])
c.pack()


print("Drawing grid...")
for y in range(configs["rows"] * 2):
    c.create_line(grid["left"], grid["top"] + y * grid["y"], grid["right"], grid["top"] + y * grid["y"], fill=line_colour)
for x in range(configs["cols"] + 1):
    for y in range(configs["rows"]):
        c.create_line(grid["left"] + x * grid["x"], grid["top"] + (y * 2) * grid["y"], grid["left"] + x * grid["x"], grid["top"] + (y * 2 + 1) * grid["y"], fill=line_colour)
    
    
simulated_annealing = SimAnneal(c, configs, nets)

button_frame = Frame(root, width=screensize["width"])
place_button = Button(button_frame, text ="Randomly Place", command=simulated_annealing.random_placement)
it_button = Button(button_frame, text ="Iterate", command=simulated_annealing.anneal)

button_frame.pack()
place_button.grid(row=0, column=0)
it_button.grid(row=0, column=1)
    
# Run GUI
root.mainloop()