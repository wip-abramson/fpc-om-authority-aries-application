from views import invite, check_trusted, data_scientist_invite, data_owner_invite

def setup_routes(app):
    app.router.add_get('/connection/new', invite)
    app.router.add_get('/connection/{conn_id}/trusted', check_trusted)
    app.router.add_post('/connection/{conn_id}/datascientist/new', data_scientist_invite)
    app.router.add_post('/connection/{conn_id}/dataowner/new', data_owner_invite)