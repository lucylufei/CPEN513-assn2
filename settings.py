# Debug mode
debug = False

# Single circuit mode
single_circuit = True

# Update GUI (True for full speed, False for delayed updates)
update_gui = True

# Debug file
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

# Display settings
display_delay = 0
graph_delay = 2000

# Cost function settings ("1" to ignore assumption 1, "2" to ignore assumption 2, "12" to ignore both)
no_assumptions = ""


''' 
ANNEALING SCHEDULE
'''

# Starting temperature
start_temperature = 20
# Temperature update
temperature_rate = 0.9

# Exit criteria ("temp", "no_improvement", or "multiple_no_improvement")
exit_criteria = "multiple_no_improvement"
# Temperature threshold if using "temp"
exit_temperature = 0
# Number of iterations with no improvements if not using "temp"
exit_iterations = 20

# Choose number of moves based on circuit size (use constant number if False)
dynamic_n_moves = True
# Number of moves per temperature (if not dynamic)
n_moves = 10
# k value for n=kN^(4/3) (if dynamic)
k_n_moves = 1

# Range window optimization
range_window = True
# Size of range window
window_size = 0.3

# Shuffle optimization
shuffle = False
ripple = False
