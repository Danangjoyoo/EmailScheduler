import os, asyncio, dotenv

dotenv.load_dotenv()

from flask import Flask, request, g
from flask_swagger_ui import get_swaggerui_blueprint

from app.database import connection, mock
from app.dependencies.schedule import Scheduler
from app.routers.email import controller as emailCtl
from app.routers.email.rest import router as email_router
from app.routers.user.rest import router as user_router
from app.routers.event.rest import router as event_router

app = Flask(__name__)

swagger = get_swaggerui_blueprint(
    base_url="/docs",
    api_url="/static/openapi.json"
)

app.register_blueprint(swagger)
app.register_blueprint(email_router)
app.register_blueprint(user_router)
app.register_blueprint(event_router)

@app.before_request
async def generate_database_session():
    async with connection.session() as sess:
        g.session = sess

@app.after_request
async def close_database_session(response):
    await g.session.close()
    return response

## saat ini hanya bisa kirim lewat user-1 (joy.choco.banana@gmail.com)
## ideally bisa menggunakan login untuk define user mana yang request
## function ini sama dengan function 'save_email' under router email -> "/emai/save_email"
@app.post("/save_email")
async def save_created_email():
    try:
        return await emailCtl.create_scheduled_email(request, g.session)
    except Exception as e:
        emailCtl.logger.error(e)
        return emailCtl.create_response(status=emailCtl.status.error(e))

scheduler = Scheduler(interval=os.getenv("CHECK_INTERVAL"))

async def startup():
    await connection.init_db()
    await mock.mock_data()

if __name__ == "__main__":
    asyncio.run(startup(), debug=True)
    # scheduler.start()
    app.run(
        host=os.getenv("APP_HOST"),
        port=os.getenv("APP_PORT")
        )