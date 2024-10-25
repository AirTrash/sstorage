from . import users, tokens, secrets


all_routers = (
    users.router,
    tokens.router,
    secrets.router,

)