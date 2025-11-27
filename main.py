from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from typing import List, Optional

from database import create_db_and_tables, get_session
from models import Menu
from schemas import MenuCreate, MenuResponse, PaginatedResponse, HealthCheckResponse, BurnCaloriesResponse
import services

# Initialize FastAPI application
app = FastAPI(
    title="Smart Menu API",
    description="Backend API for menu management with Generative AI integration.",
)

@app.on_event("startup")
def on_startup():
    """
    Event handler executed on application startup.
    Initializes database connection and creates tables if they don't exist.
    """
    create_db_and_tables()

# Exception Handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPExceptions.
    Returns a standardized JSON response when errors occur.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# 1. SEARCH
@app.get("/menu/search", response_model=PaginatedResponse, summary="Search Menu")
def search_menu(
    q: str, 
    page: int = 1, 
    per_page: int = 10, 
    db: Session = Depends(get_session)
):
    """
    Simple menu search endpoint.
    
    Args:
        q (str): Search keyword (query).
        page (int): Page number for pagination.
        per_page (int): Number of items per page.
    
    Returns:
        PaginatedResponse: List of menus matching the keyword.
    """
    return list_menu(page=page, per_page=per_page, q=q, db=db)

# 2. GROUP BY CATEGORY
@app.get("/menu/group-by-category", summary="Aggregate Menus by Category")
def group_by_category(
    mode: str = "list", 
    per_category: int = 5,
    db: Session = Depends(get_session)
):
    """
    Groups menus based on their categories.
    
    Args:
        mode (str): 'count' for quantity statistics, 'list' for item details.
        per_category (int): Limit items per category (only applies if mode='list').
    """
    # Count Mode: Returns item count per category
    if mode == "count":
        results = db.exec(select(Menu.category, func.count(Menu.id)).group_by(Menu.category)).all()
        data_count = {r[0]: r[1] for r in results}
        return {"data": data_count}
    
    # List Mode: Fetches all data and groups manually
    menus = db.exec(select(Menu)).all()
    grouped = {}
    for m in menus:
        if m.category not in grouped:
            grouped[m.category] = []
        
        # Logic to limit items per category
        if len(grouped[m.category]) < per_category:
            grouped[m.category].append(m)
    
    return {"data": grouped}

# 3. CREATE
@app.post("/menu", response_model=dict, status_code=201, summary="Create New Menu")
async def create_menu(menu_in: MenuCreate, db: Session = Depends(get_session)):
    """
    Creates a new menu item in the database.
    
    AI Integration Features:
    - If description is set to "(AI)", system auto-generates description.
    - If calories is set to 0, system auto-estimates calories.
    """
    # Check AI trigger for description or calories
    if menu_in.description == "(AI)" or menu_in.calories == 0:
        ai_data = await services.generate_menu_details(menu_in.name, menu_in.ingredients)
        if ai_data:
            if menu_in.description == "(AI)":
                menu_in.description = ai_data.get("description")
            if menu_in.calories == 0:
                menu_in.calories = ai_data.get("calories")

    # Map schema data to database model
    new_menu = Menu.model_validate(menu_in)
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    
    return {"message": "Menu created successfully", "data": new_menu}

