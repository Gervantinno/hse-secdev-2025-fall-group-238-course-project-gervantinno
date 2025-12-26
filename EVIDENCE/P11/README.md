# P11 - DAST (OWASP ZAP Baseline) Reports

## Latest Scan (953299f)
- **ZAP HTML Report:** [zap_baseline_latest.html](zap_baseline_latest.html) (from [zap_baseline_953299f.html](zap_baseline_953299f.html))
- **ZAP JSON Report:** [zap_baseline_latest.json](zap_baseline_latest.json) (from [zap_baseline_953299f.json](zap_baseline_953299f.json))
- **Scan Summary:** [summary_latest.md](summary_latest.md) (from [summary_953299f.md](summary_953299f.md))
- **Scan Date:** Fri Dec 26 14:18:35 UTC 2025
- **Target:** http://localhost:8534

## Available Reports:
| File | Description | Commit |
|------|-------------|--------|
| [zap_baseline_953299f.html](zap_baseline_953299f.html) | ZAP HTML report | 953299f |
| [zap_baseline_953299f.json](zap_baseline_953299f.json) | ZAP JSON report | 953299f |
| [summary_953299f.md](summary_953299f.md) | Scan summary | 953299f |
| [zap_baseline_latest.html](zap_baseline_latest.html) | Latest HTML report (symlink) | 953299f |
| [zap_baseline_latest.json](zap_baseline_latest.json) | Latest JSON report (symlink) | 953299f |
| [summary_latest.md](summary_latest.md) | Latest summary (symlink) | 953299f |

## How to View Reports
1. Click on the HTML links above to view ZAP reports directly in GitHub
2. JSON reports can be parsed with jq or viewed in ZAP desktop
3. Latest reports are available via `_latest` symlinks

## Workflow
Scans are triggered automatically on push to relevant paths or manually via workflow_dispatch.
