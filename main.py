import os, asyncio, dotenv

dotenv.load_dotenv()

from flask import Flask, session, g
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

@app.before_request
async def generate_database_session():
    async with connection.session() as sess:
        if "sqlite" in os.getenv("DATABASE_URL"):
            await sess.execute("PRAGMA foreign_keys=ON")
        g.session = sess

@app.after_request
async def close_database_session(response):
    await g.session.close()
    return response


scheduler = Scheduler(interval=os.getenv("CHECK_INTERVAL"))

if __name__ == "__main__":
    asyncio.run(connection.init_db())
    # scheduler.start()
    app.run(
        host=os.getenv("APP_HOST"),
        port=os.getenv("APP_PORT")
        )