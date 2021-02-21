import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import copy
import math
from util import *
from settings import *

np.set_printoptions(threshold=np.inf, linewidth=np.inf)


class SimAnneal:
    
    def __init__(self, canvas, configs, nets, ax):
        self.c = canvas
        self.configs = configs
        self.nets = nets
        
        self.placement = np.zeros((configs["rows"], configs["cols"]))
        self.placement[:] = np.NaN
        random.seed()
        
        self.cells = {}
        self.cost = {}
        self.new_cost = {}
        self.temperature = start_temperature
        
        self.iteration = 0
        
        self.x = np.arange(0, 2*np.pi, 0.01) 
        self.line, = ax.plot(self.x, np.sin(self.x))
        
    def animate(self,i):
        self.line.set_ydata(np.sin(self.x*i))  # update the data
        return self.line,
        
    def random_placement(self):
        # Reset all placement
        self.placement[:] = np.NaN
        
        # Make a list of possible coordinates
        possible_placements = [(x, y) for x in range(0, self.configs["rows"]) for y in range(0, self.configs["cols"])]
        
        for i in range(self.configs["cells"]):
            (x, y) = random.choice(possible_placements)
            possible_placements.remove((x, y))
            self.placement[x, y] = i
            self.cells[i] = (x, y)
            
        assert len(self.cells) == self.configs["cells"]
        
        print("Current Placement:")
        print(self.placement)
        
        self.draw_connections()
        self.update_labels()
        self.calculate_cost()

                
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
                draw_line(orig, dest, self.c, grid, colour=wire_colour_palette[i % len(wire_colour_palette)], tag="wires", extra_point=i)
        
            
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
            
        print("Delta Cost: {}".format(delta_cost))
        return delta_cost
        
    def update_cost(self):
        total_cost = sum(self.cost[i] for i in range(self.configs["nets"]))
        print("Total Cost: {}".format(total_cost))
        
    def no_exit(self):
        if exit_criteria == "temp":
            return self.temperature > exit_temperature
            
    def update_swap(self, cell1, cell2, cell1_xy, cell2_xy):
        self.placement[cell1_xy] = cell2
        self.placement[cell2_xy] = cell1
        if not np.isnan(cell2):
            self.cells[cell2] = cell1_xy
        if not np.isnan(cell1):
            self.cells[cell1] = cell2_xy
        
        self.cost = copy.deepcopy(self.new_cost)
        print("New Placement:")
        print(self.placement)
        
        self.update_cost()
        self.draw_connections()
        self.update_labels()
        
    def anneal(self):
        
        for i in range(n_moves):
            self.iteration += 1
            temp_placement = copy.deepcopy(self.cells)
            
            # Choose random cells to swap
            cells = list(range(0, self.configs["cells"] + 1))
            cell1 = random.choice(cells)
            cells.remove(cell1)
            cell2 = random.choice(cells)
            
            # If swapping with empty cell
            if cell1 == self.configs["cells"]:
                cell1 = np.NaN
                while True:
                    x = random.randint(0, self.configs["rows"]-1)
                    y = random.randint(0, self.configs["cols"]-1)
                    
                    # Check that the block is currently empty
                    if np.isnan(self.placement[x, y]):
                        cell1_xy = (x, y)
                        break
                        
            # Get currrent location of cells
            else:
                cell1_xy = self.cells[cell1]
                
            if cell2 == self.configs["cells"]:
                cell2 = np.NaN
                while True:
                    x = random.randint(0, self.configs["rows"]-1)
                    y = random.randint(0, self.configs["cols"]-1)
                    
                    # Check that the block is currently empty
                    if np.isnan(self.placement[x, y]):
                        cell2_xy = (x, y)
                        break
            else:
                cell2_xy = self.cells[cell2]
            
            print("Swapping cell {c1} ({x1}, {y1}) with cell {c2} ({x2}, {y2})".format(c1=cell1, c2=cell2, x1=cell1_xy[0], y1=cell1_xy[1], x2=cell2_xy[0], y2=cell2_xy[1]))
            
            # Update placement
            if not np.isnan(cell2):
                temp_placement[cell2] = cell1_xy
            if not np.isnan(cell1):
                temp_placement[cell1] = cell2_xy
                
            # Check updated cost
            delta_cost = self.calculate_delta_cost(cell1, cell2, temp_placement)
            
            # Check if swap should happen
            r = random.uniform(0, 1)
            update_threshold = math.exp(-1 * delta_cost / self.temperature)
            print("Update Threshold: {u} (r = {r})".format(u=update_threshold, r=r))
            
            if (r < update_threshold):
                # Update
                self.update_swap(cell1, cell2, cell1_xy, cell2_xy)
            else:
                print("Swap rejected")
                
            del temp_placement
            
        self.temperature = self.temperature * temperature_rate
        print("New temperature: {}".format(self.temperature))
            
            
    def full_anneal(self):
        while self.no_exit():
            self.anneal()