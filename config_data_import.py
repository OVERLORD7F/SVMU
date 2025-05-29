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
        config_menu_options="[gold bold][1] [grey53 italic]Show current configuration\n[/] \
\n[gold bold][2] [grey53 italic]Setup new config file[/]\n \
\n[gold bold][3] [grey53 italic]Change selected data pool[/]\n\
\n[gold bold][4] [grey53 italic]Change selected VMs[/]\
\n\n[green_yellow bold]ENTER - return to Main Menu[/]"
        config_menu_options=Align.center(config_menu_options, vertical="middle")
        console = Console()
        console.print(Panel(config_menu_options, title="[gold bold]SpaceVM Utility - Utility Configuration" , border_style="magenta" , width=150 , padding = 2))
        sub_choice=str(input("\n>>> "))
        if sub_choice == "1":
            config_show(config_relative_path)
            config_menu(base_url, api_key, config_relative_path)
        if sub_choice == "2":
            config_edit(config_relative_path)
        if sub_choice == "3":
            change_data_pool(base_url, api_key, config_relative_path)
        if sub_choice == "4":
            change_vm_uuids(config_relative_path)

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

    base_url = config.get('General', 'controller_ip')
    api_key = "jwt " + config.get('General', 'api_key') #That was realy obvious DACOM >:C
    data_pool_uuid = config.get('Data_Pool', 'data_pool_uuid')

    vm_list = []
    if 'VM_List' in config:
        for key, value in config['VM_List'].items():
            vm_list.append(value)
    
    #importing disk sizes for SpaceVM courses        
    disk1_size = config.get('Courses-Space-VM', 'disk1')
    disk2_size = config.get('Courses-Space-VM', 'disk2') 
    disk3_size = config.get('Courses-Space-VM', 'disk3')

    #get pretty name for selected data pool
    data_pool_name = get_data_pool_name(base_url , api_key , data_pool_uuid)
    #get pretty name for selected VMs
    vm_names=[]
    for x in vm_list:
        vm_names.append(get_vm_name(base_url, api_key, x))
    return base_url, api_key, data_pool_uuid, data_pool_name, vm_list, vm_names, disk1_size, disk2_size, disk3_size

def change_data_pool(base_url, api_key, config_relative_path):
    cls()
    show_data_pools(base_url, api_key)
    new_data_pool_uuid = input("Type NEW Data Pool UUID: ")
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('Data_Pool'):
        # update data_pool_uuid
        config.set('Data_Pool', 'data_pool_uuid', new_data_pool_uuid)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
    else:
        print("No 'Data_Pool' section in config file..")
    config_show(config_relative_path)


def change_vm_uuids(config_relative_path):
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    # Remove old VM_List section if it exists, then add a fresh one
    if config.has_section('VM_List'):
        config.remove_section('VM_List')
    config.add_section('VM_List')
    cls()
    console.print("[yellow bold]Type new VM UUIDs one by one (input ENTER to stop):")
    x = 0
    while True:
        vm_input = input(">> ")
        if not vm_input:
            break
        x += 1
        config.set('VM_List', f'uuid_{x}', vm_input)

    with open(config_relative_path, 'w') as configfile:
        config.write(configfile)

    console.print("[green bold]VM UUIDs have been updated in config :pencil:")
    Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    config_show(config_relative_path)


def config_edit(config_relative_path):
    read_input = input("Create new config file? (Y / N): ")
    menu_choice = str(read_input)
    if menu_choice == "Y" or menu_choice == "y":
        base_url = input("Type SpaceVM Controller IP: ")
        while check_ping(base_url) != True:
            base_url = console.input("[bold red]No response.\nCheck and type SpaceVM Controller IP again: [/]")

        api_key = input("Type your API Key: ")
        while check_api_key(base_url, "jwt " + api_key) != 200:
            api_key = console.input("[bold red]Check and type SpaceVM Controller API Key again: [/]")
        show_data_pools(base_url, "jwt " + api_key)
        data_pool_uuid = input("Type Data Pool UUID you wish to use: ")

        config = configparser.ConfigParser()
        config["General"] = {
            "controller_ip": base_url,
            "api_key": api_key,
        }
        config["Data_Pool"] = {"data_pool_uuid": data_pool_uuid}

        with open(config_relative_path, "w") as configfile:
            config.write(configfile)

        print("Type VM UUIDs one by one (input ENTER to stop)")
        with open(config_relative_path, "a") as file:
            file.write("[VM_List]\n") #manually writing section for VMs
            vm_input = []
            x = 0
            while vm_input != "":
                vm_input = input(">> ")
                if vm_input:
                    x += 1
                    file.write(f"uuid_{x} = {vm_input}\n")

        console.print("[green bold]VM UUIDs have been written in config :pencil:")
        console.print("[green bold]Configuration completed ! :white_check_mark:")
        Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
        cls()

def check_config(config_relative_path):
    if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: #check if config exists and not empty   
        pass #do nothing
    else:
        console.print("[yellow bold italic]Config file was not found or empty.. ")
        config_edit(config_relative_path)

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