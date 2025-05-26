import os
import subprocess
import configparser
from cluster_api import *
from data_pools_api import *
from rich import print
from rich.panel import Panel
from rich.console import Console , Align
from rich.prompt import Prompt
console = Console()

def config_menu(config_relative_path):
        cls()
        config_menu_options="[gold bold][1] [grey53 italic]Show current configuration\n[/grey53 italic] \
\n[gold bold][2] [grey53 italic]Change configuraion[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - return to Main Menu"
        config_menu_options=Align.center(config_menu_options, vertical="middle")
        console = Console()
        console.print(Panel(config_menu_options, title="[gold bold]SpaceVM Utility - Utility Configuration" , border_style="magenta" , width=150 , padding = 2))
        sub_choice=str(input("\n>>> "))
        if sub_choice == "1":
            config_show(config_relative_path)
            config_menu(config_relative_path)
        if sub_choice == "2":
            config_edit(config_relative_path)

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
    api_key = config.get('General', 'api_key')
    data_pool_uuid = config.get('Data_Pool', 'data_pool_uuid')

    vm_list = []
    if 'VM_List' in config:
        for key, value in config['VM_List'].items():
            vm_list.append(value)

    config_values = {
        'base_url': base_url,
        'api_key': "jwt " + api_key,
        'data_pool_uuid': data_pool_uuid,
        'vm_list': vm_list
    }

    return config_values

def config_edit(config_relative_path):
    read_input = input("Create new config file? (Y / N): ")
    menu_choice = str(read_input)
    if menu_choice == "Y" or menu_choice == "y":
        base_url = input("Type SpaceVM Controller IP: ")
        api_key = input("Type your API Key: ")
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
                    file.write(f"UUID_{x} = {vm_input}\n")

        console.print("[green bold]VM UUIDs have been written in config :pencil:")
        console.print("[green bold]Configuration completed ! :white_check_mark:")
        Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
        cls()

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def ping(base_url):
    DNULL = open(os.devnull, 'w')
    if os.name == 'nt':
        status = subprocess.call(["ping","-n","1",base_url],stdout = DNULL)
    else:
        status = subprocess.call(["ping","-c","1",base_url],stdout = DNULL)
        
    if status == 0:
        return True
    else:
        return False