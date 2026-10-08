# Regulatory and Contractual Applicability

This is **conditional knowledge**, not a universal security checklist or legal opinion. Consult only if jurisdiction, industry, customer requirements, regulated status, personal-data handling or contractual commitments make it relevant. Official requirements and effective dates may change; verify against current primary sources on each material assessment.

## Decision procedure

1. Identify entity roles (controller/processor, covered entity/business associate, merchant/service provider, etc.), jurisdiction, customers, actors, data categories, data flows and deployment geography.
2. Identify plausible **laws, contractual standards and assurance programs** separately.
3. Record the fact supporting each trigger and what is missing; do not assume applicability from a product nickname.
4. Read authoritative current requirements and commencement/transition dates; link exact source/version.
5. Map *technical controls assessable from the application* to requirements. Put legal, business-process and organizational requirements outside the code-audit evidence boundary unless directly assessed.
6. Mark unresolved applicability `UNDETERMINED`, not noncompliant or not-applicable. Request accountable legal/compliance confirmation for consequential conclusions.

## Trigger examples and cautions

### United States: HIPAA

Applicability depends on covered-entity/business-associate status and protected health information handled in the specified relationship, **not simply “fitness app” or “health data.”** A consumer app receiving data directly at an individual's request can be outside HIPAA, while an app processing PHI for a covered provider can be within scope. Examine relationships, contracts/BAAs and flows before mapping technical safeguards. No code-only “HIPAA certified” claim.

Official: [HHS covered entities](https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html), [HHS business associates](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/business-associates/index.html), [HHS app access FAQ](https://www.hhs.gov/hipaa/for-professionals/faq/does-hipaa-require-a-covered-entity-to-enter-into-a-business-associate-agreement.html).

### European Union: GDPR

Consider controller/processor establishment, offering goods/services to persons in the EU, and monitoring behavior there; data center location alone is not decisive. Personal-data categories, processing purposes and actor relationships determine applicable obligations. Code audit may verify technical protections; cannot determine full lawfulness of processing, notices, contracts, data subject rights, or organizational compliance by itself.

Official: [European Commission applicability](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/application-gdpr_en).

### India: Digital Personal Data Protection Act / Rules

Check relevant digital-personal-data processing, data-fiduciary/processor role, applicable exceptions, cross-border facts and phased commencement. The November 2025 notification phased commencement of provisions; **do not assume all provisions are in force on the audit date**. Verify the current gazette, notifications, rules and corrigenda before any assertion.

Official: [MeitY DPDP Rules and updates](https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digit), [commencement notification](https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf).

### Payment cards: PCI DSS

PCI DSS is about payment-card account data and security of the cardholder data environment, not “any application involving money.” Payment processing outsourced to a provider can substantially reduce merchant technical scope but may leave contractual oversight/validation requirements. PCI SSC states risk acceptance does **not** let organizations elect to ignore applicable PCI DSS requirements. Confirm with the applicable acquiring/payment brand/compliance owner; never self-certify a PCI program from source inspection.

Official: [PCI SSC: requirement applicability](https://www.pcisecuritystandards.org/faqs/do-all-pci-dss-requirements-apply-to-every-system-component/), [outsourced payment merchant scope](https://www.pcisecuritystandards.org/faqs/does-pci-dss-apply-to-merchants-who-outsource-all-payment-processing-operations-and-never-store-process-or-transmit-cardholder-data/), [bank account versus card data](https://www.pcisecuritystandards.org/faqs/1335/).

### Identity assurance: NIST SP 800-63-4

Provides normative guidance for covered federal digital identity systems and useful risk-based recommendations elsewhere. Do **not** automatically demand AAL3 for all banking applications or every financial transaction. Identify whether the standard is binding or advisory; determine authenticator requirements from threat, regulation, customer contract and risk.

Official: [NIST SP 800-63-4](https://csrc.nist.gov/pubs/sp/800/63/4/final).

### SOC 2 / ISO/IEC 27001

These concern organizational control assurance and management systems. A single application code audit cannot confer a SOC 2 report or ISO certification. Map relevant technical controls as supporting evidence without conflating them with an organizational attestation.

### Other jurisdictions or sectors

Financial, medical-device, educational, children's data, telecom, government, export-control and other rules may apply. **Do not assume omissions are violations or exhaustively enumerate the world's laws.** Determine jurisdiction, relationship, activity and current rules from official sources; defer to qualified legal/compliance specialists when uncertain.

## Reporting obligations

State for each suggested regime:
- `CONFIRMED_APPLICABLE`, `POTENTIALLY_APPLICABLE`, `NOT_APPLICABLE`, or `UNDETERMINED` **for screening purposes only**
- triggering facts and missing facts
- latest source checked, version/date and scope caveat
- *technical checks performed* versus *organizational/legal checks not performed*
- next human decision, if required

No statement in this guide authorizes a definitive legal-compliance verdict.
