import os

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
        if sub_choice == "2":
            config_edit(config_relative_path)

def config_show(config_relative_path):
    cls()
    console.rule(title = "Current configuration" , align="center" , style="yellow")
    with open(config_relative_path, "r") as f:
        print(f.read())
    console.rule(style="yellow")
    Prompt.ask("[green_yellow bold]ENTER - return to Main Menu.. :right_arrow_curving_down:")

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
    threelines = [None] * 3
    with open(config_relative_path, "r") as f:
        all_lines = f.readlines()
        if len(all_lines) < 3:
             raise ValueError("Check config. Receiving less than 3 lines!")
        threelines[0] = all_lines[0].strip('\n')
        threelines[1] = "jwt " + all_lines[1].strip('\n') #actual format for api_key. That was realy obvious DACOM >:C
        threelines[2] = all_lines[2].strip('\n')
    return threelines

def config_edit(config_relative_path):
    read_input=input("Create new config file? (Y / N): ") 
    menu_choice=str(read_input)
    if menu_choice == "Y" or menu_choice == "y":
        base_url = input("Type SpaceVM Controller IP: ")
        api_key = input("Type your API Key: ")
        data_pool_uuid = input("Type Data Pool UUID you wish to use: ")
        lines = [base_url, api_key, data_pool_uuid]
        with open(config_relative_path, "w+") as file:
            for line in lines:
                file.write(line + '\n')
               
        print("Type VM UUIDs one by one (input ENTER to stop)")
        with open(config_relative_path, "a") as file: #appends new content at the end without modifying the existing data
            vm_input="test"
            while (vm_input != ""):
                vm_input = input(">> ")
                file.write(vm_input + '\n') 
            console.print("[green bold]VM UUIDs has been written in config :pencil:")
            console.print("[green bold]Configuration completed ! :white_check_mark:")
            Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
            cls()

def cls():
    os.system('cls' if os.name=='nt' else 'clear')