# 4. LIST ALL
@app.get("/menu", response_model=dict, summary="Get Menu List")
def list_menu(
    page: int = 1,
    per_page: int = 10,
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[str] = None, 
    max_price: Optional[str] = None,
    max_cal: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """
    Retrieves menu list with filtering, sorting, and pagination features.
    """
    statement = select(Menu)


    # Filter by query string (name or description)
    if q and q.strip():
        statement = statement.where(
            (Menu.name.ilike(f"%{q}%")) | (Menu.description.ilike(f"%{q}%"))
        )

    # Filter by category
    if category and category.strip():
        statement = statement.where(Menu.category == category)

    # Filter by minimum price range
    if min_price and min_price.strip():
        try:
            val = float(min_price)
            statement = statement.where(Menu.price >= val)
        except ValueError:
            pass

    # Filter by maximum price range
    if max_price and max_price.strip():
        try:
            val = float(max_price)
            statement = statement.where(Menu.price <= val)
        except ValueError:
            pass

    # Filter by maximum calorie limit
    if max_cal and max_cal.strip():
        try:
            val = float(max_cal)
            statement = statement.where(Menu.calories <= val)
        except ValueError:
            pass

    # Sorting
    if sort == "price:asc":
        statement = statement.order_by(Menu.price.asc())
    elif sort == "price:desc":
        statement = statement.order_by(Menu.price.desc())

    # Execute query and implement pagination
    all_results = db.exec(statement).all()
    total_items = len(all_results)
    start = (page - 1) * per_page
    end = start + per_page
    menus = all_results[start:end]

    return {
        "data": menus,
        "pagination": {
            "total": total_items,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_items + per_page - 1) // per_page
        }
    }

    
# 5. GET BY ID
@app.get("/menu/{menu_id}", response_model=dict, summary="Get Menu by ID")
def get_menu(menu_id: int, db: Session = Depends(get_session)):
    """
    Retrieves a single menu detail based on Primary Key (ID).
    Returns 404 if data not found.
    """
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"data": menu}

# 6. UPDATE
@app.put("/menu/{menu_id}", response_model=dict, summary="Update Menu")
async def update_menu(menu_id: int, menu_in: MenuCreate, db: Session = Depends(get_session)):
    """
    Updates existing menu data.
    Supports AI content regeneration if description field is set to "(AI)".
    """
    menu_db = db.get(Menu, menu_id)
    if not menu_db:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Update standard fields
    menu_db.name = menu_in.name
    menu_db.category = menu_in.category
    menu_db.price = menu_in.price
    menu_db.calories = menu_in.calories
    menu_db.ingredients = menu_in.ingredients
    
    # Update AI logic if requested
    ai_data = await services.generate_menu_details(menu_in.name, menu_in.ingredients)
    if menu_in.description == "(AI)":
        menu_db.description = ai_data.get("description")
    else:
        menu_db.description = menu_in.description
    
    db.add(menu_db)
    db.commit()
    db.refresh(menu_db)
    return {"message": "Menu updated successfully", "data": menu_db}

# 7. DELETE
@app.delete("/menu/{menu_id}", summary="Delete Menu")
def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    """
    Permanently deletes menu data from the database based on ID.
    """
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    db.delete(menu)
    db.commit()
    return {"message": "Menu deleted successfully"}

# 8. Allergan
@app.get("/menu/{menu_id}/health-check", response_model=HealthCheckResponse, summary="AI Health Check")
async def check_menu_health(menu_id: int, db: Session = Depends(get_session)):
    """
    AI Feature: Analyzes menu composition for health data.
    
    Returns:
        - Allergen list
        - Diet labels (Vegan/Halal)
        - Health score
        - Consumption advice
    """
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Call AI service for analysis
    health_data = await services.analyze_health(menu.name, menu.ingredients)
    
    return {
        "menu_name": menu.name,
        "allergens": health_data.get("allergens", []),
        "diet_labels": health_data.get("diet_labels", []),
        "health_score": health_data.get("health_score", 5),
        "advice": health_data.get("advice", "Consume wisely.")
    }

# 9. exercise
@app.get("/menu/{menu_id}/burn-it", response_model=BurnCaloriesResponse, summary="AI Calorie Calculator")
async def get_burn_info(menu_id: int, db: Session = Depends(get_session)):
    """
    AI Feature: Calculates estimated physical activity to burn calories.
    If database calories are 0/empty, a default value of 200 is used for calculation.
    """
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Validate calories
    cal = menu.calories if menu.calories > 0 else 200

    # Call AI service for activity calculation
    burn_data = await services.calculate_burn_activity(menu.name, cal)
    
    return {
        "menu_name": menu.name,
        "calories": cal,
        "exercises": burn_data.get("exercises", []),
    }