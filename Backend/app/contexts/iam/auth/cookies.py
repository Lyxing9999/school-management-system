def set_refresh_cookie(resp, refresh_token: str):
    resp.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=False,        # dev HTTP: False
        samesite="Lax",      # dev: Lax. Prod cross-site: None + HTTPS
        path="/api/iam",    
        max_age=14 * 24 * 3600,
    )

def clear_refresh_cookie(resp):
    resp.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=True,
        secure=False,
        samesite="Lax",
        path="/api/iam",     
    )