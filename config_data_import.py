import os
import subprocess
import configparser
from cluster_api import *
from domain_api import *
from data_pools_api import *
from rich import print
from rich.panel import Panel
from rich.console import Console , Align
from rich.prompt import Prompt
console = Console()
def config_menu(base_url, api_key, config_relative_path):
    cls()
    menu = (
        "[gold1 bold][1][/] [grey53 italic]Show current profile configuration[/grey53 italic]\n\n"
        "[gold1 bold][2][/] [grey53 italic]Setup new profile[/]\n\n"
        "[gold1 bold][3][/] [grey53 italic]Switch profile[/]\n\n"
        "[gold1 bold][4][/] [grey53 italic]Delete profile[/]\n\n"
        "[gold1 bold][5][/] [grey53 italic]Set default profile[/]\n\n"
        "[gold1 bold][6][/] [grey53 italic]Change selected data pool[/]\n\n"
        "[gold1 bold][7][/] [grey53 italic]Change selected VMs[/]\n\n"
        "[gold1 bold][8][/] [grey53 italic]Change ISO UUID (auto-mount)[/]\n\n"
        "[gold1 bold][9][/] [grey53 italic]Skip start-up splash[/]\n\n"
        "[green_yellow bold]ENTER - return to Main Menu"
    )
    console.print(Panel(Align.center(menu, vertical="middle"), title="[gold bold]SpaceVM Utility - Utility Configuration", border_style="magenta", width=150, padding=2))
    choice = console.input("[bold yellow]\n>>> [/]")
    new_profile = None #used for controlling profile switch / updating current profile
    needs_reload = False

    if choice == "1":
        config_show(config_relative_path)
        return new_profile, needs_reload
    if choice == "2":
        result = create_new_profile() # create_new_profile may return a profile path (to switch to)
        if result:
            new_profile = result
        return new_profile, needs_reload
    if choice == "3":
        result = switch_profile() # switch_profile returns the selected profile path
        if result:
            new_profile = result
        return new_profile, needs_reload
    if choice == "4":
        delete_profile(config_relative_path)
        return new_profile, needs_reload
    if choice == "5":
        set_default_profile()
        return new_profile, needs_reload
    if choice == "6":
        change_data_pool(base_url, api_key, config_relative_path)
        needs_reload = True
        return new_profile, needs_reload
    if choice == "7":
        change_vm_uuids(config_relative_path, base_url, api_key)
        needs_reload = True
        return new_profile, needs_reload
    if choice == "8":
        change_iso_uuid(config_relative_path)
        needs_reload = True
        return new_profile, needs_reload
    if choice == "9":
        change_startup_option(config_relative_path)
        needs_reload = True
        return new_profile, needs_reload

    return new_profile, needs_reload

def config_show(config_relative_path):
    cls()
    console.rule(title = "Current configuration" , align="center" , style="yellow")
    with open(config_relative_path, "r") as f:
        print(f.read())
    console.rule(style="yellow")
    Prompt.ask("[green_yellow bold]ENTER - return to Utility Configuration.. :right_arrow_curving_down:")

