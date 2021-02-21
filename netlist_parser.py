from settings import *

def parse_file(filename):
    
    f = open(filename, "r")
    
    line = f.readline()
    
    configs = {}
    
    configs["cells"] = int(line.strip().split(" ")[0])
    configs["nets"] = int(line.strip().split(" ")[1])
    configs["rows"] = int(line.strip().split(" ")[2])
    configs["cols"] = int(line.strip().split(" ")[2])
    
    print("{c} cells to be places in {r} x {col} (= {t}) grid with {n} nets.".format(c=configs["cells"], r=configs["rows"], col=configs["cols"], t=configs["rows"]*configs["cols"] ,n=configs["nets"]))
    
    nets = []
    
    for i in range(configs["nets"]):
        cells = []
        line = f.readline().strip().split(" ")
        
        for cell in line[1:]:
            cells.append(int(cell))
            
        nets.append(cells)
        
    if debug:
        print("Nets:")
        print(nets)
        
    return configs, nets
    
        