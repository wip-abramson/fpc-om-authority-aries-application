from aiohttp import web
import async_timeout
import requests
import datetime
import secrets
import config
from om_authority_agent import om_authority_agent

async def invite(request):
    # Create Invitation
    # wait for the coroutine to finish
    with async_timeout.timeout(5):
        payload = {
            "include_handshake": True,
            "use_public_did": False
        }

        # Create an out of band Invitation
        json_response = om_authority_agent.client_invitation()
        return web.json_response(json_response)


async def check_trusted(request: web.Request):

    connection_id = request.match_info["conn_id"]

    with async_timeout.timeout(2):

        is_trusted = om_authority_agent.client_connection_trusted(connection_id)

        json_response = {"trusted": is_trusted}

        return web.json_response(json_response)


async def data_scientist_invite(request: web.Request):
    connection_id = request.match_info["conn_id"]

    data = await request.json()

    print("Data Scientist Request ", data)

    if not connection_id:
        return web.HTTPUnauthorized

    if not om_authority_agent.client_connection_trusted(connection_id):
        return web.HTTPUnauthorized

    with async_timeout.timeout(2):

        # connection = await agent_controller.issuer.

        json_response = om_authority_agent.data_scientist_invitation(data["name"], data["scope"])

        return web.json_response(json_response)

async def data_owner_invite(request: web.Request):
    connection_id = request.match_info["conn_id"]

    data = await request.json()

    print("Data Scientist Request ", data)

    if not connection_id:
        return web.HTTPUnauthorized

    if not om_authority_agent.client_connection_trusted(connection_id):
        return web.HTTPUnauthorized

    with async_timeout.timeout(2):

        # connection = await agent_controller.issuer.

        json_response = om_authority_agent.data_owner_invitation(data["name"], data["domain"])

        return web.json_response(json_response)