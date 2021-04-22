
import os
import requests
import logging
import json
import config
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()
from aries_cloudcontroller import AriesAgentController

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("agent_controller")
logger.setLevel(logging.INFO)

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PORT = os.getenv('WEBHOOK_PORT')
WEBHOOK_BASE = os.getenv('WEBHOOK_BASE')
ADMIN_URL = os.getenv('ADMIN_URL')
API_KEY = os.getenv('ACAPY_ADMIN_API_KEY')

print(WEBHOOK_HOST)
print(WEBHOOK_PORT)
print(WEBHOOK_BASE)

logger.info(f"Initialising Agent. Webhook URL {WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_BASE}. ADMIN_URL - {ADMIN_URL}")





class OMAuthorityAgent:

    def __init__(self, agent_controller):

        self.agent_controller = agent_controller

        asyncio.get_event_loop().run_until_complete(agent_controller.listen_webhooks())


        self.agent_listeners = [{"topic":"connections", "handler": self._connections_handler},
                          {"topic":"present_proof", "handler": self._proof_handler},
                                {
                                    "topic": "issue_credential",
                                    "handler": self._cred_handler
                                }
                                ]

        self.agent_controller.register_listeners(self.agent_listeners, defaults=True)

        self.trusted_client_connection_ids = []
        self.pending_client_connection_ids = []
        self.scientist_connection_ids =[]
        self.datascientist_details_list = []
        self.dataowner_connection_ids = []
        self.dataowner_details_list = []

        self.client_auth_policy =  None




    def _cred_handler(self, payload):
        print("Handle Credentials")
        exchange_id = payload['credential_exchange_id']
        state = payload['state']
        role = payload['role']
        # attributes = payload['credential_proposal_dict']['credential_proposal']['attributes']
        logger.debug(f"Credential exchange {exchange_id}, role: {role}, state: {state}")
        # print(f"Offering: {attributes}")

    def _connections_handler(self, payload):
        global STATE
        connection_id = payload["connection_id"]
        logger.debug("Connection message", payload, connection_id)
        STATE = payload['state']
        if STATE == "response":

            # Ensures connections moved to active
            loop = asyncio.get_event_loop()
            loop.create_task(self.agent_controller.messaging.trust_ping(connection_id, 'hello!'))
            time.sleep(3)
            loop.create_task(self.agent_controller.messaging.trust_ping(connection_id, 'hello!'))
        if STATE == "active":
            loop = asyncio.get_event_loop()
            if connection_id in self.pending_client_connection_ids:
                if self.client_auth_policy:

                    # Specify the connection id to send the authentication request to
                    proof_request_web_request = {
                        "connection_id": connection_id,
                        "proof_request": self.client_auth_policy,
                        "trace": False
                    }
                    response = loop.run_until_complete(self.agent_controller.proofs.send_request(proof_request_web_request))
            elif connection_id in self.scientist_connection_ids:
                for datascientist in self.datascientist_details_list:
                    if datascientist["connection_id"] == connection_id:
                        schema_id = config.data_scientist_schema_id
                        cred_def_id = config.data_scientist_cred_def_id
                        credential_attributes = [
                            {"name": "name", "value": datascientist["name"]},
                            {"name": "scope", "value": datascientist["scope"]},
                        ]
                        logger.info(f"issuing data scientist - {connection_id} a credential using schema {schema_id} and definition {cred_def_id}")
                        loop.run_until_complete(self.agent_controller.issuer.send_credential(connection_id, schema_id,
                                                                    cred_def_id,
                                                                    credential_attributes, trace=False))
                        break
            elif connection_id in self.dataowner_connection_ids:
                for dataowner in self.dataowner_details_list:
                    if dataowner["connection_id"] == connection_id:
                        schema_id = config.data_owner_schema_id
                        cred_def_id = config.data_owner_cred_def_id
                        credential_attributes = [
                            {"name": "name", "value": dataowner["name"]},
                            {"name": "domain", "value": dataowner["domain"]},
                        ]
                        logger.info(f"issuing data scientist - {connection_id} a credential using schema {schema_id} and definition {cred_def_id}")
                        loop.run_until_complete(self.agent_controller.issuer.send_credential(connection_id, schema_id,
                                                                    cred_def_id,
                                                                    credential_attributes, trace=False))


    def _proof_handler(self, payload):
        role = payload["role"]
        connection_id = payload["connection_id"]
        pres_ex_id = payload["presentation_exchange_id"]
        state = payload["state"]
        print("\n---------------------------------------------------------------------\n")
        print("Handle present-proof")
        print("Connection ID : ", connection_id)
        print("Presentation Exchange ID : ", pres_ex_id)
        print("Protocol State : ", state)
        print("Agent Role : ", role)
        print("\n---------------------------------------------------------------------\n")
        if state == "presentation_received":
            # Only verify presentation's from pending scientist connections
            if connection_id in self.pending_client_connection_ids:

                print("Connection is a pending scientist")

                loop = asyncio.get_event_loop()
                print("Verifying Presentation from Data Scientist")
                verify = loop.run_until_complete(self.agent_controller.proofs.verify_presentation(pres_ex_id))
                # Completing future with result of the verification - True of False
                if verify['state'] == "verified":
                    self.trusted_client_connection_ids.append(connection_id)
                self.pending_client_connection_ids.remove(connection_id)






    def client_invitation(self):

        loop = asyncio.get_event_loop()

        client_invite = loop.run_until_complete(self.agent_controller.connections.create_invitation())

        connection_id = client_invite["connection_id"]


        self.pending_client_connection_ids.append(connection_id)

        return {"invite_url": client_invite["invitation_url"], "connection_id": connection_id}

    def data_scientist_invitation(self, name, scope):
        loop = asyncio.get_event_loop()

        scientist_invite = loop.run_until_complete(self.agent_controller.connections.create_invitation())

        connection_id = scientist_invite["connection_id"]

        self.scientist_connection_ids.append(connection_id)

        datascientist = {"connection_id": connection_id, "scope": scope, "name": name}
        self.datascientist_details_list.append(datascientist)

        return {"invitation": scientist_invite["invitation"]}

    def data_owner_invitation(self, name, domain):
        loop = asyncio.get_event_loop()

        owner_invite = loop.run_until_complete(self.agent_controller.connections.create_invitation())

        connection_id = owner_invite["connection_id"]

        self.dataowner_connection_ids.append(connection_id)
        dataowner = {"connection_id": connection_id, "domain": domain, "name": name}
        self.dataowner_details_list.append(dataowner)
        return {"invitation": owner_invite["invitation"]}


    def client_connection_trusted(self, connection_id):
        return connection_id in self.trusted_client_connection_ids


    def set_client_auth_policy(self, proof_request):
        self.client_auth_policy = proof_request