def config_import(config_relative_path):
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    skip_startup_splash = config.get('General', 'skip_startup_splash')
    base_url = config.get('General', 'controller_ip')
    api_key = "jwt " + config.get('General', 'api_key') #That was realy obvious DACOM >:C
    data_pool_uuid = config.get('Data_Pool', 'data_pool_uuid')

    vm_list = []
    if 'VM_List' in config:
        for key, value in config['VM_List'].items():
            vm_list.append(value)
    
    if config.has_section('VM_Options'): #importing VM_Options
        iso_uuid = config.get('VM_Options' , 'iso_uuid')
        disk_interface = config.get('VM_Options' , 'disk_interface')    
        preallocation = config.get('VM_Options' , 'preallocation')
        iso_name=get_iso_name(base_url, api_key, iso_uuid)
    else:
        console.print("[bold yellow]Applying default values to Virtual Machine Options")
        iso_uuid = "none"
        disk_interface = "virtio" 
        preallocation = "falloc"
        iso_name= "none"
        config = configparser.ConfigParser() #writing default values to config
        config["VM_Options"] = {"disk_interface": "virtio", "preallocation": "falloc", "iso_uuid": "none"}        
        with open(config_relative_path, "a") as configfile: # appending to existing config file
            config.write(configfile) 

    if config.has_section('Courses-Space-VM'): #importing disk sizes for SpaceVM courses
        disk1_size, disk2_size, disk3_size = config.get('Courses-Space-VM', 'disk1'), config.get('Courses-Space-VM', 'disk2'), config.get('Courses-Space-VM', 'disk3')
    else:
        console.print("[bold yellow]Applying default values to Disk sizes for Courses")
        disk1_size, disk2_size, disk3_size = 10, 20, 20 #applying default values for courses
        config = configparser.ConfigParser() #writing default values to config
        config["Courses-Space-VM"] = {"disk1": 10, "disk2": 20,"disk3": 20}
        with open(config_relative_path, "a") as configfile: # appending to existing config file
            config.write(configfile)        

    data_pool_name = get_data_pool_name(base_url , api_key , data_pool_uuid)  #get pretty name for selected data pool
    vm_names=[]     #get pretty name for selected VMs
    for x in vm_list:
        vm_names.append(get_vm_name(base_url, api_key, x))
    
    return skip_startup_splash, base_url, api_key, data_pool_uuid, data_pool_name, vm_list, vm_names, disk1_size, disk2_size, disk3_size, disk_interface, preallocation, iso_uuid, iso_name

def change_startup_option(config_relative_path):
    cls()
    new_value = Prompt.ask("[yellow bold]Skip start-up splash ?[/]", choices=["Y", "N"], default="N", case_sensitive=False)
    if new_value.lower() == "y":
        startup_option = "yes"
    else:
        startup_option = "no"
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    config.set('General', 'skip_startup_splash', startup_option)
    with open(config_relative_path, 'w') as config_file:
        config.write(config_file)
    console.print(f"[green bold]Option set to: {new_value}")

def change_data_pool(base_url, api_key, config_relative_path): #change selected data pool in config
    cls()
    show_data_pools(base_url, api_key)
    new_data_pool_uuid = console.input("[bold yellow]Type NEW Data Pool UUID: [/]")
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('Data_Pool'):
        config.set('Data_Pool', 'data_pool_uuid', new_data_pool_uuid)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
    else:
        print("No 'Data_Pool' section in config file..")
    config_show(config_relative_path)

def change_iso_uuid(config_relative_path):
    cls()
    new_iso_uuid = console.input("[bold yellow]Type ISO UUID: [/]")
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('VM_Options'):
        config.set('VM_Options', 'iso_uuid', new_iso_uuid)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
    else:
        print("No 'VM_Options' section in config file..")
    #config_show(config_relative_path)

def change_vm_uuids(config_relative_path, base_url, api_key): #change selected VM uuids in config
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('VM_List'): # Remove old VM_List section if it exists, then add a new one
        config.remove_section('VM_List')
    config.add_section('VM_List')
    cls()
    console.print("[yellow bold]Type new VM UUIDs one by one [red bold](ENTER to stop)[/] ")
    x = 0
    while True:
        vm_input = console.input("[bold yellow]>> [/]" )
        if not vm_input:
            break
        vm_name = get_vm_name(base_url, "jwt " + api_key, vm_input) # validate entered VM UUID via get_vm_name
        if not vm_name:
            console.print("[red bold]Invalid VM UUID (not found)")
            continue
        x += 1
        config.set('VM_List', f'uuid_{x}', vm_input)

    with open(config_relative_path, 'w') as configfile:
        config.write(configfile)
        console.print("[green bold]VM UUIDs have been updated in config :pencil:")
    Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    config_show(config_relative_path)

def check_config(config_relative_path): # Check if config exists and is valid
    if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) == 0: # Only check if the file is empty
        console.print("[red bold]Config file is empty!")

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def check_ping(base_url):
    DNULL = open(os.devnull, 'w')
    if os.name == 'nt':
        status = subprocess.call(["ping","-n","1",base_url],stdout = DNULL)
    else:
        status = subprocess.call(["ping","-c","1",base_url],stdout = DNULL)
        
    if status == 0:
        return True
    else:
        return False

def create_profiles_dir(): #creates ./profiles directory if it does not exist
    profiles_dir = os.path.join(os.getcwd(), 'profiles')
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)
    return profiles_dir

