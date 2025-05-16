
#from main import base_url , api_key , requests
import requests
import os
from rich.prompt import Prompt

def cluster_info(base_url , api_key): #output short clusters overview 
    url= f"http://{base_url}/api/clusters"
    response = requests.get(url , headers={'Authorization' : api_key})
   
    if response.status_code == 200:
        cluster_info = response.json()
        results_cluster_info = cluster_info['results']

        print("\nShort clusters overview:")
        print(f"\nClusters total: {cluster_info['count']}")
        print("-" * 51)         
        for x in results_cluster_info:

            print(f"\nCluster Name: {x['verbose_name']}  ({x['status']})")
            print(f"Nodes: {x['nodes_count']}")
            print(f"Total CPU: {x['cpu_count']} Cores || CPU Usage: {round(x['cpu_used_percent_user'] , 2)}%")#output is rounded by 2
            print(f"Total RAM: {int(x['memory_count']/1024)}GB    || RAM Usage: {round(x['mem_used_percent_user'] , 2)}%") #RAM pretty output = mb-to-gb + set 'int' to remove .0
            
            print("-" * 51) 
        
    else:
        print(f"Failed to retrieve data {response.status_code}")  
    Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    os.system('cls' if os.name=='nt' else 'clear')