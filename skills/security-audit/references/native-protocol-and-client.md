# Conditional Native, Protocol and Client Security Paths

Load **only** when the architecture contains the relevant attack surface. The standard application/API reference does not replace these specialized investigations. These are selection prompts for expert inspection, not exhaustive lists or a license to run intrusive tools.

## Native code / FFI / parsers

Trigger: C/C++, unsafe Rust blocks, native extensions, FFI boundaries, kernel/driver interactions, parsers of untrusted binary formats, performance-critical unsafe memory paths.

Trace external bytes and object ownership through parsing, allocation, lifetime, conversion, memory access and final effects. Look for:
- bounds/length mismatch, integer over/underflow, signedness truncation, pointer arithmetic
- use-after-free, double free, dangling references, race-induced memory safety failures
- unsafe FFI assumptions and inconsistent ownership/borrowing
- privilege changes, sandbox escapes, loader/configuration trust, parsing differential

Use existing sanitizer builds, compile flags, fuzz corpora, SAST or memory-safe test harnesses **when already configured or explicitly authorized**. A sanitizer run without a crash is not proof of safety; no sanitizer available is a coverage limitation.

## HTTP protocol, reverse proxies and caches

Trigger: multiple HTTP parsers/versions, reverse proxy ↔ origin, CDN/cache with authentication, gateways, cross-origin sessions, proxy routing, request normalization.

Verify trust boundaries across parser/framing/normalization differences, header and path canonicalization, cache-key partitioning, auth-related cache variation, forwarded-host/proto trust, request smuggling/desync potential, CSRF/CORS coupling, cookie boundaries and OAuth redirect handling. Keep probes *non-destructive and scoped*; request-desynchronization tests can affect other users and generally require dedicated isolated fixtures.

Do not claim that a framework is vulnerable solely because it supports HTTP/2, chunked bodies or a proxy. Show a relevant boundary and observation.

## Browser/mobile client trust

Trigger: SPA, embedded webviews, postMessage/cross-window flows, service workers, extensions, mobile local storage, deep links, exported components.

Trace attacker-controlled message origins, DOM sinks, session storage/cookie behavior, service worker caching, navigation/deep-link parsing, token persistence and permissions. Client-side controls cannot substitute for server-side authority. Validate the real consumer interaction when authorized and safe.

## Criticality and handoff

If these paths are high impact and specialized dynamic tools or environment access are unavailable, record an explicit blocked/unverified boundary and recommend a specialist engagement. Do not improvise invasive experiments against shared or production systems.
