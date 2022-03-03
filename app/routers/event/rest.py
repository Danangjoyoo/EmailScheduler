from flask import Blueprint, request, g

from .controller import (
    show_event,
    create_event,
    update_event,
    remove_event,
    show_participant,
    set_participant,
    remove_participant
)
from . import schema
from ...dependencies.utils import create_response, status, QueryPaginationParams
from ...dependencies.log import logger
from ...database import connection as conn

router = Blueprint(
    name="event", 
    import_name=__name__,
    url_prefix="/event",
    template_folder="/routers/event",
    )

@router.get("")
async def get_event():
    try:
        return await show_event(request, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))
    

@router.post("")
async def post_event():
    try:
        return await create_event(request, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.put("/<id>")
async def put_event(id: int):
    try:
        return await update_event(request, id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.delete("/<id>")
async def delete_event(id: int):
    try:
        return await remove_event(id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.get("/<event_id>/participant")
async def get_participant(event_id: int):
    try:
        return await show_participant(request, event_id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.put("/<event_id>/participant")
async def put_participant(event_id: int):
    try:
        return await set_participant(request, event_id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.delete("/participant/<participant_id>")
async def delete_participant(participant_id: int):
    try:
        return await remove_participant(participant_id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))