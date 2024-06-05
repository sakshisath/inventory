import streamlit as st
import requests

# FastAPI base URL
BASE_URL = "http://localhost:8000"

def fetch_items():
    try:
        response = requests.get(f"{BASE_URL}/items/")
        response.raise_for_status()  # Raise an error for bad status
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching items: {e}")
        return []

def fetch_item(item_id):
    try:
        response = requests.get(f"{BASE_URL}/items/{item_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching item: {e}")
        return None

def search_items(name):
    try:
        response = requests.get(f"{BASE_URL}/search/", params={"name": name})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching items: {e}")
        return []

def create_item(item):
    try:
        response = requests.post(f"{BASE_URL}/items/", json=item)
        response.raise_for_status()
        st.success("Item created successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating item: {e}")
        return None

def update_item(item_id, item):
    try:
        response = requests.put(f"{BASE_URL}/items/{item_id}", json=item)
        response.raise_for_status()
        st.success("Item updated successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating item: {e}")
        return None

def delete_item(item_id):
    try:
        response = requests.delete(f"{BASE_URL}/items/{item_id}")
        response.raise_for_status()
        st.success("Item deleted successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting item: {e}")
        return None

# Function to add a custom theme
def set_custom_theme():
    st.markdown(
        """
        <style>
        .reportview-container {
            background: #FFF0F5;
            color: #4B0082;
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background: #FFB6C1;
        }
        .css-1d391kg p {
            color: #4B0082;
        }
        .stButton>button {
            background-color: #FF69B4;
            color: white;
            border-radius: 10px;
            transition: background-color 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: rgba(255, 165, 0, 0.5);
        }
        .stMarkdown h2 {
            color: #FF69B4;
            text-align: center;
            font-size: 3em;
        }
        .item-details {
            margin-bottom: 20px;
        }
        .item-box {
            border: 2px solid #FF69B4;
            border-radius: 10px;
            padding: 10px;
            background-color: rgba(255, 105, 180, 0.2);
            margin-bottom: 10px;
        }
        .stTable {
            background-color: rgba(255, 105, 180, 0.2);
        }
        .stTableRow {
            background-color: rgba(255, 165, 0, 0.5);
        }
        .stTable th, .stTable td {
            border: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to display header with action buttons
def display_header():
    st.markdown("## Inventory Management")
    st.markdown("---")
    cols = st.columns([1, 1, 1, 1, 1])
    if cols[0].button("Add Item", key="add_item"):
        st.session_state.page = "add"
    if cols[1].button("Update Item", key="update_item"):
        st.session_state.page = "update"
    if cols[2].button("Delete Item", key="delete_item"):
        st.session_state.page = "delete"
    if cols[3].button("Search Items", key="search_item"):
        st.session_state.page = "search"
    if cols[4].button("View List", key="view_list"):
        st.session_state.page = "view_list"
    st.markdown("---")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Set theme
set_custom_theme()

# Display header
display_header()

# Display content based on page
if st.session_state.page == "home":
    st.title("Welcome to the Inventory Management App!")
    st.write("Choose an action from the header above to get started.")
elif st.session_state.page == "add":
    st.subheader("Add Item")
    name = st.text_input("Name")
    description = st.text_input("Description")
    price = st.number_input("Price", min_value=0)
    quantity = st.number_input("Quantity", min_value=0)
  
    if st.button("Add Item"):
        item = {"name": name, "description": description, "price": price, "quantity": quantity}
        create_item(item)
elif st.session_state.page == "update":
    st.subheader("Update Item")
    item_id = st.number_input("Item ID", min_value=0)
    item = fetch_item(item_id)
    if item:
        name = st.text_input("Name", item['name'])
        description = st.text_input("Description", item['description'])
        price = st.number_input("Price", min_value=0, value=item['price'])
        quantity = st.number_input("Quantity", min_value=0, value=item['quantity'])

        if st.button("Update Item"):
            updated_item = {"name": name, "description": description, "price": price, "quantity": quantity}
            update_item(item_id, updated_item)
elif st.session_state.page == "delete":
    st.subheader("Delete Item")
    item_id = st.number_input("Item ID", min_value=0)
    if st.button("Delete Item"):
        delete_item(item_id)
elif st.session_state.page == "search":
    st.subheader("Search Items")
    name = st.text_input("Item Name")
    if st.button("Search"):
        items = search_items(name)
        if items:
            for item in items:
                st.markdown(f'<div class="item-box">ID: {item["id"]}, Name: {item["name"]}, Description: {item["description"]}, Price: {item["price"]}, Quantity: {item["quantity"]}</div>', unsafe_allow_html=True)
        else:
            st.write("No items found.")
elif st.session_state.page == "view_list":
    st.subheader("View the List of Items")
    items = fetch_items()
    if items:
        item_data = [{"ID": item["id"], "Name":item["name"], "Description": item["description"], "Price": item["price"], "Quantity": item["quantity"]} for item in items]
        st.table(item_data)
    else:
        st.write("No items found.")
