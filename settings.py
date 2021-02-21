debug = True

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

start_temperature = 100
temperature_rate = 0.8

exit_criteria = "temp"
exit_temperature = 5

n_moves = 5