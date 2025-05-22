import requests
import os
from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

def data_pools(base_url, api_key):  # output data pool info
    url = f"http://{base_url}//api/data-pools/"
    response = requests.get(url, headers={'Authorization': api_key})
    console = Console()
    if response.status_code == 200:
        data_pools = response.json()
        results_data_pools_info = data_pools['results']
        #os.system('cls' if os.name == 'nt' else 'clear')
        console.rule("[bold cyan]Data Pools Overview")
        console.print(f"[bold]Data pools total:[/] {data_pools['count']}\n")
        panels = []
        for x in results_data_pools_info:
            panel_content = (
                f"[bold]Type:[/] {x['type']}\n"
                f"[bold]Used:[/] {round((x['free_space']/1024), 1)} Gb / {round((x['size'] / 1024), 1)} Gb\n"
                f"[bold]UUID:[/] [italic]{x['id']}"
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