agent_controller = AriesAgentController(admin_url=ADMIN_URL, api_key=API_KEY)

agent_controller.init_webhook_server(webhook_host=WEBHOOK_HOST, webhook_port=WEBHOOK_PORT)
om_authority_agent = OMAuthorityAgent(agent_controller)


async def initialise():

    is_alive = False
    while not is_alive:
        try:
            await agent_controller.server.get_status()
            is_alive = True
            logger.info("Agent Active")
        except:

            time.sleep(5)

    response = await agent_controller.wallet.get_public_did()

    if not response['result']:
        raise Exception("You have not configured your agent as an issuer")
    else:
        logger.info("Public DID: ", response["result"]["did"])



    # We are only asking the Data Scientist to present the scope attribute from their credential
    req_attrs = [
        {"name": "name", "restrictions": [{"schema_id": config.pki_schema_id}]},  # , "cred_def_id": cred_def}]},
    ]

    # We could extend this to request the name attribute aswell if we wanted.

    indy_proof_request = {
        "name": "Proof of PKI Course",
        "version": "1.0",
        "requested_attributes": {
            # They must follow this uuid pattern
            f"0_{req_attr['name']}_uuid":
                req_attr for req_attr in req_attrs
        },
        # Predicates allow us to specify range proofs or set membership on attributes. For example greater than 10.
        # We will ignore these for now.
        "requested_predicates": {
            #         f"0_{req_pred['name']}_GE_uuid":
            #         req_pred for req_pred in req_preds
        },
    }

    om_authority_agent.set_client_auth_policy(indy_proof_request)


# async def write_public_did():
#     # generate new DID
#     response = await agent_controller.wallet.create_did()
#
#     did_object = response['result']
#     did = did_object["did"]
#     logger.debug("New DID", did)
#     # write new DID to Sovrin Stagingnet
#
#     url = 'https://selfserve.sovrin.org/nym'
#
#     payload = {"network": "stagingnet", "did": did_object["did"], "verkey": did_object["verkey"], "paymentaddr": ""}
#
#     # Adding empty header as parameters are being sent in payload
#     headers = {}
#
#     r = requests.post(url, data=json.dumps(payload), headers=headers)
#     if r.status_code != 200:
#         logger.error("Unable to write DID to StagingNet")
#         raise Exception
#
#     response = await agent_controller.ledger.get_taa()
#     taa = response['result']['taa_record']
#     taa['mechanism'] = "service_agreement"
#
#     await agent_controller.ledger.accept_taa(taa)
#
#     await agent_controller.wallet.assign_public_did(did)
#
#     return did_object["did"]