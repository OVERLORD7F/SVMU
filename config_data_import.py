
def import_vm_uuid(config_relative_path):
    vm_uuids = []
    with open(config_relative_path, "r") as f:
        for i in range(3): # ignoring 2 first lines (IP, API-KEY)
            next(f)
        for line in f:                
            line = line.strip('\n')
            if line: # checks if line is empty (EOF). ESSENTIAL, DO NOT REMOVE
                vm_uuids.append(line)
    return vm_uuids

def import_threelines(config_relative_path):
    threelines = []
    with open(config_relative_path, "r") as f:
        all_lines = f.readlines()  
        threelines[0] = all_lines[0].strip('\n')
        threelines[1] = "jwt " + all_lines[1].strip('\n') #actual format for api_key. That was realy obvious DACOM >:C
        threelines[2] = all_lines[2].strip('\n')
    return threelines
