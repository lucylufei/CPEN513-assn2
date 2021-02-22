import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import copy
import math
import time
from util import *
from settings import *

np.set_printoptions(threshold=np.inf, linewidth=np.inf)


class SimAnneal:
    '''
    Implementation of Simulated Annealing
    '''
    
    def __init__(self, canvas, ax):
        '''
        Initialize class with permanent variables
        '''
        self.c = canvas
        self.ax = ax
        
        
    def setup(self, configs, nets):
        '''
        Setup the simulation with the current circuit
        '''
        
        # Circuit parameters
        self.configs = configs
        self.nets = nets
        
        # Initialize placement map (NaN for empty cells)
        self.placement = np.zeros((configs["cols"], configs["rows"]))
        self.placement[:] = np.NaN
        random.seed()
        
        # Initialize simulation variables
        self.cells = {}
        self.cost = {}
        self.new_cost = {}
        self.current_cost = 0
        self.delta_cost = 0
        self.temperature = start_temperature
        self.iteration = 0
        self.exit_tracker = 0
        self.initalized = False
        
        # Set number of moves per temperature (either based on circuit size or a fixed value)
        if dynamic_n_moves:
            self.n_moves = round(k_n_moves * math.pow(configs["cells"], float(4)/3))
        else:
            self.n_moves = n_moves
        
        # Label temperature
        self.c.create_text(
            grid["right"] - 100,
            20,
            text="Temp: {}".format(round(self.temperature, 2)),
            fill="black",
            font=('Arial',20,'bold'),
            tag="temp"
        )
        
    
    def animate(self, frame=None):
        '''
        Update matplotlib graph
        '''
        
        # Update graph if the initial cost has already been calculated
        if self.initalized:
            self.ax.clear()
            self.ax.plot(self.x, self.y)
        
        
    def random_placement(self):
        '''
        Initialize circuit with a random placement
        '''
        # Reset all placement
        self.placement[:] = np.NaN
        
        # Make a list of possible coordinates
        possible_placements = [(x, y) for x in range(0, self.configs["cols"]) for y in range(0, self.configs["rows"])]
        
        # Place every cell
        for i in range(self.configs["cells"]):
            (x, y) = random.choice(possible_placements)
            possible_placements.remove((x, y))
            # Track which cell is in which coordinate
            self.placement[x, y] = i
            # Track which coordinate each cell is at
            self.cells[i] = (x, y)
            
        # Double check that all cells have been accounted for
        assert len(self.cells) == self.configs["cells"]
        
        debug_print("Current Placement:")
        debug_print(self.placement)
        
        # Update the GUI
        self.draw_connections()
        self.update_labels()
        
        # Calculate the initial cost
        self.calculate_cost()
        
        # Mark circuit as initialized
        self.initalized = True
        
        # Track graph x and y
        self.x = [0]
        self.y = [self.current_cost]
        
        # Initialize plot
        self.ax.plot(self.x, self.y)
        self.ax.set_ylabel("Half Perimeter Cost")
        self.ax.set_xlabel("Iteration")

                
    def update_labels(self):
        '''
        Update cell labels on GUI
        '''
        
        # Delete all previous labels
        self.c.delete("cell")
        # Add new labels
        for cell in self.cells:
            add_text(self.cells[cell][0], self.cells[cell][1], self.c, grid, cell, tag="cell")
        
        
    def draw_connections(self):
        '''
        Update connections on GUI
        '''
        
        # Delete all previous wires
        self.c.delete("wires")
        # Draw new wires
        for i, net in enumerate(self.nets):
            # Draw from first cell to the rest
            orig = self.cells[net[0]]
            for cell in net[1:]:
                dest = self.cells[cell]
                # Draw a curve
                if line_curve:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires", extra_point=i)
                # Draw a line
                else:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires")
        
            
    def calculate_cost(self):
        '''
        Calculate the half perimeter cost
        '''
        
        # Track the cost for each net
        for i, net in enumerate(self.nets):
            self.cost[i] = calculate_half_perimeter(net, self.cells)
            
        # Sum the cost and update globally
        self.update_cost()
        
            
    def calculate_delta_cost(self, cell1, cell2, temp_placement, additional_cells=None):
        '''
        Calculate incremental half perimenter cost
        '''
        delta_cost = 0
        
        # Check each net to see if the cost has changed
        for i, net in enumerate(self.nets):            
            cost_updated = False
            # If the cells being swapped belong to this net, update the cost
            if cell1 in net or cell2 in net:
                self.new_cost[i] = calculate_half_perimeter(net, temp_placement)
                delta_cost += self.new_cost[i] - self.cost[i]
                cost_updated = True
                
            # If there are more than 2 cells that have been updated, update the cost for any nets with those cells
            elif additional_cells:
                for cell in additional_cells:
                    if cell["cell"] in net:
                        debug_print("Cell {c} in net {n}".format(c=cell["cell"], n=net))
                        self.new_cost[i] = calculate_half_perimeter(net, temp_placement)
                        delta_cost += self.new_cost[i] - self.cost[i]
                        cost_updated = True

            # If the net has not changed, set new cost equal to old cost
            if not cost_updated:
                self.new_cost[i] = self.cost[i]
            
        debug_print("Delta Cost: {}".format(delta_cost))
        
        # Return just the change in cost
        return delta_cost
        
        
    def update_cost(self):
        '''
        Update cost globally
        '''
        
        # Sum up total cost
        total_cost = sum(self.cost[i] for i in range(self.configs["nets"]))
        debug_print("Total Cost: {}".format(total_cost))
        
        # Update global cost
        self.current_cost = total_cost
        
        
    def no_exit(self):
        '''
        Exit condition
        '''
        
        # Exit once the temperature is below a threshold
        if exit_criteria == "temp":
            return self.temperature > exit_temperature
            
        # Exit if there is no improvement and the temperature is already at 0
        elif exit_criteria == "no_improvement":
            return self.delta_cost < 0 or self.temperature != 0
            
        # Exit if there have been multiple iterations of no improvement and the temperature is already at 0
        elif exit_criteria == "multiple_no_improvement":
            if self.delta_cost > 0 and self.temperature == 0:
                self.exit_tracker += 1
            else:
                self.exit_tracker = 0
            return self.exit_tracker < exit_iterations
            
        # Otherwise, the exit condition is missing or incorrect
        else:
            raise Exception
            
            
    def update_swap(self, cell1, cell2, cell1_xy, cell2_xy, additional_cells=None):
        '''
        Commit the current swap
        '''
        
        # Move cell1 to the location of cell2
        self.placement[cell2_xy] = cell1
        if not np.isnan(cell1):
            self.cells[cell1] = cell2_xy
            
        # For settings with multiple swaps
        if additional_cells:
            prev_cell = cell2
            
            # Iteratively update each cell (moving cell2 to cell3, cell3 to cell4, ...)
            for additional_cell in additional_cells:
                self.placement[additional_cell["cell_xy"]] = prev_cell
                if not np.isnan(prev_cell):
                    self.cells[prev_cell] = additional_cell["cell_xy"]
                prev_cell = additional_cell["cell"]
        
        # Otherwise, just perform a simple swap
        else:
            # Move cell2 to the location of cell1
            self.placement[cell1_xy] = cell2
            if not np.isnan(cell2):
                self.cells[cell2] = cell1_xy
        
        # Update the official cost
        self.cost = copy.deepcopy(self.new_cost)
        debug_print("New Placement:")
        debug_print(self.placement)
        
        # Sum up the total cost and update the canvas
        self.update_cost()
        self.c.update()
        
        # Update GUI elements
        if update_gui:
            self.draw_connections()
            self.update_labels()
            time.sleep(display_delay)
        
        
    def anneal(self):
        '''
        Swaps at one temperature
        '''
        
        # Track number of accepted swaps
        accepted_swap = 0
        
        # Run for n moves
        for i in range(self.n_moves):
            self.iteration += 1
            
            # Create a temperary placement map
            temp_placement = copy.deepcopy(self.cells)
            
            # Make a list of cells
            cells = list(range(0, self.configs["cells"]))
            
            # Choose random cells to swap
            cell1 = random.choice(cells)
            cell1_xy = self.cells[cell1]
            cells.remove(cell1)
            
            # Add in possibility of empty cell
            cells.append(self.configs["cells"])
            
            # Choose another cell within the range
            if range_window:
                
                # Calculate the window
                window_x = round(window_size*self.configs["cols"])
                window_y = round(window_size*self.configs["rows"])
                x_min = 0 if cell1_xy[0] - window_x < 0 else cell1_xy[0] - window_x
                x_max = self.configs["cols"]-1 if cell1_xy[0] + window_x >= self.configs["cols"] else cell1_xy[0] + window_x
                y_min = 0 if cell1_xy[1] - window_y < 0 else cell1_xy[1] - window_y
                y_max = self.configs["rows"]-1 if cell1_xy[1] + window_y >= self.configs["rows"] else cell1_xy[1] + window_y
                
                debug_print("Cell1: ({x}, {y}) -> range ({xmin}-{xmax}, {ymin}-{ymax})".format(x=cell1_xy[0], y=cell1_xy[1], xmin=x_min, xmax=x_max, ymin=y_min, ymax=y_max))
                
                # Randomly pick second location
                cell2_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                
                # Make sure the swap isn't with itself
                while cell2_xy == cell1_xy:
                    cell2_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                
                cell2 = self.placement[cell2_xy]
                
            # Choose any cell
            else:
                cell2 = random.choice(cells)
                
            # If using range window, handle case of second choice being an empty cell
            if not range_window:
                if cell2 == self.configs["cells"]:
                    cell2 = np.NaN
                    
                    # Choose any NaN (empty) cell location 
                    while True:
                        x = random.randint(0, self.configs["cols"]-1)
                        y = random.randint(0, self.configs["rows"]-1)
                        
                        # Check that the block is currently empty
                        if np.isnan(self.placement[x, y]):
                            cell2_xy = (x, y)
                            break
                else:
                    cell2_xy = self.cells[cell2]
                
            # If using "ripple" configuration (only valid if cell2 is not an empty cell)
            if ripple and not np.isnan(cell2):
                additional_cells = []
                
                # Choose another cell in a new window
                window_x = round(window_size*self.configs["cols"])
                window_y = round(window_size*self.configs["rows"])
                x_min = 0 if cell2_xy[0] - window_x < 0 else cell2_xy[0] - window_x
                x_max = self.configs["cols"]-1 if cell2_xy[0] + window_x >= self.configs["cols"] else cell2_xy[0] + window_x
                y_min = 0 if cell2_xy[1] - window_y < 0 else cell2_xy[1] - window_y
                y_max = self.configs["rows"]-1 if cell2_xy[1] + window_y >= self.configs["rows"] else cell2_xy[1] + window_y
                
                # Randomly pick a location in the new window
                cell3_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                
                # Make sure the swap isn't with itself
                while cell3_xy == cell2_xy:
                    cell3_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                    
                cell3 = self.placement[cell3_xy]
                
                # Add to list of additional cells involved in the swap
                additional_cells.append({"cell": cell3, "cell_xy": cell3_xy})
                    
                # Keep finding next cell until an empty spot is chosen
                while not np.isnan(cell3):
                    celln_xy = additional_cells[-1]["cell_xy"]
                    
                    x_min = 0 if celln_xy[0] - window_x < 0 else celln_xy[0] - window_x
                    x_max = self.configs["cols"]-1 if celln_xy[0] + window_x >= self.configs["cols"] else celln_xy[0] + window_x
                    y_min = 0 if celln_xy[1] - window_y < 0 else celln_xy[1] - window_y
                    y_max = self.configs["rows"]-1 if celln_xy[1] + window_y >= self.configs["rows"] else celln_xy[1] + window_y
                    
                    cell3_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                    
                    # Make sure the swap isn't with itself and cell has not already been swapped
                    counter = 0
                    while cell3_xy == celln_xy or check_add_cells(cell3, additional_cells):
                        cell3_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                        cell3 = self.placement[cell3_xy]
                        counter += 1
                        
                        # If it has taken more than 10 iterations, there probably isn't a possible cell
                        if counter > 10:
                            # Use cell1 location as backup
                            cell3 = cell1
                            cell3_xy = cell1_xy
                            break
                        
                    # Add to list of additional cells
                    additional_cells.append({"cell": cell3, "cell_xy": cell3_xy})
                    
                    # Prevent infinite loop
                    if counter > 10:
                        break
                    
                debug_print(additional_cells)
                
                
            # If using "shuffle" configuration (only valid if cell2 is not an empty cell)
            elif shuffle and not np.isnan(cell2):
                
                # Check 4 closest placements
                possible_placements = [
                    (cell2_xy[0] + 1, cell2_xy[1]),
                    (cell2_xy[0] - 1, cell2_xy[1]),
                    (cell2_xy[0], cell2_xy[1] + 1),
                    (cell2_xy[0], cell2_xy[1] - 1),
                ]
                
                # Choose one of the placements
                cell3_xy = random.choice(possible_placements)
                while True:
                    try:
                        cell3 = self.placement[cell3_xy]
                        
                        # Check if cell is empty
                        if np.isnan(cell3):
                            break
                        else:
                            possible_placements.remove(cell3_xy)
                            
                    except IndexError:
                        # Location is out of range
                        possible_placements.remove(cell3_xy)
                        
                    # If no more options, resort to swapping back with cell1
                    if len(possible_placements) == 0:
                        cell3_xy = cell1_xy
                        break
                    cell3_xy = random.choice(possible_placements)
                
                additional_cells = [{"cell": cell3, "cell_xy": cell3_xy}]
                    
                
            debug_print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell1, c2=cell2, x1=cell1_xy[0], y1=cell1_xy[1], x2=cell2_xy[0], y2=cell2_xy[1]))
            
            
            # Update placement
            if shuffle and not np.isnan(cell2):
                debug_print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell2, c2=cell3, x1=cell2_xy[0], y1=cell2_xy[1], x2=additional_cells[0]["cell_xy"][0], y2=additional_cells[0]["cell_xy"][1]))
                temp_placement[cell2] = cell3_xy
                temp_placement[cell1] = cell2_xy
            
                # Check updated cost
                self.delta_cost = self.calculate_delta_cost(cell1, cell2, temp_placement, additional_cells)
                
            # Update placement
            elif ripple and not np.isnan(cell2):
                temp_placement[cell1] = cell2_xy
                
                temp_placement[cell2] = additional_cells[0]["cell_xy"]
                cell3 = additional_cells[0]["cell"]
                debug_print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell2, c2=cell3, x1=cell2_xy[0], y1=cell2_xy[1], x2=additional_cells[0]["cell_xy"][0], y2=additional_cells[0]["cell_xy"][1]))
                
                for additional_cell in additional_cells[1:]:
                    debug_print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell3, c2=additional_cell["cell"], x1=temp_placement[cell3][0], y1=temp_placement[cell3][1], x2=additional_cell["cell_xy"][0], y2=additional_cell["cell_xy"][1]))
                    temp_placement[cell3] = additional_cell["cell_xy"]
                    cell3 = additional_cell["cell"]
                
                # Check updated cost
                self.delta_cost = self.calculate_delta_cost(cell1, cell2, temp_placement, additional_cells)
                
            # Update placement
            else:
                additional_cells = None
                if not np.isnan(cell2):
                    temp_placement[cell2] = cell1_xy
                if not np.isnan(cell1):
                    temp_placement[cell1] = cell2_xy
                    
                # Check updated cost
                self.delta_cost = self.calculate_delta_cost(cell1, cell2, temp_placement)
            
            
            # If cost has decreased, swap is automatically accepted
            if self.delta_cost < 0:
                self.update_swap(cell1, cell2, cell1_xy, cell2_xy, additional_cells)
                accepted_swap += 1
                
            # Otherwise accept with probability
            elif self.temperature != 0:
                # Check if swap should happen
                r = random.uniform(0, 1)
                update_threshold = math.exp(-1 * self.delta_cost / self.temperature)
                debug_print("Update Threshold: {u} (r = {r})".format(u=update_threshold, r=r))
                
                if (r < update_threshold):
                    # Update
                    self.update_swap(cell1, cell2, cell1_xy, cell2_xy, additional_cells)
                    accepted_swap += 1
                else:
                    debug_print("Swap rejected")
                    
            # If temperature is 0, the swap must decrease cost to be accepted
            else:
                debug_print("Swap rejected")
                
            del temp_placement
            
            # Add to graph
            self.x.append(self.iteration)
            self.y.append(self.current_cost)
            
            
        debug_print("{}% accepted swaps".format(float(accepted_swap) / self.n_moves))
        
        # Update temperature
        self.temperature = self.temperature * temperature_rate
        if self.temperature < 0.1:
            self.temperature = 0
        debug_print("New temperature: {}".format(round(self.temperature, 2)))
        
        # Update temperature label on GUI
        self.c.delete("temp")
        self.c.create_text(
            grid["right"] - 100,
            20,
            text="Temp: {}".format(round(self.temperature, 2)),
            fill="black",
            font=('Arial',20,'bold'),
            tag="temp"
        )
            
            
    def full_anneal(self):
        '''
        Run full simulated annealing
        '''
        
        # Start with a random placement
        self.random_placement()
        
        # While the exit criteria has not been met, keep iterating
        while self.no_exit():
            self.anneal()
            
        # Update the graph when annealing is complete
        self.animate()
        
        # Check the final cost
        self.calculate_cost()
        print("Done! Cost = {}".format(self.current_cost))
        
        # Update final GUI
        self.draw_connections()
        self.update_labels()
        self.c.update()
        
        return self.current_cost