
#from main import base_url , api_key , requests
import requests

def vm_info_short(base_url , api_key): #output data pool info 
    url= f"http://{base_url}//api/domains/"
    response = requests.get(url , headers={'Authorization' : api_key})
   
    if response.status_code == 200:
        vm_info_short = response.json()
        results_vm_info_short = vm_info_short['results']

        print("\nShort VM overview")
        print(f"\nVM total: {vm_info_short['count']}")
        print("-" * 41)         
        for x in results_vm_info_short:
            print(f"VM: {x['verbose_name']} ")
            print(f"UID: {x['id']}")
            print("-" * 41)
        
    else:
        print(f"Failed to retrieve data {response.status_code}")  