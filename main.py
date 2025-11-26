from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from toyproject_fastapis_db import get_db_connection
from psycopg2.extras import RealDictCursor
import datetime

app = FastAPI()
templates = Jinja2Templates(directory=".")

# http://localhost:8000/toyproject
@app.get("/toyproject")  
async def toyproject(request: Request):
    
    products = [
    {"name": "Laptop","price": 1200,"tags": ["electronics", "office"]},
    {"name": "Smartphone","price": 800,"tags": ["mobile", "electronics"]},
    {"name": "Keyboard","price": 100,"tags": ["accessories"]}
    ]

    
    context = {
        "request": request, 
        "product_list" : products
    }
    return templates.TemplateResponse("users/10_jina2.html"
                                      , context)



@app.on_event("startup")
async def startup_event():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notices (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    finally:
        conn.close()

class Notice(BaseModel):
    title: str
    content: str

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("toyproject_fastapis.html", {"request": request})

@app.get("/api/notices")
async def get_notices():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, title, content, created_at FROM notices ORDER BY created_at DESC")
            notices = cur.fetchall()
            return notices
    finally:
        conn.close()

@app.post("/api/notices")
async def post_notice(notice: Notice):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notices (title, content) VALUES (%s, %s) RETURNING id",
                (notice.title, notice.content)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"id": new_id, "title": notice.title, "content": notice.content}
    except psycopg2.Error as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        conn.close()

@app.delete("/api/notices/{notice_id}")
async def delete_notice(notice_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notices WHERE id = %s RETURNING id", (notice_id,))
            deleted_id = cur.fetchone()
            conn.commit()
            if deleted_id:
                return {"message": "Notice deleted successfully"}
            else:
                return JSONResponse(status_code=404, content={"message": "Notice not found"})
    except psycopg2.Error as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    finally:
        conn.close()