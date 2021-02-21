from settings import *

def debug_print(content):
    if debug:
        print(content)
    else:
        # debug_log.write(str(content))
        # debug_log.write("\n")
        pass

def calculate_half_perimeter(net, cells):
    '''
    Net: [cell0, cell1, ...]
    Cells: {cell0: (x0, y0), cell1: (x1, y1), ...}
    '''
    
    smallest_x = cells[net[0]][0]
    smallest_y = cells[net[0]][1]
    largest_x = cells[net[0]][0]
    largest_y = cells[net[0]][1]
    
    for cell in net:
        if cells[cell][0] < smallest_x:
            smallest_x = cells[cell][0]
            
        elif cells[cell][0] > largest_x:
            largest_x = cells[cell][0]
            
        if cells[cell][1] < smallest_y:
            smallest_y = cells[cell][1]
            
        elif cells[cell][1] > largest_y:
            largest_y = cells[cell][1]
            
            
    half_perimeter = (largest_x - smallest_x + 1) + (largest_y - smallest_y + 1)
    
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
    start_x = grid["left"] + orig[0] * grid["x"] + grid["x"]/2
    start_y = grid["top"] + (orig[1] * 2) * grid["y"] + grid["y"]/2
    end_x = grid["left"] + dest[0] * grid["x"] + grid["x"]/2
    end_y = grid["top"] + (dest[1] * 2) * grid["y"] + grid["y"]/2
    
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
    else:
        midpoint_x = start_x + (end_x - start_x)/2 + extra_point * 10
        midpoint_y = start_y + (end_y - start_y)/2 + extra_point * 10
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
    for additional_cell in additional_cells:
        if additional_cell["cell"] == cell:
            return True
            
    return False