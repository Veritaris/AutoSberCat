import json
from uuid import UUID, uuid4

import uvicorn
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi_sessions.frontends.implementations import CookieParameters, SessionCookie

from app import users
from app.config import settings
from app.main import SberCatClient
from app.middleware import BasicVerifier
from app.models import SessionData

cookie_params = CookieParameters()
backend = InMemoryBackend[UUID, SessionData]()
# Uses UUID
cookie = SessionCookie(
    cookie_name="sbercat_app_token",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Chel"}


@app.post("/register/{token}")
async def create_session(token: str):

    session = uuid4()
    data = SessionData(sbercat_token=token)

    await backend.create(session, data)
    try:
        await users.add_user(data)
    except ValueError:
        return Response(
            content=json.dumps({"error": "token already exists"}), media_type="application/json", status_code=400
        )

    sbercat = SberCatClient(token=token)
    info = await sbercat.get_work_info()

    response = Response(content=json.dumps(info), media_type="application/json")
    cookie.attach_to_response(response, session)

    return response


@app.get("/me", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    sbercat = SberCatClient(token=session_data.sbercat_token)
    info = await sbercat.get_work_info()
    return Response(content=json.dumps(info), media_type="application/json")


@app.post("/stop_using")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await users.delete_user(backend.data.get(session_id))
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"


@app.get("/all/{superkey}")
async def del_session(superkey: str, response: Response, session_id: UUID = Depends(cookie)):
    if superkey != settings.superkey:
        return Response(status_code=1488)

    tokens = await users.get_users_for_auto()

    return Response(
        media_type="application/json",
        status_code=200,
        content=json.dumps({"tokens": tokens})
    )


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=settings.app_port)
