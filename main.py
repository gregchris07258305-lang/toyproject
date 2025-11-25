from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request

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