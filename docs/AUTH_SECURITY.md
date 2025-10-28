# Authentication & Security Analysis

## Current Implementation

### Token Storage: LocalStorage
- Location: [src/lib/api.ts:28](../src/lib/api.ts#L28)
- Method: JWT tokens stored in `localStorage`
- Transmission: `Authorization: Bearer {token}` header

### Authentication Flow
1. User logs in via `/api/v1/auth/login`
2. Backend returns JWT access & refresh tokens
3. Frontend stores tokens in `localStorage`
4. Each API request includes `Authorization: Bearer {token}` header
5. Backend validates token in [backend/api/dependencies.py](../backend/api/dependencies.py)

### Protected Routes
- **Dashboard**: Now redirects to `/auth` if not authenticated ([src/pages/Dashboard.tsx](../src/pages/Dashboard.tsx))
- **API Endpoints**: Return `401 Unauthorized` without valid token

---

## Security Assessment

### ✅ Current Setup is Acceptable For:
- **Development environments**
- **Internal tools** with trusted users
- **Mobile apps** (where localStorage is sandboxed)
- **Scenarios where** XSS risk is very low

### ⚠️ Security Concerns for Production:

#### 1. XSS Vulnerability
- **Risk**: If malicious script executes on your domain, it can steal tokens from `localStorage`
- **Impact**: Complete account takeover
- **Mitigation**:
  - Strict Content Security Policy (CSP)
  - Input sanitization
  - Regular security audits

#### 2. No Automatic Token Cleanup
- **Risk**: Tokens persist even after browser closes
- **Impact**: Shared computer security issue
- **Mitigation**: Shorter token expiration times

---

## Production-Grade Recommendations

### Option 1: HttpOnly Cookies (Most Secure)

**Benefits:**
- ✅ Immune to XSS attacks (JavaScript can't access cookies)
- ✅ Automatic expiration on browser close (session cookies)
- ✅ Built-in CSRF protection with SameSite attribute

**Changes Required:**

#### Backend Changes:
```python
# backend/api/routes/auth.py

from fastapi import Response

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # ... existing auth logic ...

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set HttpOnly cookies instead of returning tokens in body
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,     # HTTPS only
        samesite="lax",  # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {"message": "Login successful"}
```

```python
# backend/api/dependencies.py

from fastapi import Cookie

async def get_current_user(
    access_token: str = Cookie(None),  # Read from cookie instead of header
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # ... rest of validation ...
```

#### Frontend Changes:
```typescript
// src/lib/api.ts

// Remove manual token management
async login(email: string, password: string) {
  const response = await fetch(`${this.baseUrl}/auth/login`, {
    method: 'POST',
    credentials: 'include',  // Important: Include cookies in request
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString()
  });

  // No need to store token - browser handles it automatically
  return response.json();
}

private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${this.baseUrl}${endpoint}`, {
    ...options,
    credentials: 'include',  // Always include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  // ... rest of code
}
```

#### CORS Configuration:
```python
# backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins, not *
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)
```

---

### Option 2: Keep LocalStorage (Current) + Enhance Security

If you prefer to keep the current implementation:

#### 1. Add Strict CSP Headers
```python
# backend/main.py

response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'sha256-{hash}'; "  # Whitelist specific scripts
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https://api.yourdomain.com"
)
```

#### 2. Shorter Token Expiration
```python
# backend/utils/auth.py

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Instead of 60
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Instead of 30
```

#### 3. Token Rotation
Implement automatic token refresh before expiration

#### 4. XSS Protection Layers
- Sanitize all user inputs
- Use React's built-in XSS protection (avoid `dangerouslySetInnerHTML`)
- Regular dependency updates
- Security scanning in CI/CD

---

## Recommended Approach

### For Production Launch:
**Use HttpOnly Cookies** - It provides the best security with minimal code changes

### Migration Path:
1. **Phase 1** (Current): LocalStorage + enhanced security (CSP, shorter tokens)
2. **Phase 2** (Pre-launch): Migrate to HttpOnly cookies
3. **Phase 3** (Post-launch): Add additional features:
   - Device fingerprinting
   - Suspicious activity monitoring
   - Rate limiting per user
   - Multi-factor authentication (MFA)

---

## Current Status

✅ **Dashboard Protection**: Users are redirected to `/auth` if not logged in
✅ **Token Management**: Tokens stored securely in localStorage (client-side)
✅ **API Protection**: All protected endpoints return 401 without valid token
⚠️ **Production Ready**: Acceptable for MVP, upgrade to HttpOnly cookies before scale

---

## Quick Win: Enable Both Methods

Support both authentication methods simultaneously:

```python
async def get_current_user(
    authorization: str = Header(None),
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    # Try cookie first (more secure)
    token = access_token

    # Fall back to Bearer token
    if not token and authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401)

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # ... validate token
```

This allows gradual migration without breaking existing clients.
