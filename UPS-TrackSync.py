from dbfread import DBF
import requests
import base64
from xml.etree import ElementTree
from datetime import datetime
import os

# Configuration
api_url = 'https://yoursite.com/shop/api'
api_key = 'looks something like this LLX4BDIUI52BZG7KG7RCCJKF3JBIMQ2A'  # Replace with your actual API key

# Encode API key in base64 format
auth = base64.b64encode(f'{api_key}:'.encode()).decode('utf-8')

# Set up headers with proper authorization
headers = {
    'Authorization': f'Basic {auth}',
    'Accept': 'application/xml',
    'Content-Type': 'application/xml'
}

# Function to get the order data from PrestaShop
def get_order(order_id):
    response = requests.get(f'{api_url}/orders/{order_id}', headers=headers)
    if response.status_code == 200:
        print(f"Order data for {order_id} fetched successfully.")
        return response.content
    else:
        print(f"Failed to get order data: {response.status_code}")
        return None

# Function to update the tracking number in PrestaShop
def update_tracking_number(order_id, tracking_number):
    order_data = get_order(order_id)
    
    if not order_data:
        return
    
    # Parse the XML data
    root = ElementTree.fromstring(order_data)
    
    # Find the shipping_number field
    shipping_number_element = root.find('.//shipping_number')
    
    if shipping_number_element is not None:
        # Update the tracking number
        shipping_number_element.text = tracking_number
        print(f"Updating order {order_id} with tracking number: {tracking_number}")
    else:
        print(f"Shipping number element not found for order {order_id}.")
        return
    
    # Convert updated XML back to string
    updated_order_data = ElementTree.tostring(root, encoding='utf-8')
    
    # Send the updated data back to PrestaShop using a PUT request
    response = requests.put(f'{api_url}/orders/{order_id}', headers=headers, data=updated_order_data)
    
    if response.status_code == 200:
        print(f"Tracking number for order {order_id} updated successfully.")
    else:
        print(f"Failed to update tracking number for order {order_id}: {response.status_code}")
        print(response.text)

# Get the current year and month
current_date = datetime.now()
year = current_date.strftime('%y')  # Two-digit year (e.g., '24' for 2024)
month = current_date.strftime('%b')  # Abbreviated month (e.g., 'Oct' for October)

# Directory for the current month, e.g., "Oct24" for October 2024
directory_name = f'{month}{year}'

# File name for the current day, e.g., "s241016.dbf" for October 16, 2024
file_name = f's{year}{current_date.strftime("%m%d")}.dbf'

# Full path to the DBF file
dbf_file_path = os.path.join(directory_name, file_name)

# Check if the DBF file exists before proceeding
if not os.path.exists(dbf_file_path):
    print(f"DBF file not found: {dbf_file_path}")
else:
    # Open the DBF file and extract order number and tracking number
    dbf = DBF(dbf_file_path)

    # Loop through records in the DBF file
    for record in dbf:
        order_number = record['REFERENCE0']
        tracking_number = record['TRACK_NO']
        
        print(f"Extracted Order Number: {order_number}, Tracking Number: {tracking_number}")
        
        # Call the function to update the tracking number in PrestaShop
        update_tracking_number(order_number, tracking_number)
