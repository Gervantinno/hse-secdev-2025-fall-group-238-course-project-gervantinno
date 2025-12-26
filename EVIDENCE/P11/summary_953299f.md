# P11 DAST ZAP Scan Summary - Commit 953299f

**Scan Date:** Fri Dec 26 14:18:33 UTC 2025
**Commit:** 953299f
**Target URL:** http://localhost:8534
**Workflow Run:** 20523908559

## Scan Results
- **High:** 0
- **Medium:** 0
- **Low:** 0
- **Informational:** 5
- **Total URLs:** 3
- **Passed Checks:** 68

## Findings
✅ No security issues found (only informational).

## Risk Acceptance Decisions
### Fetch Metadata Headers Missing (4 findings)
**Risk Level:** Informational
**Decision:** Accept risk
**Justification:** These headers (Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site, Sec-Fetch-User) are designed for browser protection against cross-site attacks. Our API is consumed programmatically by internal services, not browsers. The risk is acceptable for our use case.

### Cacheable Error Pages (1 finding)
**Risk Level:** Informational
**Decision:** Accept risk
**Justification:** The cacheable content is limited to 404 error pages and robots.txt which contain no sensitive data. This will be addressed in production deployment with proper Cache-Control headers.
