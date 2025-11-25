from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from typing import List, Optional

from database import create_db_and_tables, get_session
from models import Menu
from schemas import MenuCreate, MenuResponse, PaginatedResponse, HealthCheckResponse, BurnCaloriesResponse
import services

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Exception Handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# 1. SEARCH
@app.get("/menu/search", response_model=PaginatedResponse)
def search_menu(
    q: str, 
    page: int = 1, 
    per_page: int = 10, 
    db: Session = Depends(get_session)
):
    return list_menu(page=page, per_page=per_page, q=q, db=db)

# 2. GROUP BY CATEGORY
@app.get("/menu/group-by-category")
def group_by_category(
    mode: str = "list", 
    per_category: int = 5,
    db: Session = Depends(get_session)
):
    if mode == "count":
        results = db.exec(select(Menu.category, func.count(Menu.id)).group_by(Menu.category)).all()
        data_count = {r[0]: r[1] for r in results}
        return {"data": data_count}
    
    menus = db.exec(select(Menu)).all()
    grouped = {}
    for m in menus:
        if m.category not in grouped:
            grouped[m.category] = []
        
        # Batasi manual pakai len()
        if len(grouped[m.category]) < per_category:
            grouped[m.category].append(m)
    
    return {"data": grouped}

# 3. CREATE
@app.post("/menu", response_model=dict, status_code=201)
async def create_menu(menu_in: MenuCreate, db: Session = Depends(get_session)):
    if menu_in.description == "(AI)" or menu_in.calories == 0:
        ai_data = await services.generate_menu_details(menu_in.name, menu_in.ingredients)
        if ai_data:
            if menu_in.description == "(AI)":
                menu_in.description = ai_data.get("description")
            if menu_in.calories == 0:
                menu_in.calories = ai_data.get("calories")

    new_menu = Menu.model_validate(menu_in)
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    
    return {"message": "Menu created successfully", "data": new_menu}

# 4. LIST ALL
@app.get("/menu", response_model=dict)
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
    statement = select(Menu)

    is_filtering = (
        (q and q.strip()) or 
        (category and category.strip()) or 
        (min_price and min_price.strip()) or 
        (max_price and max_price.strip()) or 
        (max_cal and max_cal.strip()) or
        (sort is not None)
    )

    if not is_filtering :
        menus = db.exec(select(Menu)).all()
        return {
            "data": menus 
        }

    if q and q.strip():
        statement = statement.where(
            (Menu.name.ilike(f"%{q}%")) | (Menu.description.ilike(f"%{q}%"))
        )

    if category and category.strip():
        statement = statement.where(Menu.category == category)

    if min_price and min_price.strip():
        try:
            val = float(min_price)
            statement = statement.where(Menu.price >= val)
        except ValueError:
            pass

    if max_price and max_price.strip():
        try:
            val = float(max_price)
            statement = statement.where(Menu.price <= val)
        except ValueError:
            pass

    if max_cal and max_cal.strip():
        try:
            val = float(max_cal)
            statement = statement.where(Menu.calories <= val)
        except ValueError:
            pass

    if sort == "price:asc":
        statement = statement.order_by(Menu.price.asc())
    elif sort == "price:desc":
        statement = statement.order_by(Menu.price.desc())

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
@app.get("/menu/{menu_id}", response_model=dict)
def get_menu(menu_id: int, db: Session = Depends(get_session)):
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"data": menu}

# 6. UPDATE
@app.put("/menu/{menu_id}", response_model=dict)
async def update_menu(menu_id: int, menu_in: MenuCreate, db: Session = Depends(get_session)):
    menu_db = db.get(Menu, menu_id)
    if not menu_db:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    menu_db.name = menu_in.name
    menu_db.category = menu_in.category
    menu_db.price = menu_in.price
    menu_db.calories = menu_in.calories
    menu_db.ingredients = menu_in.ingredients
    
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
@app.delete("/menu/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_session)):
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    db.delete(menu)
    db.commit()
    return {"message": "Menu deleted successfully"}

# 8. Allergan
@app.get("/menu/{menu_id}/health-check", response_model=HealthCheckResponse)
async def check_menu_health(menu_id: int, db: Session = Depends(get_session)):
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    health_data = await services.analyze_health(menu.name, menu.ingredients)
    
    return {
        "menu_name": menu.name,
        "allergens": health_data.get("allergens", []),
        "diet_labels": health_data.get("diet_labels", []),
        "health_score": health_data.get("health_score", 5),
        "advice": health_data.get("advice", "Tetap makan dengan bijak.")
    }

# 9. exercise
@app.get("/menu/{menu_id}/burn-it", response_model=BurnCaloriesResponse)
async def get_burn_info(menu_id: int, db: Session = Depends(get_session)):
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    cal = menu.calories if menu.calories > 0 else 200

    burn_data = await services.calculate_burn_activity(menu.name, cal)
    
    return {
        "menu_name": menu.name,
        "calories": cal,
        "exercises": burn_data.get("exercises", []),
    }