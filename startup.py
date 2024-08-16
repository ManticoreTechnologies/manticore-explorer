# Manticore Technologies LLC
# (c) 2024 
# Manticore Asset Explorer
#       startup.py 

# Import utilities
from utils import create_logger, welcome_message, config, initialize_directories, save_maps

# Create a logger

logger = create_logger()

# Import flask
from flask import Flask

# Create flask application
app = Flask("Manticore Asset Explorer")

# Print the welcome message
print(welcome_message)



if __name__=="__main__":
    print("Starting image downloader")
    
    from downloader import map_assets
    from utils import load_map, download_image
    import time
    from rpc import send_command
    import os
    # Initialize the necessary directories
    existing_data = initialize_directories()

    # Load the network assets by height
    by_name = load_map("by_name")#map_assets()
    by_ipfshash = load_map("by_ipfshash")
    # Initialize the maps if nothing was loaded
    if len(by_name) == 0 or len(by_ipfshash) == 0:
        maps = map_assets()
        # Get the network assets by height
        by_name = maps[0]
        by_ipfshash = maps[3]
    


    while True:
        print("Updating asset maps")
        
        # Reload the asset maps with latest data
        by_ipfshash = map_assets()[3]
        
        # Sleep for a minute
        time.sleep(60)



else:
    print("Lets start the flask app here since its gunicorn")
    import routes








