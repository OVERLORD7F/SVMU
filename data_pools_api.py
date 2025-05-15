
#from main import base_url , api_key , requests
import requests

def data_pools(base_url , api_key): #output data pool info 
    url= f"http://{base_url}//api/data-pools/"
    response = requests.get(url , headers={'Authorization' : api_key})
   
    if response.status_code == 200:
        data_pools = response.json()
        results_data_pools_info = data_pools['results']

        print("\nData pools overview:")
        print(f"\nData pools total: {data_pools['count']}")
        print("-" * 44)         
        for x in results_data_pools_info:
            print(f"\nData pool: {x['verbose_name']} ({x['status']})")
            print(f"type: {x['type']} | Used: {round((x['free_space']/1024), 1)} Gb/{round((x['size'] / 1024), 1)} Gb")
            print(f"UID: {x['id']}")
            print("-" * 44)
            #
        
    else:
        print(f"Failed to retrieve data {response.status_code}")  