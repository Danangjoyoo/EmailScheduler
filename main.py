import os, asyncio, dotenv

dotenv.load_dotenv()

from flask import Flask, session
from flask_swagger_ui import get_swaggerui_blueprint

from app.database import connection
from app.dependencies.schedule import Scheduler
from app.routers.email.rest import router as email_router
from app.routers.user.rest import router as user_router

app = Flask(__name__)

swagger = get_swaggerui_blueprint(
    base_url="/docs",
    api_url="/static/openapi.json"
)

app.register_blueprint(swagger)
app.register_blueprint(email_router)
app.register_blueprint(user_router)

scheduler = Scheduler(interval=os.getenv("CHECK_INTERVAL"))

if __name__ == "__main__":
    asyncio.run(connection.init_db())
    # scheduler.start()
    app.run(
        host=os.getenv("APP_HOST"),
        port=os.getenv("APP_PORT")
        )