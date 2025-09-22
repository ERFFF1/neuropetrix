import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import Response

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(self, request, call_next):
        rid = request.headers.get(self.header_name) or uuid.uuid4().hex[:8]
        request.state.request_id = rid
        resp: Response = await call_next(request)
        resp.headers[self.header_name] = rid
        return resp


