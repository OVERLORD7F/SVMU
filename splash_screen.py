import os
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def get_skip_startup_splash(config_path):
    """Read only skip_startup_splash from config file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("skip_startup_splash"):
                    # Example: skip_startup_splash = yes
                    return line.split("=")[-1].strip().lower()
    except Exception:
        pass
    return "no"  # Default if not found

def show_startup_logo(skip_startup_splash, SVMU_ver):
    if skip_startup_splash == "yes":
        return
    splash_dir = os.path.dirname(__file__) # Assume splash file lives in the assets/ directory
    splash_file = os.path.join(splash_dir, "assets", "splash-screens.txt")
    if not os.path.exists(splash_file):
        console.print(f"[bold red]No splash file fouond at: {splash_file}[/bold red]")
        return

    with open(splash_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split ASCII art blocks by lines of '=' (at least 160 in a row)
    blocks = [block.strip() for block in content.split("\n" + "="*160) if block.strip()]
    if not blocks:
        console.print("[bold red]No splash screens found![/bold red]")
        return

    art = random.choice(blocks)

    # Animated spinner while showing splash
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Loading SpaceVM Utility...[/bold cyan]"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("startup", total=None)
        # Simulate loading
        import time
        time.sleep(1.5)
        progress.remove_task(task)

    # Show the ASCII art in a pretty panel
    console.print(Panel.fit(art, subtitle=f"[bold magenta]{SVMU_ver}[/bold magenta]", subtitle_align="right", border_style="grey53" , width=200 , padding = 2))
    time.sleep(2) #pause for 2 sec
    os.system('cls' if os.name=='nt' else 'clear')  #clears screen before returning


# show_startup_logo()
