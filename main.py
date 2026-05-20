import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from process_csv import load_schools

app = FastAPI(title="BEIS Project")
app.mount("/static", StaticFiles(directory="static"), name="static") # serving static files like assets, CSS
templates = Jinja2Templates(directory="templates") # jinja templates (e.g HTML)

def main():
    """Entry point. Starts the Uvicorn development server."""
    uvicorn.run("project:app", host="127.0.0.1", port=8000, reload=True)

DF = load_schools('data/beis_project.csv')

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return templates.TemplateResponse(request, "base.html")

@app.get("/explore")
def test(request: Request) -> Response:
    return templates.TemplateResponse(request, "explore.html", {"schools": DF.head().to_dict(orient='records')})

if __name__ == '__main__':
    main()