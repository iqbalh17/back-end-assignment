Modern backend API for menu management powered by artificial intelligence (Google Gemini AI). This API features automation ranging from description generation to food health analysis.

## Key Features

-   **Complete Menu CRUD:** Menu data management (Create, Read, Update, Delete) with a database.
-   **AI Auto-Description & Aut-Calorie Counter :** AI automatically generates descriptions and calorie based on name & ingredients.
-   **AI Health Check:** Automatic analysis of allergen content, dietary labels (Vegan/Dairy-Free), and health scores.
-   **AI Burn-it Calculator:** Calculates the estimated exercise needed to burn the menu's calories.
-   **Search & Filter:** Advanced search based on price, category, and calories.

## Technologies Used

-   **Framework:** FastAPI (Python)
-   **Database:** SQLite (Local) / PostgreSQL (Production)
-   **AI Model:** Google Gemini 2.5 Flash
-   **ORM:** SQLModel (SQLAlchemy wrapper)
-   **Deployment:** vercel.com

## How to Run (Localhost)

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/USERNAME/REPO_NAME.git](https://github.com/USERNAME/REPO_NAME.git)
    cd REPO_NAME
    ```

2.  **Setup Virtual Environment**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Library**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key**
    Create a new `.env` file, then fill in:
    ```env
    GOOGLE_API_KEY="gemini_key"
    DATABASE_URL="sqlite:///./menu.db"
    ```

5.  **Run Server**
    ```bash
    uvicorn main:app --reload
    ```
    Access documentation at: `http://127.0.0.1:8000/docs`

## Live Demo (Online Access)

This application has been deployed and can be accessed online without installation.

- **Base URL:** `https://menu-api-beta.vercel.app`
- **API Documentation (Swagger UI):** [Click Here to Try API](https://menu-api-beta.vercel.app/docs)

---

## API Documentation

This API has documentation on Swagger UI.
**[Click Here to Open Complete Documentation](https://menu-api-beta.vercel.app/docs)**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/menu` | GET | Retrieves menu list. |
| `/menu/search` | GET | Searches menu with filter & pagination. |
| `/menu` | POST | Adds new menu. |
| `/menu/{id}` | DELETE | Delete menu with id. |
| `/menu/{id}` | PUT | Edit menu with id. |
| `/menu/group-by-category` | GET | Retrieve menus grouped by category. |
| `/menu/{id}/health-check` | GET | Check health & allergy info (AI). |
| `/menu/{id}/burn-it` | GET | Calorie burn calculator (AI). |

## How to use AI Features

### 1. AI Auto-Description & Auto-Calorie Counter

To trigger the automatic description generation by Google Gemini, simply set the `description` field to `"(AI)"` & set `calorie` to `0` when creating a new menu via the **POST** request.

**Example Request Body:**
```json
{
  "name": "Special Fried Rice",
  "category": "Food",
  "price": 25000,
  "description": "(AI)",
  "ingredients": ["Rice", "Egg", "Chicken", "Soy Sauce"],
  "calories" : 0
}
```

**Response with Auto-Description:**
```json
{
    "message": "Menu created successfully",
    "data": {
        "price": 25000.0,
        "id": 9,
        "description": "Experience our exquisite Special Fried Rice, where fragrant jasmine rice is masterfully wok-tossed with tender chicken, delicate scrambled egg, and a whisper of our signature aged soy for a symphony of umami.",
        "created_at": "2025-11-25T11:42:26.028604",
        "calories": 820,
        "name": "Special Fried Rice",
        "category": "Food",
        "ingredients": [
            "Rice",
            "Egg",
            "Chicken",
            "Soy Sauce"
        ],
        "updated_at": "2025-11-25T11:42:26.028615"
    }
}
```
### 2. AI Health Check
To analyze allergens and health score, send a GET request with the specific Menu ID.

- **Endpoint:** `/menu/{id}/health-check`

- **Example:** `GET /menu/1/health-check`

  **Response:**
  ```json
  {
        "menu_name": "Special Fried Rice",
        "allergens": [
            "Egg",
            "Soy",
            "Gluten"
        ],
        "diet_labels": [
            "High Protein",
            "Dairy-Free"
        ],
        "health_score": 7,
        "advice": "To boost health, consider adding more vegetables and requesting less soy sauce to reduce sodium and increase nutrients."
  }
  ```


### 3. AI Burn-it Calculator
To calculate the exercise duration needed to burn the menu's calories, send a GET request with the specific Menu ID.

- **Endpoint:** `/menu/{id}/burn-it`

- **Example:** `GET /menu/1/burn-it`

  **Response:**
  ```json
  {
    "menu_name": "Special Fried Rice",
    "calories": 820,
    "exercises": [
            {
                "activity": "Running",
                "duration": "75 mins",
                "intensity": "Medium"
            },
            {
                "activity": "Cycling",
                "duration": "126 mins",
                "intensity": "Low"
            },
            {
                "activity": "Swimming",
                "duration": "66 mins",
                "intensity": "High"
            }
        ]
    }  

