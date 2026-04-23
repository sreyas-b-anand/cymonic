from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from config import SupabaseConfig
class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.supabase = SupabaseConfig()

    async def dispatch(self, request: Request, call_next):

        print("COOKIES:", request.cookies)

        if request.url.path in ["/health"]:
            return await call_next(request)

        token = request.cookies.get("sb-access-token")

        request.state.user = None

        if token:
            try:
                res = self.supabase.client.auth.get_user(token)
                request.state.user = res.user
                print("Authenticated user:", res.user)

            except Exception as e:
                print("Auth error:", e)
                request.state.user = None

        return await call_next(request)