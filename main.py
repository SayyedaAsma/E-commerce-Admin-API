from fastapi import FastAPI,Depends,Query,HTTPException
from database import engine ,SessionLocal,Base
from sqlalchemy import func
from typing import List
from models import Product,Sale,Inventory,Category,InventoryChangeLog
from sqlalchemy.orm import Session
from pydantic import BaseModel


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Error creating tables:", str(e))

app=FastAPI()


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductSchema(BaseModel):
    name : str
    description :str
    price : float
    category_id :int
    class Config:
        orm_mode=True


class PriceRangeFilter(BaseModel):
    min_price: float
    max_price: float


class InventoryStatus(BaseModel):
    product_id: int
    product_name: str
    quantity_in_stock: int
    is_low_stock_alert: bool

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    


class InventoryUpdate(BaseModel):
    product_id: int
    quantity_change: int


@app.get("/products",response_model=list[ProductSchema])
def get_products(db:Session=Depends(get_db)):
    return db.query(Product).all()

#register products
@app.post("/products",response_model=ProductSchema)
def get_products(product:ProductSchema,db:Session=Depends(get_db)):
    u=Product(name=product.name,description=product.description,price=product.price,category_id=product.category_id)
    db.add(u)
    db.commit()
    return u


#end point to retrieve sales product
@app.get("/salesproducts/retrieve", response_model=list[ProductSchema])
def salesproducts(db: Session = Depends(get_db)):
    query = (
        db.query(Product)
        .join(Sale, Product.id == Sale.product_id)
        .all()
    )
    return query

#filtering sales data
@app.get("/salesproducts/filter", response_model=list[ProductSchema])
def filter_products_by_price_range(price_range: PriceRangeFilter, db: Session = Depends(get_db)):
    query = (
        db.query(Product)
        .join(Sale, Product.id == Sale.product_id)
        .filter(Product.price >= price_range.min_price, Product.price <= price_range.max_price)
        .all()
    )
    return query




# Endpoint to provide sales data by date range, product, and category
@app.get("/salesdata")
def get_sales_data(
    start_date: str = Query(None, description="Start date for date range filter (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date for date range filter (YYYY-MM-DD)"),
    product_id: int = Query(None, description="Product ID for product filter"),
    category_id: int = Query(None, description="Category ID for category filter"),
    db: Session = Depends(get_db),
):
    # Start with the base query
    query = db.query(Sale)

    # Apply filters as needed
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if product_id:
        query = query.filter(Sale.product_id == product_id)

    # Join with Product and Category tables to include product and category information
    query = query.join(Product, Sale.product_id == Product.id)
    query = query.join(Category, Product.category_id == Category.id)

    # Select the desired columns for the response
    query = query.with_entities(
        Sale.id,
        Sale.sale_date,
        Product.name.label("product_name"),
        Category.name.label("category_name"),
        Sale.quantity,
    )

    # Execute the query and retrieve the results
    results = query.all()

    # Transform the results into a list of dictionaries
    sales_data = [
        {
            "id": result.id,
            "sale_date": result.sale_date,
            "product_name": result.product_name,
            "category_name": result.category_name,
            "quantity": result.quantity,
        }
        for result in results
    ]

    return sales_data



# Endpoint to get the current inventory status, including low stock alerts
@app.get("/inventory-status", response_model=List[InventoryStatus])
def get_inventory_status(db: Session = Depends(get_db)):
    # Calculate the inventory status and low stock alerts
    inventory_statuses = (
        db.query(Product.id, Product.name, func.sum(Inventory.quantity).label("total_quantity"))
        .join(Inventory, Product.id == Inventory.product_id)
        .group_by(Product.id, Product.name)
        .all()
    )

    # Define a threshold for low stock alerts (you can adjust this threshold as needed)
    low_stock_threshold = 10

    # Create a list of InventoryStatus objects
    result = []
    for product_id, product_name, total_quantity in inventory_statuses:
        is_low_stock_alert = total_quantity < low_stock_threshold
        inventory_status = InventoryStatus(
            product_id=product_id,
            product_name=product_name,
            quantity_in_stock=total_quantity,
            is_low_stock_alert=is_low_stock_alert,
        )
        result.append(inventory_status)

    return result



