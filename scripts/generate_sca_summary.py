#!/usr/bin/env python3
"""Генерация SCA summary из JSON отчёта Grype."""

import json
import sys
from pathlib import Path


def main():
    evidence_dir = Path("EVIDENCE/P09")
    sca_report = evidence_dir / "sca_report.json"
    summary_output = evidence_dir / "sca_summary.md"

    summary = "# SCA Summary\n\n"
    summary += "## Vulnerability Count by Severity\n\n"

    try:
        if not sca_report.exists():
            summary += "No SCA report found.\n"
            with open(summary_output, "w") as f:
                f.write(summary)
            return 0

        with open(sca_report, "r") as f:
            data = json.load(f)

        severity_counts = {}
        matches = data.get("matches", [])

        for match in matches:
            vuln = match.get("vulnerability", {})
            severity = vuln.get("severity", "Unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        if severity_counts:
            for severity in [
                "Critical",
                "High",
                "Medium",
                "Low",
                "Negligible",
                "Unknown",
            ]:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    summary += f"- **{severity}**: {count}\n"
        else:
            summary += "No vulnerabilities found.\n"

        summary += f"\n## Total Vulnerabilities: {len(matches)}\n"

        with open(summary_output, "w") as f:
            f.write(summary)

        print("Summary generated successfully")
        return 0
    except json.JSONDecodeError as e:
        summary += f"Error: Invalid JSON in SCA report: {e}\n"
        with open(summary_output, "w") as f:
            f.write(summary)
        return 1
    except Exception as e:
        summary += f"Error generating summary: {e}\n"
        with open(summary_output, "w") as f:
            f.write(summary)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
