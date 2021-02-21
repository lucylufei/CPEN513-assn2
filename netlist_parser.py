from settings import *
from util import *

def parse_file(filename):
    
    f = open(filename, "r")
    
    line = f.readline()
    
    configs = {}
    
    configs["cells"] = int(line.strip().split(" ")[0])
    configs["nets"] = int(line.strip().split(" ")[1])
    configs["rows"] = int(line.strip().split(" ")[2])
    configs["cols"] = int(line.strip().split(" ")[3])
    
    debug_print("{c} cells to be places in {r} x {col} (= {t}) grid with {n} nets.".format(c=configs["cells"], r=configs["rows"], col=configs["cols"], t=configs["rows"]*configs["cols"] ,n=configs["nets"]))
    
    nets = []
    
    n = 0
    while True:
        cells = []
        line = f.readline().strip().split(" ")
        if len(line) <= 1:
            continue
        else:
            n += 1
            
        for cell in line[1:]:
            cells.append(int(cell))
            
        nets.append(cells)
        if n >= configs["nets"]:
            break
        
    debug_print("Nets:")
    debug_print(nets)
        
    return configs, nets
    
        