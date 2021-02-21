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
    
    def __init__(self, canvas, ax):
        self.c = canvas
        self.ax = ax
        
    def setup(self, configs, nets):
        self.configs = configs
        self.nets = nets
        
        self.placement = np.zeros((configs["cols"], configs["rows"]))
        self.placement[:] = np.NaN
        random.seed()
        
        self.cells = {}
        self.cost = {}
        self.new_cost = {}
        self.current_cost = 0
        self.delta_cost = 0
        self.temperature = start_temperature
        
        if dynamic_n_moves:
            self.n_moves = round(k_n_moves * math.pow(configs["cells"], float(4)/3))
        else:
            self.n_moves = n_moves
        
        self.c.create_text(
            grid["right"] - 100,
            20,
            text="Temp: {}".format(round(self.temperature, 2)),
            fill="black",
            font=('Arial',20,'bold'),
            tag="temp"
        )
        
        self.iteration = 0
        self.exit_tracker = 0
        self.initalized = False
        
    
    def animate(self, frame=None):
        if self.initalized:
            self.ax.clear()
            self.ax.plot(self.x, self.y)
        
    def random_placement(self):
        # Reset all placement
        self.placement[:] = np.NaN
        
        # Make a list of possible coordinates
        possible_placements = [(x, y) for x in range(0, self.configs["cols"]) for y in range(0, self.configs["rows"])]
        
        for i in range(self.configs["cells"]):
            (x, y) = random.choice(possible_placements)
            possible_placements.remove((x, y))
            self.placement[x, y] = i
            self.cells[i] = (x, y)
            
        assert len(self.cells) == self.configs["cells"]
        
        debug_print("Current Placement:")
        debug_print(self.placement)
        
        self.draw_connections()
        self.update_labels()
        self.calculate_cost()
        
        self.initalized = True
        self.x = [0]
        self.y = [self.current_cost]
        self.ax.plot(self.x, self.y)
        self.ax.set_ylabel("Half Perimeter Cost")
        self.ax.set_xlabel("Iteration")

                
    def update_labels(self):
        self.c.delete("cell")
        for cell in self.cells:
            add_text(self.cells[cell][0], self.cells[cell][1], self.c, grid, cell, tag="cell")
        
        
    def draw_connections(self):
        self.c.delete("wires")
        for i, net in enumerate(self.nets):
            for cell in net[1:]:
                orig = self.cells[net[0]]
                dest = self.cells[cell]
                if line_curve:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires", extra_point=i)
                else:
                    draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires")
        
            
    def calculate_cost(self):
        
        for i, net in enumerate(self.nets):
            self.cost[i] = calculate_half_perimeter(net, self.cells)
            
        self.update_cost()
            
    def calculate_delta_cost(self, cell1, cell2, temp_placement):
        delta_cost = 0
        
        for i, net in enumerate(self.nets):
            if cell1 in net or cell2 in net:
                self.new_cost[i] = calculate_half_perimeter(net, temp_placement)
                delta_cost += self.new_cost[i] - self.cost[i]
            else:
                self.new_cost[i] = self.cost[i]
            
        debug_print("Delta Cost: {}".format(delta_cost))
        return delta_cost
        
    def update_cost(self):
        total_cost = sum(self.cost[i] for i in range(self.configs["nets"]))
        debug_print("Total Cost: {}".format(total_cost))
        self.current_cost = total_cost
        
    def no_exit(self):
        if exit_criteria == "temp":
            return self.temperature > exit_temperature
            
        elif exit_criteria == "no_improvement":
            return self.delta_cost < 0 or self.temperature != 0
            
        elif exit_criteria == "multiple_no_improvement":
            if self.delta_cost > 0 and self.temperature == 0:
                self.exit_tracker += 1
            else:
                self.exit_tracker = 0
            return self.exit_tracker < exit_iterations
            
            
        else:
            raise Exception
            
    def update_swap(self, cell1, cell2, cell1_xy, cell2_xy):
        self.placement[cell1_xy] = cell2
        self.placement[cell2_xy] = cell1
        if not np.isnan(cell2):
            self.cells[cell2] = cell1_xy
        if not np.isnan(cell1):
            self.cells[cell1] = cell2_xy
        
        self.cost = copy.deepcopy(self.new_cost)
        debug_print("New Placement:")
        debug_print(self.placement)
        
        self.update_cost()
        self.c.update()
        
        if update_gui:
            self.draw_connections()
            self.update_labels()
            time.sleep(display_delay)
        
    def anneal(self):
        
        accepted_swap = 0
        for i in range(self.n_moves):
            self.iteration += 1
            temp_placement = copy.deepcopy(self.cells)
            
            # Choose random cells to swap
            cells = list(range(0, self.configs["cells"]))
            
            cell1 = random.choice(cells)
            cell1_xy = self.cells[cell1]
            cells.remove(cell1)
            
            # Add in possibility of empty cell
            cells.append(self.configs["cells"])
            
            # Choose another cell within the range
            if range_window:
                window_x = round(window_size*self.configs["cols"])
                window_y = round(window_size*self.configs["rows"])
                x_min = 0 if cell1_xy[0] - window_x < 0 else cell1_xy[0] - window_x
                x_max = self.configs["cols"]-1 if cell1_xy[0] + window_x >= self.configs["cols"] else cell1_xy[0] + window_x
                y_min = 0 if cell1_xy[1] - window_y < 0 else cell1_xy[1] - window_y
                y_max = self.configs["rows"]-1 if cell1_xy[1] + window_y >= self.configs["rows"] else cell1_xy[1] + window_y
                
                debug_print("Cell1: ({x}, {y}) -> range ({xmin}-{xmax}, {ymin}-{ymax})".format(x=cell1_xy[0], y=cell1_xy[1], xmin=x_min, xmax=x_max, ymin=y_min, ymax=y_max))
                
                cell2_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                
                # Make sure the swap isn't with itself
                while cell2_xy == cell1_xy:
                    cell2_xy = (random.randint(x_min, x_max), random.randint(y_min, y_max))
                
                cell2 = self.placement[cell2_xy]
            # Choose any cell
            else:
                cell2 = random.choice(cells)
                
            if not range_window:
                if cell2 == self.configs["cells"]:
                    cell2 = np.NaN
                    while True:
                        x = random.randint(0, self.configs["cols"]-1)
                        y = random.randint(0, self.configs["rows"]-1)
                        
                        # Check that the block is currently empty
                        if np.isnan(self.placement[x, y]):
                            cell2_xy = (x, y)
                            break
                else:
                    cell2_xy = self.cells[cell2]
                
            debug_print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell1, c2=cell2, x1=cell1_xy[0], y1=cell1_xy[1], x2=cell2_xy[0], y2=cell2_xy[1]))
            
            # Update placement
            if not np.isnan(cell2):
                temp_placement[cell2] = cell1_xy
            if not np.isnan(cell1):
                temp_placement[cell1] = cell2_xy
                
            # Check updated cost
            self.delta_cost = self.calculate_delta_cost(cell1, cell2, temp_placement)
            
            if self.delta_cost < 0:
                self.update_swap(cell1, cell2, cell1_xy, cell2_xy)
                accepted_swap += 1
                
            elif self.temperature != 0:
                # Check if swap should happen
                r = random.uniform(0, 1)
                update_threshold = math.exp(-1 * self.delta_cost / self.temperature)
                debug_print("Update Threshold: {u} (r = {r})".format(u=update_threshold, r=r))
                
                if (r < update_threshold):
                    # Update
                    self.update_swap(cell1, cell2, cell1_xy, cell2_xy)
                    accepted_swap += 1
                else:
                    debug_print("Swap rejected")
                    
            else:
                debug_print("Swap rejected")
                
            del temp_placement
            
            self.x.append(self.iteration)
            self.y.append(self.current_cost)
            
            
        debug_print("{}% accepted swaps".format(float(accepted_swap) / self.n_moves))
        self.temperature = self.temperature * temperature_rate
        if self.temperature < 0.1:
            self.temperature = 0
        debug_print("New temperature: {}".format(round(self.temperature, 2)))
        
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
        self.random_placement()
        while self.no_exit():
            self.anneal()
            
        self.animate()
        print("Done! Cost = {}".format(self.current_cost))
        self.draw_connections()
        self.update_labels()
        self.c.update()
        return self.current_cost