Modern backend API for menu management powered by artificial intelligence (Google Gemini AI). This API features automation ranging from description generation to food health analysis.

## Key Features

-   **Complete Menu CRUD:** Menu data management (Create, Read, Update, Delete) with a database.
-   **AI Auto-Description:** AI automatically generates descriptions based on name & ingredients.
-   **AI Health Check:** Automatic analysis of allergen content, dietary labels (Vegan/Halal), and health scores.
-   **AI Exercise Calculator:** Calculates the estimated exercise needed to burn the menu's calories.
-   **Search & Filter:** Advanced search based on price, category, and calories.

## Technologies Used

-   **Framework:** FastAPI (Python)
-   **Database:** SQLite (Local) / PostgreSQL (Production)
-   **AI Model:** Google Gemini 2.5 Flash
-   **ORM:** SQLModel (SQLAlchemy wrapper)
-   **Deployment:** Render.com

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

- **Base URL:** `https://your-app-name.onrender.com`
- **API Documentation (Swagger UI):** [Click Here to Try API](https://your-app-name.onrender.com/docs)

**⚠️ Important Note:**
Because it uses the **Render Free Tier** service, the server will restart if not accessed for 15 minutes.
If you open the link above, the loading time might be a bit long (50+ seconds).

---

## API Documentation

This API has documentation on Swagger UI.
**[Click Here to Open Complete Documentation](LINK_RENDER/docs)**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/menu` | GET | Retrieves menu list. |
| `/menu/search` | GET | Searches menu with filter & pagination. |
| `/menu` | POST | Adds new menu (Trigger AI). |
| `/menu/{id}/health-check` | GET | Check health & allergy info (AI). |
| `/menu/{id}/burn-it` | GET | Calorie burn calculator (AI). |