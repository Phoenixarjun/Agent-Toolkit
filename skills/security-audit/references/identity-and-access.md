# Identity, Authentication, Authorization and Sessions

Use only for identity/access boundaries actually present. Derive exact expected properties from the application's protocol, identity provider, risk and specification.

## Authentication lifecycle

Identify each factor/identity mechanism, endpoint and principal: human account, admin, service principal, workload identity, external IdP. Map registration, login, recovery, credential update, account lock/suspension, logout, session expiry, and token refresh where implemented.

Inspect algorithm/secret/key use, secure credential storage, brute-force resistance appropriate to risk, session issuance, error leakage, anti-enumeration, verification of claims, secure callback handling and fail-closed errors.

**Runtime evidence**: test with authorized test identities for successful and failing cases, expired/revoked sessions, tampered credentials/tokens, logout behavior, protected-route access after lifecycle changes. Capture redacted requests/results only.

## Authorization is not authentication

For each sensitive operation identify *subject, action, object, tenant, context, effect*. Check enforcement at the server/resource boundary, not only UI visibility or gateway labels.

Select differential tests:
- no session vs valid session
- low privilege vs allowed role
- subject A requesting subject B's private object
- tenant A requesting tenant B's object if multi-tenant
- disallowed field mutation and property-level exposure
- access after role removal, suspension, or session revocation
- worker/event/service pathways bypassing normal HTTP middleware

`403` or `404` responses can both be appropriate for unauthorized object access; confirm no protected side effect or information leakage. One denied route does not prove the whole resource collection is safe.

## JWT and tokens

First determine token purpose and issuer: app-issued session JWT, OAuth access token, OIDC ID token, signed URL, refresh token, opaque reference. Do not assume all are governed by RFC 9068 (`at+jwt` applies to that access-token profile, not every JWT).

Where applicable inspect:
- accepted algorithms and actual signature verification
- key lookup/trust and key rotation
- issuer, audience, expiration and not-before
- token type and cross-token substitution
- refresh/rotation/revocation requirements
- replay and privilege change behavior
- token storage, exposure and propagation across services

Use only controlled tokens/test identities; don't put real secrets/tokens in reports.

## Browser sessions and federation

Inspect cookies (`Secure`, `HttpOnly`, appropriate `SameSite`), CSRF protection where browser credential mechanisms require it, session fixation, lifecycle and cache behavior. For OAuth/OIDC/SAML, validate applicable protocol invariants and IdP configuration—redirect URIs, state, nonce, PKCE, issuer/audience, code exchange, assertion validation—without assuming every deployment needs SSO.

Session timeout, MFA and step-up authentication are **risk decisions**, not uniform mandatory settings. A financial transfer may warrant step-up authorization even if general browsing sessions persist longer. A low-impact application still must enforce its chosen session semantics correctly.

## Evidence pitfalls

- JWT dependency imported != signatures checked.
- Middleware present != every route protected.
- Frontend hides a button != backend denies forbidden action.
- User can log out in UI != an already issued token is necessarily revoked.
- RBAC implemented != object/tenant/property authorization verified.
- One successful IdP login != callback or token-substitution security verified.

Report remaining uncertainty at the level of each property.
