# Manticore Technologies LLC
# (c) 2024 
# Manticore Asset Explorer
#       routes.py 

from startup import app
from rpc import send_command
from utils import create_logger, config, load_map
from flask import jsonify, request, send_file, abort
import re
import math
import random

def paginate_list(data_list, limit, page):
    """Helper function to paginate a list based on page number."""
    start = (page - 1) * limit
    end = start + limit
    return data_list[start:end]

@app.route('/search')
def search():
    # Extract query parameters
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 10))  # Default limit is 10
    page = int(request.args.get('page', 1))  # Default page is 1
    reissuable = request.args.get('reissuable', None)  # Get reissuable filter
    sort_by = request.args.get('sort', 'units')

    if reissuable == "false":
        reissuable = "0"
    elif reissuable == "true":
        reissuable = "1"

    # Load the map by name and units
    by_name = load_map("by_name") if reissuable is None else load_map("by_reissuable")[reissuable]
    by_units = load_map("by_units") 
    if sort_by == "height":
        by_units = load_map("by_height")
    elif sort_by == "amount":
        by_units = load_map("by_amount")

    # Handle special queries
    if query.startswith('%'):
        if query == '%random':
            # Generate a random list of assets
            all_assets = list(by_name.keys())
            random.shuffle(all_assets)
            ordered_assets = all_assets
        elif query == '%all':
            # Return all assets ordered as per the sort criteria
            ordered_assets = list(by_name.keys())
        else:
            # If the special query is not recognized, return an error
            abort(400, description="Invalid special query")
    else:
        # Normal query handling
        if sort_by != "name":
            # Flatten the by_units map into a list while preserving order
            ordered_assets = []
            for unit, assets in by_units.items():
                ordered_assets.extend(assets)
        elif sort_by == "name":
            ordered_assets = list(by_name.keys())

        # Filter the list by the name using the query while maintaining order
        regex = re.compile(query, re.IGNORECASE)
        ordered_assets = [asset for asset in ordered_assets if regex.search(asset)]

    # Total assets after filtering
    total_assets = len(ordered_assets)

    # Calculate total pages
    total_pages = math.ceil(total_assets / limit)

    # Apply pagination to the filtered list
    paginated_assets = paginate_list(ordered_assets, limit, page)

    # Create a dictionary for the paginated assets using by_name data
    response_assets = [by_name[asset_name] for asset_name in paginated_assets if asset_name in by_name]
    
    # Return the paginated data along with metadata
    response = {
        'total_assets': total_assets,
        'total_pages': total_pages,
        'current_page': page,
        'results': response_assets
    }

    return jsonify(response)
