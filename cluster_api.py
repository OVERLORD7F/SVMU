#from main import base_url , api_key , requests
import requests
import os
from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

def cluster_info(base_url, api_key):  # output short clusters overview
    url = f"http://{base_url}/api/clusters"
    response = requests.get(url, headers={'Authorization': api_key})
    console = Console()
    if response.status_code == 200:
        cluster_info = response.json()
        results_cluster_info = cluster_info['results']
        os.system('cls' if os.name == 'nt' else 'clear')
        console.rule("[bold cyan]Short Clusters Overview")
        console.print(f"[bold]Clusters total:[/] {cluster_info['count']}\n")
        panels = []
        for x in results_cluster_info:
            panel_content = (
                f"[bold]Nodes:[/] {x['nodes_count']}\n"
                f"[bold]Total CPU:[/] {x['cpu_count']} Cores  /  [bold]CPU Usage:[/] {round(x['cpu_used_percent_user'], 2)}%\n"
                f"[bold]Total RAM:[/] {int(x['memory_count']/1024)} GB    /   [bold]RAM Usage:[/] {round(x['mem_used_percent_user'], 2)}%"
            )
            panel = Panel(
                Align.left(panel_content),
                title=f"[bold gold3]{x['verbose_name']}[/] [red]({x['status']})[/]",
                border_style="magenta",
                expand=False
            )
            panels.append(panel)
        console.print(*panels, sep="\n")
    else:
        console.print(f"[red]Failed to retrieve data {response.status_code}[/]")
    Prompt.ask("[green_yellow bold]ENTER - return to Main Menu.. :right_arrow_curving_down:")
    os.system('cls' if os.name == 'nt' else 'clear')