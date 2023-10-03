# E-commerce-Admin-API
The Inventory Management System is a  Apis based application that helps businesses manage their product inventory efficiently. It provides features for adding and updating products, tracking sales, analyzing revenue, and monitoring inventory levels. Users can filter and search for products, view sales data by date range, and receive low stock alerts. The system also maintains a history of inventory changes for auditing purposes.

#  Database Schema
we are using mysql relational database .workbench is used to as a relational dbms tool. To run apis in vs code we are using thunderclient.it can be easily used by installing its extension.
### Product and Inventory:

#### Relationship Type:
 One-to-One
Explanation: Each product in the "products" table has a one-to-one relationship with an inventory record in the "inventory" table. This relationship allows you to associate each product with its current inventory status. For example, if you have a product called "Widget A," the "inventory" table will contain a record for "Widget A" that tracks its current quantity in stock and the last time it was updated.
### Product and Sale:

#### Relationship Type: 
One-to-Many
Explanation: Each product in the "products" table can have multiple sales records associated with it in the "sales" table. This one-to-many relationship allows you to record all the sales transactions for a particular product. For example, if you sell "Widget A" multiple times, each sale will be recorded in the "sales" table, and they will all be associated with "Widget A."
### Product and InventoryChangeLog:

#### Relationship Type:
One-to-Many
Explanation: Each product in the "products" table can have multiple entries in the "inventory_change_logs" table. This one-to-many relationship is used to log changes in inventory for a specific product. Whenever the quantity of a product in stock changes, an entry is added to the "inventory_change_logs" table, indicating the change and when it occurred.

### Product and Category:

#### Relationship Type:
Many-to-One
Explanation: The "products" table is related to the "categories" table in a many-to-one relationship. This means that multiple products can belong to the same category, but each product can only belong to one category.

## 1. Sales Status:
- Endpoints to retrieve, filter, and analyze sales data.
```bash
http://localhost:8000/salesproducts/retrieve
http://localhost:8000/salesproducts/filter
```
- Endpoints to analyze revenue on a daily, weekly, monthly, and annual basis.
```bash
http://localhost:8000/revenue/daily?date=2022-05-16%2021:33:40
http://localhost:8000/revenue/weekly
http://localhost:8000/revenue/yearly?start_year=2020&end_year=2022
```
- Ability to compare revenue across different periods and categories.
```bash
 http://localhost:8000/inventory-status
```
- Provide sales data by date range, product, and category.
```bash

http://localhost:8000/salesdata?applyfilter here
set range in the body
body
{
    "min_price": 50.0,
    "max_price": 100.0
}
```
## 2. Inventory Management:
- Endpoints to view current inventory status, including low stock alerts.
```bash
 http://localhost:8000/inventory-status
```
- Functionality to update inventory levels, and track changes over time.
    
 ```bash
http://localhost:8000/inventory/update
body
{
    "product_id": 1,
    "quantity_change": 1
}
```


## Dependencies

below are the installation command needed to run in vscode inorder to run the code .

```bash
  pip install alembic
  pip install mysqlclient
  pip install sqlalchemy
  pip install mysqlclient
  pip3 install fastapi "uvicorn[standard]"
```

for making migrations in database 
```bash
alembic revision --autogenerate -m "initial migrations"
alembic upgrade head
```

for running app
```bash
 uvicorn main:app --reload
```






