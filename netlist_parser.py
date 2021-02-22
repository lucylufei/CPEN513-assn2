from settings import *
from util import *

def parse_file(filename):
    '''
    Parse input file
    Input: 
        filename - name of the circuit
    Output:
        configs - configurations for the circuit
        nets - list of nets and the cells for each
    '''
    
    # Initialize data structures
    configs = {}
    nets = []
    
    
    # Read file
    f = open(filename, "r")
    line = f.readline()
    
    # First line has the configurations
    configs["cells"] = int(line.strip().split(" ")[0])
    configs["nets"] = int(line.strip().split(" ")[1])
    configs["rows"] = int(line.strip().split(" ")[2])
    configs["cols"] = int(line.strip().split(" ")[3])
    
    debug_print("{c} cells to be places in {r} x {col} (= {t}) grid with {n} nets.".format(c=configs["cells"], r=configs["rows"], col=configs["cols"], t=configs["rows"]*configs["cols"] ,n=configs["nets"]))
    
    # Parse each net
    n = 0
    while True:
        cells = []
        line = f.readline().strip().split(" ")
        
        # Ignore blank lines
        if len(line) <= 1:
            continue
        else:
            n += 1
            
        # Add list of cells to net
        for cell in line[1:]:
            cells.append(int(cell))
        nets.append(cells)
        
        # Done if all nets have been read
        if n >= configs["nets"]:
            break
        
    debug_print("Nets:")
    debug_print(nets)
        
    return configs, nets
    
        