def get_available_profiles(): #Get list of available profile names
    profiles_dir = create_profiles_dir()
    profiles = []
    for filename in os.listdir(profiles_dir):
        if filename.endswith('.conf'):
            profiles.append(filename[:-5])  # Remove .conf extension
    return profiles

def create_new_profile(): # Create new profile. Returns profile_path
    cls()
    profiles_dir = create_profiles_dir()
    profile_name = Prompt.ask("[yellow bold]Enter new profile name")
    profile_path = os.path.join(profiles_dir, f"{profile_name}.conf")
    if os.path.exists(profile_path):
        console.print("[red bold]Profile already exists!")
        return
    
    base_url = console.input("[bold yellow]Type SpaceVM Controller IP: [/]")
    while check_ping(base_url) != True:
        base_url = console.input("[bold red]No response.\nCheck and type SpaceVM Controller IP again: [/]")

    api_key = console.input("[bold yellow]Type your API Key: [/]")
    while check_api_key(base_url, "jwt " + api_key) != 200:
        api_key = console.input("[bold red]Check and type SpaceVM Controller API Key again: [/]")
    
    show_data_pools(base_url, "jwt " + api_key)
    data_pool_uuid = console.input("[bold yellow]Type Data Pool UUID you wish to use: [/]")

    config = configparser.ConfigParser()
    config["General"] = {"controller_ip": base_url, "api_key": api_key, "skip_startup_splash": "no"}
    config["Data_Pool"] = {"data_pool_uuid": data_pool_uuid}

    with open(profile_path, "w") as configfile:
        config.write(configfile)

    console.print("[yellow bold]Type VM UUIDs one by one (input ENTER to stop):")
    with open(profile_path, "a") as file:
        file.write("[VM_List]\n")
        x = 0
        while True:
            vm_input = console.input("[bold yellow]>> [/]")
            if not vm_input:
                break
            vm_name = get_vm_name(base_url, "jwt " + api_key, vm_input) # validate entered VM UUID via get_vm_name
            if not vm_name:
                console.print("[red bold]Invalid VM UUID (not found)")
                continue
            x += 1
            file.write(f"uuid_{x} = {vm_input}\n")

    console.print("[green bold]Configuration completed! :white_check_mark:")
    switch_now = Prompt.ask("[yellow bold]Switch to new profile now?", choices=["Y", "N"] , default="Y", case_sensitive=False)
    if switch_now.lower() == "y" or switch_now.lower() == "Y":
        set_default = Prompt.ask("[yellow bold]Set new profile as default?", choices=["Y", "N"], default="N", case_sensitive=False)
        if set_default.lower() == "y" or set_default.lower() == "Y":
            profiles_dir = create_profiles_dir()
            profiles = get_available_profiles()
            for p in profiles:
                p_path = os.path.join(profiles_dir, f"{p}.conf")
                cfg = configparser.ConfigParser()
                cfg.read(p_path)
                if cfg.has_section('General'):
                    cfg.set('General', 'load_by_default', 'false')
                    with open(p_path, 'w') as f:
                        cfg.write(f)

            cfg = configparser.ConfigParser() # set new profile as default
            cfg.read(profile_path)
            if not cfg.has_section('General'):
                cfg.add_section('General')
            cfg.set('General', 'load_by_default', 'true')
            with open(profile_path, 'w') as f:
                cfg.write(f)
        return profile_path

def switch_profile(): # switch to different profile
    cls()
    profiles = get_available_profiles()
    if not profiles:
        console.print("[red bold]No profiles found!")
        return

    console.print("[yellow bold]Available profiles:")
    for i, profile in enumerate(profiles, 1):
        console.print(f"[grey53]{i}. {profile}")
    choice = Prompt.ask("[yellow bold]Select profile number: ", choices=[str(i) for i in range(1, len(profiles) + 1)])
    selected_profile = profiles[int(choice) - 1]

    selected_profile_path = os.path.join(create_profiles_dir(), f"{selected_profile}.conf") # Get the path for the selected profile
    if not os.path.exists(selected_profile_path):
        console.print(f"[red bold]Profile '{selected_profile}' does not exist!")
        return

    console.print(f"[green bold]Switched to profile: {selected_profile}") # Return the new profile path to update in main.py
    return selected_profile_path  # Return the new path instead of True

