"""Validate measured RV32I differential test coverage; fail CI on missing bins."""
import json
from pathlib import Path

report = json.loads(Path("verification/reports/rv32i_functional_coverage.json").read_text())
assert report["schema_version"] == 1
assert report["operation_bin_coverage"] == {"hit": 21, "total": 21}
ops = report["operation_counts"]
assert len(ops) == 22 and all(ops[k] >= 100 for k in ops if k != "illegal")
assert ops["illegal"] == 64
assert report["validity_bins"]["legal"] == 3801
assert report["validity_bins"]["illegal"] == 64
assert sum(report["operand_sign_bins"].values()) == 2 * 3801
assert all(report["operand_sign_bins"].get(k, 0) > 0 for k in ("zero", "positive", "negative"))
print("Measured RV32I operation bins: 21/21; legal stimuli: 3801; invalid: 64")
