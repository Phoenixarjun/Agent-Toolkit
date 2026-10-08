# Security Assurance Principles

Use when distinguishing evidence from confidence, selecting appropriate controls, or making audit claims.

## Assurance is scoped and temporal

An audit result applies to a specific revision/build, environment, time window, scope, identities and executed verification activities. A source commit does not identify a deployed binary unless provenance links them. Changes after an assessment may invalidate affected evidence.

## Necessary distinctions

- **Design claim**: architecture or intended policy states a security property.
- **Implementation evidence**: code/config appears to enforce the property.
- **Observed behavior**: authorized runtime probe exercised a defined boundary.
- **Verified property**: sufficient relevant, independent evidence supports the property for tested scope. Not universal absence of attack paths.
- **Compliance**: legal/contractual/organizational conclusion, frequently outside a source-only code assessment.

Failing to establish a property is not identical to proving a vulnerability. A single scanner finding is not automatically a confirmed exploit.

## Risk reasoning

Determine severity using threat actors, exposed surface, privileges needed, plausible exploit path, confidentiality/integrity/availability consequences, blast radius, detectability, and compensating controls. Use a reproducible scoring standard such as CVSS only when inputs are supported; business impact can warrant separate prioritization.

Do not assume high exposure is the only concern; an internal administrator tool can be critical if compromise carries substantial privilege and data access. Do not assume no reported vulnerability equals secure.

## Selective assurance and overengineering

A control is appropriate when it is mandated by an applicable obligation or justified by a credible security property. Prefer the smallest sufficiently protective solution, not the most impressive technology. Record reasoned exclusions and residual risks; recommendations should distinguish required corrections from optional hardening.

## Confirmation discipline

A strong security finding contains:
- invariant expected to hold
- path or boundary that broke it
- scope and authorized method
- observed outcome and reproducible evidence
- supported consequence, confidence and limitations
- practical remediation objective without forcing a specific architecture

If active testing is not authorized/available, mark the lack of independent verification. Never manufacture evidence, screenshots, tool logs or success percentages.

## Human authority

Auditors can recommend, not accept organizational risk for an owner or grant formal certifications. Human experts remain appropriate for penetration testing, cryptographic assurance, legal compliance and high-risk release decisions. The assessor must be able to conclude that existing controls are sufficient **within tested scope** rather than inventing new work.

## Report confidentiality

Audit reports can expose architecture and security weaknesses. Share with authorized recipients; redact secrets, personal data, and unnecessary exploit artifacts. Make detailed reproductions accessible only to a controlled remediation audience.
