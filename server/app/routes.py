from views import invite, check_trusted, data_scientist_invite, data_owner_invite, authorize

def setup_routes(app):
    app.router.add_get('/connection/new', invite)
    app.router.add_get('/connection/{conn_id}/trusted', check_trusted)
    app.router.add_post('/connection/{conn_id}/datascientist/new', data_scientist_invite)
    app.router.add_post('/connection/{conn_id}/dataowner/new', data_owner_invite)
    app.router.add_get('vc/connect/authorize', authorize)
    app.router.add_get('vc/connect/poll')
    app.router.add_get('vc/connect/callback')
    app.router.add_post('vc/connect/token')

    # path("", views.authorize, name="authorize"),
    # path("vc/connect/poll", views.poll, name="poll"),
    # path("vc/connect/callback", views.callback, name="callback"),
    # path("vc/connect/token", views.token_endpoint, name="token_endpoint"),