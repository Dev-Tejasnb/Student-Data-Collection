from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
import logging
import jinja2

from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import public, auth, admin_students, admin_pdf


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create a custom Jinja2 environment with cache disabled to fix Python 3.14 compatibility
# See: https://github.com/pallets/jinja/issues/2038
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    cache_size=0,  # Disable cache to fix Python 3.14 compatibility issue
    autoescape=True,
    enable_async=True,
)

# Create a simple async template renderer
class TemplateRenderer:
    def __init__(self, env):
        self.env = env
    
    async def TemplateResponse(self, template_name, context, status_code=200, headers=None, media_type="text/html"):
        from fastapi.responses import HTMLResponse
        template = self.env.get_template(template_name)
        content = await template.render_async(context)
        return HTMLResponse(content=content, status_code=status_code, headers=headers, media_type=media_type)

templates = TemplateRenderer(jinja_env)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="College Student Data Collection System",
    description="A professional college student data collection and administration system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(admin_students.router)
app.include_router(admin_pdf.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return await templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return await templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return await templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/student-details", response_class=HTMLResponse, include_in_schema=False)
async def student_details(request: Request):
    return await templates.TemplateResponse("student_details.html", {"request": request})


@app.get("/health", include_in_schema=False)
async def health_check():
    database = await get_database()
    await database.command("ping")
    return {"status": "healthy", "database": "connected"}