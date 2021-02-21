debug = True
single_circuit = True
update_gui = True

debug_log = open("logs/debug_log.txt", "a+")

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
temperature_rate = 0.9

exit_criteria = "multiple_no_improvement"
exit_temperature = 0
exit_iterations = 20

n_moves = 10
dynamic_n_moves = False
k_n_moves = 1

range_window = True
window_size = 0.3

shuffle = False
shuffle_window = (1, 1)
ripple = False