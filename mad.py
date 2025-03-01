from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='Restaurant Management System ER Diagram')

# Define entities
entities = {
    "Users": ["user_id (PK)", "username", "password", "name", "email", "role"],
    "Admin": ["admin_id (PK)", "user_id (FK)", "name", "email"],
    "Chef": ["chef_id (PK)", "user_id (FK)", "name", "email"],
    "Employee": ["employee_id (PK)", "user_id (FK)", "name", "email"],
    "Customer": ["customer_id (PK)", "user_id (FK)", "name", "email"],
    "Menu": ["menu_id (PK)", "name", "price", "description", "image_url"],
    "Inventory": ["inventory_id (PK)", "item_name", "quantity"],
    "Orders": ["order_id (PK)", "customer_id (FK)", "menu_id (FK)", "quantity", "status", "total_amount", "order_date"],
    "Table_Booking": ["booking_id (PK)", "customer_id (FK)", "customer_name", "number_of_people", "booking_date", "booking_time"],
    "Payments": ["payment_id (PK)", "customer_id (FK)", "order_id (FK)", "amount", "payment_method", "status"]
}

# Add entities to the graph
for entity, attributes in entities.items():
    dot.node(entity, label=f"{entity}\n" + "\n".join(attributes))

# Define relationships
relationships = [
    ("Users", "Admin", "1..1"),
    ("Users", "Chef", "1..1"),
    ("Users", "Employee", "1..1"),
    ("Users", "Customer", "1..1"),
    ("Admin", "Users", "1..1"),
    ("Chef", "Users", "1..1"),
    ("Employee", "Users", "1..1"),
    ("Customer", "Users", "1..1"),
    ("Menu", "Orders", "1..*"),
    ("Orders", "Customer", "1..1"),
    ("Orders", "Menu", "1..1"),
    ("Orders", "Payments", "1..1"),
    ("Payments", "Orders", "1..1"),
    ("Payments", "Customer", "1..1"),
    ("Inventory", "Menu", "0..*"),
    ("Table_Booking", "Customer", "1..1")
]

# Add relationships to the graph
for src, dest, cardinality in relationships:
    dot.edge(src, dest, label=cardinality)

# Save the diagram to a file
file_path = "/mnt/data/restaurant_management_system_er_diagram.png"
dot.render(file_path, format='png', cleanup=True)

file_path
