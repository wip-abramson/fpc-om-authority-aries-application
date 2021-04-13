from aiohttp import web
import async_timeout
import requests
import datetime
import secrets
import config
from datetime import timedelta
from om_authority_agent import om_authority_agent

from aioauth.server import AuthorizationServer

from models import PresentationFactory

POLL_INTERVAL = 5000
POLL_MAX_TRIES = 12

async def authorize(request):
    # pres_req_conf_id = request.GET.get("pres_req_conf_id")
    ## THINK THIS IS EQUIVALENT
    pres_req_conf_id = request.rel_url.query['pres_req_conf_id']

    if not pres_req_conf_id:
        return web.HTTPBadRequest()

    # scopes = request.GET.get("scope")
    scopes = request.rel_url.query["scope"]
    if not scopes or "vc_authn" not in scopes.split(" "):
        return web.HTTPBadRequest()

    # await validatePresentation(request)

    aut = AuthorizationServer()
    try:
        aut.validate_params()
    except Exception as e:
        # return HttpResponseBadRequest(
        #     f"Error validating parameters: [{e.error}: {e.description}]"
        # )
        return web.HTTPBadRequest(
            # f"Error validating parameters: [{e!r}: {e!r}]"
        )

    response = await om_authority_agent.agent_controller.proofs.create_request(om_authority_agent.client_auth_policy)
    response = response[0]

    print('PROOF REQUEST: ', response)
    # TODO - NOT SURE ABOUT THIS COMMENT -- the current DID of the Agent is already ledgered on Stagingnet
    # This creates a scenario where the endpoint being fetched is wrong
    # Need to update the code so that new DIDs can be ledgered to stagingnet together with endpoints


    public_did = await om_authority_agent.agent_controller.wallet.get_public_did()
    public_did = public_did[0]['result']
    print('PUBLIC DID: ', public_did)

    endpoint = await om_authority_agent.agent_controller.ledger.get_did_endpoint(public_did['did'])
    endpoint = endpoint[0]['endpoint']
    print('ENDPOINT ', endpoint)
    presentation_request = PresentationFactory.from_params(
        presentation_request=response.get("presentation_request"),
        p_id=response.get("thread_id"),
        verkey=[public_did.get("verkey")],
        endpoint=endpoint,
    ).to_json()

    print('PROOF REQUEST: ', presentation_request)

    presentation_request_id = response["presentation_exchange_id"]

    ## TODO this is a django oidc function
    url, b64_presentation = create_short_url(presentation_request)
    print(url)



    ## TODO need to replace with oic stuff to create session
    session = AuthSession.objects.create(
        presentation_record_id=pres_req_conf_id,
        presentation_request_id=presentation_request_id,
        presentation_request=presentation_request,
        request_parameters=request,
        expired_timestamp= timezone.now() + timedelta(minutes=60),
    )
    mapped_url = MappedUrl.objects.create(url=url, session=session)
    print(mapped_url)
    short_url = mapped_url.get_short_url()
    print(short_url)



    print('SESSION ', session)
    print('sessionpk: ', str(session.pk))
    print('mapped_url: ', mapped_url)
    print('short_url: ', short_url)
    print('presx_id: ', presentation_request_id)
    print('b64 presx: ', b64_presentation)


    return short_url, str(session.pk), presentation_request_id, b64_presentation

    print('TEST:', test[0])
    short_url, session_id, pres_req, b64_presentation = test[0]

    request = set_session(request, session_id)
    # request.session["sessionid"] = session_id


    json_response =    {
            "url": short_url,
            "b64_presentation": b64_presentation,
            "poll_interval": settings.POLL_INTERVAL,
            "poll_max_tries": settings.POLL_MAX_TRIES,
            "poll_url": f"{settings.SITE_URL}/vc/connect/poll?pid={pres_req}",
            "resolution_url": f"{settings.SITE_URL}/vc/connect/callback?pid={pres_req}",
            "pres_req": pres_req,
        },
    return web.json_response(json_response)


def poll(request):

    # presentation_request_id = request.GET.get("pid")
    presentation_request_id = request.rel_url.query["pid"]

    if not presentation_request_id:
        return web.HTTPNotFound()

    ## TODO translate to aiohttp and oic
    # session = get_object_or_404(
    #     AuthSession, presentation_request_id=presentation_request_id
    # )
    # if not session.presentation_request_satisfied:
    #     return HttpResponseBadRequest()

    return web.HTTPOk()


def callback(request):

    presentation_request_id = request.GET.get("pid")
    if not presentation_request_id:
        return web.HTTPNotFound()

    ## TODO translate to aiohttp and oic
    # session = get_object_or_404(
    #     AuthSession, presentation_request_id=presentation_request_id
    # )

    if not session.presentation_request_satisfied:
        return web.HTTPBadRequest()

    if session.request_parameters.get("response_type", "") == "code":
        redirect_uri = session.request_parameters.get("redirect_uri", "")
        url = f"{redirect_uri}?code={session.pk}"
        state = session.request_parameters.get("state")
        if state:
            url += f"&state={state}"
        return web.HTTPFound(url)

    return web.HTTPBadRequest()



async def token_endpoint(request):

    message = await request.json()
    grant_type = message.get("grant_type")
    if not grant_type or grant_type != "authorization_code":
        return web.HTTPBadRequest()

    session_id = message.get("code")
    if not session_id:
        return web.HTTPBadRequest()

    ## TODO Translate to aiohttm
    # session = get_object_or_404(AuthSession, id=session_id)

    if not session.presentation_request_satisfied:
        return web.HTTPBadRequest()

    try:
        token = create_id_token(session)
        session.delete()
    except Exception as e:
        # logger.warning(f"Error creating token for {session_id}: {e}")
        return web.HTTPServerError()

    # Add CorsOrigin with cors_allow_any?

    data = {"access_token": "invalid", "id_token": token, "token_type": "Bearer"}
    return web.json_response(data)


def set_session(request, session_id):
    request.session["sessionid"] = session_id
    return request



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