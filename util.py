from settings import *
import time

def debug_print(content):
    '''
    Special print statement (prints only in debug mode, otherwise logs to file)
    Input:
        content - content to be printed
    '''
    if debug:
        print(content)
    else:
        debug_log.write(str(content))
        debug_log.write("\n")

def calculate_half_perimeter(net, cells):
    '''
    Calculate the half perimeter for a net
    Input:
        net - [cell0, cell1, ...]
        cells - {cell0: (x0, y0), cell1: (x1, y1), ...}
    Output:
        half_perimeter - calculated half perimeter
    '''
    
    # Initialize bounds to the first cell
    smallest_x = cells[net[0]][0]
    smallest_y = cells[net[0]][1]
    largest_x = cells[net[0]][0]
    largest_y = cells[net[0]][1]
    
    # Search for the smallest and largest bound of the bounding box
    for cell in net:
        if cells[cell][0] < smallest_x:
            smallest_x = cells[cell][0]
            
        elif cells[cell][0] > largest_x:
            largest_x = cells[cell][0]
            
        if cells[cell][1] < smallest_y:
            smallest_y = cells[cell][1]
            
        elif cells[cell][1] > largest_y:
            largest_y = cells[cell][1]
            
    # Calculate half perimenter
    if "2" in no_assumptions:
        # No assumption 2
        half_perimeter = (largest_x - smallest_x + 1) + (largest_y - smallest_y + 1)
    else:
        half_perimeter = (largest_x - smallest_x) + (largest_y - smallest_y)
        
    # No assumption 1
    if "1" in no_assumptions:
        # Add in routing track (only in the vertical dimension)
        half_perimeter += (largest_y - smallest_y)
    
    debug_print("Half perimeter calculated from ({x1}, {y1}) to ({x2}, {y2}) = {h}".format(x1=smallest_x, y1=smallest_y, x2=largest_x, y2=largest_y, h=half_perimeter))
    return half_perimeter
    
    
def add_text(x, y, c, grid, text, colour="black", tag=""):
    """
    Add (text) on the canvas (c) at (x, y) coordinates with (grid) size in (colour) with (tag)
    """
    c.create_text(
        grid["left"] + x * grid["x"] + grid["x"] / 2,
        grid["top"] + (y * 2) * grid["y"] + grid["y"] / 2,
        text=text,
        fill=colour,
        tag=tag,
    )
    
    
def draw_line(orig, dest, c, grid, colour="gray", tag="", extra_point=None):
    '''
    Draw a line from (orig) to (dest) on canvas (c) using (grid) with (colour) and (tag)
    extra_point to draw a curve instead of a straight line 
    '''
    
    # Calculate starting position and end positions on the canvas grid
    start_x = grid["left"] + orig[0] * grid["x"] + grid["x"]/2
    start_y = grid["top"] + (orig[1] * 2) * grid["y"] + grid["y"]/2
    end_x = grid["left"] + dest[0] * grid["x"] + grid["x"]/2
    end_y = grid["top"] + (dest[1] * 2) * grid["y"] + grid["y"]/2
    
    # Draw line
    if extra_point == None:
        c.create_line(
            start_x, 
            start_y, 
            end_x,
            end_y,
            width=3,
            fill=colour,
            tag=tag
        )
        
    # Draw curve
    else:
        # Determine midpoint from start to end and offset
        midpoint_x = start_x + (end_x - start_x)/2 + extra_point * 10
        midpoint_y = start_y + (end_y - start_y)/2 + extra_point * 10
        
        # Draw the curve
        c.create_line(
            start_x, 
            start_y, 
            midpoint_x,
            midpoint_y,
            end_x,
            end_y,
            width=2,
            fill=colour,
            tag=tag,
            smooth=1
        )
        
        
def check_add_cells(cell, additional_cells):
    '''
    Check if a (cell) has already been added to the list of (additional_cells)
    Input:
        cell - the cell to check for
        additional_cells - [{"cell": cell, "cell_xy": (x, y)}, ...]
    Output:
        True if cell is already in the list
        False otherwise
    '''
    for additional_cell in additional_cells:
        if additional_cell["cell"] == cell:
            return True
            
    return False
    

def initalize_results_file(filename):
    
    results_log = open("logs/{}".format(filename), "w+")

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
    results_log.write("Range Window: {}\n".format(range_window))
    results_log.write("Range Window Size: {}\n".format(window_size))
    results_log.write("Shuffle: {}\n".format(shuffle))
    results_log.write("Ripple: {}\n".format(ripple))
    results_log.write("No Assumptions: {}\n".format(no_assumptions))
    results_log.write("\n{}\n\n".format("*"*50))
    
    results_log.write("Circuit\tCost\tIterations\n".format(no_assumptions))
    results_log.close()
    