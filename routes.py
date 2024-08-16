# Manticore Technologies LLC
# (c) 2024 
# Manticore Asset Explorer
#       routes.py 

from startup import app
from rpc import send_command
from utils import create_logger, config, load_map
from flask import jsonify, request, send_file, abort
import time
import os
import re

def paginate_dict(data_dict, limit, offset):
    """Helper function to paginate a dictionary."""
    keys = list(data_dict.keys())
    paginated_keys = keys[offset:offset + limit]
    paginated_dict = {k: data_dict[k] for k in paginated_keys}
    return paginated_dict

@app.route('/filter/<mode>')
def filter(mode):
    # Load the map based on the mode
    by_mode = load_map(f"by_{mode}")
    
    # Get the pattern from query parameters
    pattern = request.args.get('pattern', '')

    # Compile the regex pattern
    regex = re.compile(pattern)

    # Filter assets based on the regex pattern matching the keys
    filtered_assets = {name: data for name, data in by_mode.items() if regex.search(name)}

    # Apply pagination
    limit = int(request.args.get('limit', 10))  # Default limit is 10
    offset = int(request.args.get('offset', 0))  # Default offset is 0
    paginated_filtered_assets = paginate_dict(filtered_assets, limit, offset)
    
    return jsonify(paginated_filtered_assets)


# Currently supports modes: amount, blockhash, height, ipfshash, name, reissuable, units
@app.route('/sort/<mode>')
def sort(mode):
    # Load the map based on the mode
    by_mode = load_map(f"by_{mode}")

    # Get query parameters for pagination and sorting order
    limit = int(request.args.get('limit', 10))  # Default limit is 10
    offset = int(request.args.get('offset', 0))  # Default offset is 0
    ascending = request.args.get('ascending', 'true').lower() == 'true'  # Default to ascending order

    # Determine the sorting key type
    if mode in ['name', 'ipfshash', 'blockhash']:
        sorted_keys = sorted(by_mode.keys(), reverse=not ascending)
    elif mode == 'amount':
        sorted_keys = sorted(by_mode.keys(), key=float, reverse=not ascending)
    else:
        sorted_keys = sorted(by_mode.keys(), key=int, reverse=not ascending)

    # Apply pagination to the sorted keys
    paginated_sorted_keys = sorted_keys[offset:offset + limit]

    # Create the paginated dictionary
    paginated_dict = {k: by_mode[k] for k in paginated_sorted_keys}

    return jsonify(paginated_dict)

from datetime import datetime

@app.route('/newest')
def newest():
    by_height = load_map("by_height")
    count = int(request.args.get('count', 10))

    # Sort the keys as integers in descending order
    sorted_keys = sorted(by_height.keys(), key=int, reverse=True)
    
    last_x_assets = []

    # Iterate through the sorted blocks and collect assets until we reach the count
    for key in sorted_keys:
        assets_in_block = by_height[key]
        for asset_name, asset_data in assets_in_block.items():
            # Get the block time using the blockhash
            blockhash = asset_data.get('blockhash')
            block_info = send_command('getblock', [blockhash])
            block_time = block_info.get('time')
            
            # Convert the block time to a human-readable date string
            block_date = datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S')

            # Append asset data along with block time and date
            asset_with_time = {
                'asset_name': asset_name,
                'data': asset_data,
                'block_time': block_time,
                'block_date': block_date
            }
            last_x_assets.append(asset_with_time)

            if len(last_x_assets) == count:
                break
        if len(last_x_assets) == count:
            break

    return jsonify(last_x_assets)