def delete_profile(current_profile_path): #Delete existing profile
    cls()
    profiles = get_available_profiles()
    if not profiles:
        console.print("[red bold]No profiles found!")
        return
        
    console.print("[yellow bold]Available profiles:")
    for i, profile in enumerate(profiles, 1):
        console.print(f"[grey53]{i}. {profile}")
        
    choice = Prompt.ask("[yellow bold]Select profile to delete", choices=[str(i) for i in range(1, len(profiles)+1)])
    selected_profile = profiles[int(choice)-1]
    selected_profile_path = os.path.join(create_profiles_dir(), f"{selected_profile}.conf")

    if os.path.normpath(selected_profile_path) == os.path.normpath(current_profile_path):
        console.print("[red bold]Cannot delete currently active profile!")
        Prompt.ask("[green_yellow bold]Press ENTER to return.. :right_arrow_curving_down:")
        return
    
    confirm = Prompt.ask(f"[red bold]Are you sure you want to delete {selected_profile}?", choices=["Y", "N"] , default="Y" , case_sensitive=False)
    if confirm.upper() == "Y":
        os.remove(os.path.join(os.getcwd(), 'profiles', f"{selected_profile}.conf"))
        console.print(f"[green bold]Profile {selected_profile} deleted!")

def set_default_profile(): # Set selected profile as default
    cls()
    profiles = get_available_profiles()
    if not profiles:
        console.print("[red bold]No profiles found!")
        return

    console.print("[yellow bold]Available profiles:")
    for i, profile in enumerate(profiles, 1):
        console.print(f"[grey53]{i}. {profile}")

    choice = Prompt.ask("[yellow bold]Select profile number to set as default", choices=[str(i) for i in range(1, len(profiles) + 1)])
    selected_profile = profiles[int(choice) - 1]
   
    profiles_dir = create_profiles_dir() #Fuck you there could be only ONE default ! (all other profiles deafult flags set to false)
    for profile in profiles:
        profile_path = os.path.join(profiles_dir, f"{profile}.conf")
        config = configparser.ConfigParser()
        config.read(profile_path)
        if config.has_section('General'):
            config.set('General', 'load_by_default', 'false')
            with open(profile_path, 'w') as f:
                config.write(f)
 
    selected_profile_path = os.path.join(profiles_dir, f"{selected_profile}.conf") # Set the selected profile as default
    config = configparser.ConfigParser()
    config.read(selected_profile_path)
    if not config.has_section('General'):
        config.add_section('General')
    config.set('General', 'load_by_default', 'true')
    with open(selected_profile_path, 'w') as f:
        config.write(f)

    console.print(f"[green bold]Profile '{selected_profile}' set as default!")

def get_default_config_path(): # Retrieve the path of the default profile. If none, promt user to select one
    profiles_dir = create_profiles_dir()
    profiles = get_available_profiles()

    for profile in profiles:
        profile_path = os.path.join(profiles_dir, f"{profile}.conf")
        config = configparser.ConfigParser()
        config.read(profile_path)
        if config.has_section('General') and config.has_option('General', 'load_by_default'):
            if config.getboolean('General', 'load_by_default'):
                return profile_path

    if profiles: # no default profile is found, prompt to select one
        console.print("[yellow bold]No default profile found. Please select a profile to load:")
        for i, profile in enumerate(profiles, 1):
            console.print(f"[grey53]{i}. {profile}")
        choice = Prompt.ask("[yellow bold]Select profile number", choices=[str(i) for i in range(1, len(profiles) + 1)])
        selected_profile = profiles[int(choice) - 1]
        return os.path.join(profiles_dir, f"{selected_profile}.conf")
    console.print("[red bold]No profiles available. Please create a new profile.")
    create_new_profile()

    profiles = get_available_profiles() # Refresh the profiles list and return new one
    if profiles:
        new_profile_path = os.path.join(profiles_dir, f"{profiles[-1]}.conf")
        console.print(f"[green bold]Loaded newly created profile: {profiles[-1]}")
        return new_profile_path

    raise RuntimeError("Failed to create or load a profile.")