@app.get("/revenue/daily")
def analyze_daily_revenue(
    date: str = Query(None, description="Date for daily revenue analysis (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    # Build the query but do not execute it yet
    query = (
        db.query(Sale)
        .filter(Sale.sale_date == date)
        .join(Product, Product.id == Sale.product_id)
        .with_entities(Sale.sale_date, func.sum(Sale.quantity * Product.price).label("revenue"))
        .group_by(Sale.sale_date)
    )

    # Print the SQL statement
    print(query.statement)

    # Execute the query
    results = query.all()

    # Transform the results into a list of dictionaries
    daily_revenue = [{"date": result.sale_date, "revenue": result.revenue} for result in results]

    return daily_revenue






# Endpoint to analyze revenue on a weekly basis
# Endpoint to analyze revenue on a weekly basis
@app.get("/revenue/weekly")
def analyze_weekly_revenue(
    start_date: str = Query(None, description="Start date for weekly revenue analysis (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date for weekly revenue analysis (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    query = db.query(Sale)

    if start_date and end_date:
        query = query.filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
    elif start_date:
        query = query.filter(Sale.sale_date >= start_date)
    elif end_date:
        query = query.filter(Sale.sale_date <= end_date)

    query = (
        query
        .join(Product, Product.id == Sale.product_id)
        .with_entities(func.year(Sale.sale_date).label("year"), func.week(Sale.sale_date).label("week"), func.sum(Sale.quantity * Product.price).label("revenue"))
        .group_by("year", "week")
        .all()
    )

    weekly_revenue = [{"year": result.year, "week": result.week, "revenue": result.revenue} for result in query]

    return weekly_revenue



@app.get("/revenue/yearly")
def analyze_yearly_revenue(
    start_year: int = Query(None, description="Start year for yearly revenue analysis (YYYY)"),
    end_year: int = Query(None, description="End year for yearly revenue analysis (YYYY)"),
    db: Session = Depends(get_db),
):
    # Check if start_year and end_year are provided
    if start_year is None or end_year is None:
        return {"error": "Both start_year and end_year must be provided."}

    # Calculate revenue for the specified year range
    query = (
        db.query(Sale)
        .filter(func.year(Sale.sale_date) >= start_year, func.year(Sale.sale_date) <= end_year)
        .join(Product, Product.id == Sale.product_id)
        .with_entities(func.year(Sale.sale_date).label("year"), func.sum(Sale.quantity * Product.price).label("revenue"))
        .group_by("year")
        .all()
    )

    # Transform the results into a list of dictionaries
    yearly_revenue = [{"year": result.year, "revenue": result.revenue} for result in query]

    return yearly_revenue

from fastapi import HTTPException

@app.post("/inventory/update", response_model=InventoryUpdate)
def update_inventory(inventory_update: InventoryUpdate, db: Session = Depends(get_db)):
   
    try:
        # Query the product by product_id
        product = db.query(Product).filter(Product.id == inventory_update.product_id).first()
        print("value",product)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update inventory quantity using product.inventory relationship
        product_inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()

        if product_inventory is None:
            # If no inventory record exists, create a new one
            product_inventory = Inventory(product_id=product.id, quantity=inventory_update.quantity_change)
            db.add(product_inventory)
        else:
            # Update existing inventory quantity
            product_inventory.quantity += inventory_update.quantity_change

        # Log the inventory change with timestamp using product.InventoryChangeLog relationship
        log_entry = InventoryChangeLog(product_id=product.id, quantity_change=inventory_update.quantity_change)
        db.add(log_entry)
        print(log_entry)
        # Commit changes to the database
        db.commit()
        # Fetch the updated inventory entry
        # Fetch the updated inventory entry
       
        return inventory_update  # Return the updated entry
 # Return the updated entry
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
