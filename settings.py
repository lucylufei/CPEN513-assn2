import time

debug = False
single_circuit = False
update_gui = False

debug_log = open("logs/debug_{}.txt".format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())), "w+")

# GUI settings
screensize = {
    "width": 1000, 
    "height": 500
}

canvas_border = 50

grid = {}
grid["left"] = canvas_border
grid["right"] = screensize["width"] - canvas_border
grid["top"] = canvas_border
grid["bottom"] = screensize["height"] - canvas_border

background_colour = "white"
line_colour = "black"
line_curve = False

wire_colour_palette = [
    "pink",
    "plum", 
    "turquoise",
    "lightblue",
    "salmon",
    "lightgreen",
    "lavender",
    "DarkSeaGreen",
    "coral",
    "blue", 
    "green",
    "yellow"
]

display_delay = 0
graph_delay = 2000

start_temperature = 100
temperature_rate = 0.7

exit_criteria = "multiple_no_improvement"
exit_temperature = 0
exit_iterations = 10

n_moves = 40
dynamic_n_moves = True
k_n_moves = 1
