#!/bin/bash
# Скрипт для локального тестирования SBOM и SCA сканирования
# Требует Docker

set -e

echo "=== Testing SBOM & SCA Workflow ==="

# Создаём директорию для артефактов
mkdir -p EVIDENCE/P09

echo "1. Generating SBOM with Syft..."
docker run --rm -v "$PWD:/work" -w /work anchore/syft:latest \
  packages dir:. -o cyclonedx-json > EVIDENCE/P09/sbom.json

if [ ! -s EVIDENCE/P09/sbom.json ]; then
  echo "ERROR: SBOM file is empty or not created"
  exit 1
fi

echo "✓ SBOM generated: EVIDENCE/P09/sbom.json"
echo "  Size: $(wc -c < EVIDENCE/P09/sbom.json) bytes"

echo ""
echo "2. Running SCA scan with Grype..."
docker run --rm -v "$PWD:/work" -w /work anchore/grype:latest \
  sbom:/work/EVIDENCE/P09/sbom.json -o json > EVIDENCE/P09/sca_report.json || true

if [ ! -s EVIDENCE/P09/sca_report.json ]; then
  echo "WARNING: SCA report file is empty or not created"
else
  echo "✓ SCA report generated: EVIDENCE/P09/sca_report.json"
  echo "  Size: $(wc -c < EVIDENCE/P09/sca_report.json) bytes"
fi

echo ""
echo "3. Generating summary..."

if command -v jq &> /dev/null; then
  echo "# SCA Summary" > EVIDENCE/P09/sca_summary.md
  echo "" >> EVIDENCE/P09/sca_summary.md
  echo "## Vulnerability Count by Severity" >> EVIDENCE/P09/sca_summary.md
  echo "" >> EVIDENCE/P09/sca_summary.md
  jq '[.matches[].vulnerability.severity] | group_by(.) | map({(.[0]): length}) | add' \
    EVIDENCE/P09/sca_report.json >> EVIDENCE/P09/sca_summary.md 2>/dev/null || echo "No vulnerabilities found." >> EVIDENCE/P09/sca_summary.md
  total=$(jq '.matches | length' EVIDENCE/P09/sca_report.json 2>/dev/null || echo "0")
  echo "" >> EVIDENCE/P09/sca_summary.md
  echo "## Total Vulnerabilities: $total" >> EVIDENCE/P09/sca_summary.md
else
  python3 scripts/generate_sca_summary.py
fi

if [ -f EVIDENCE/P09/sca_summary.md ]; then
  echo "✓ Summary generated: EVIDENCE/P09/sca_summary.md"
  echo ""
  echo "Summary content:"
  cat EVIDENCE/P09/sca_summary.md
else
  echo "ERROR: Summary file not created"
  exit 1
fi

echo ""
echo "=== Test completed successfully ==="
echo "Artifacts in EVIDENCE/P09/:"
ls -lh EVIDENCE/P09/

