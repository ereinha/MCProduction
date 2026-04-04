import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


TEMPLATE_DIR = Path("Inputcards_M15")

# Base process name used in the output line of proc_card.dat
BASE_OUTPUT_PREFIX = "hToaaTo2gamma2tau_ma"
BASE_OUTPUT_SUFFIX = "GeV_MLM_4f_max1j"

# Mass scan (GeV)
MASS_MIN = 3.6
MASS_MAX = 8.0
MASS_STEP = 0.2

# Param-card settings
SET_WHS = True
WHS_VALUE_GEV = 1.0e-6  # keep narrow; override if you have a width model


def frange(mmin: float, mmax: float, step: float) -> List[float]:
    """Inclusive float range with stable rounding."""
    if step <= 0:
        raise ValueError("step must be > 0")
    # Round to 3 decimals by default (enough for MeV-level scans if needed)
    pts: List[float] = []
    x = mmin
    # Add a small epsilon to include endpoint when within rounding
    while x <= mmax + 1e-12:
        pts.append(round(x, 3))
        x += step
    return pts


def mass_tag(m: float) -> str:
    """Mass tag for filenames: 3.6 -> 3p6, 8.0 -> 8p0."""
    s = f"{m:.3f}".rstrip("0").rstrip(".")
    # Keep at least one decimal place for 8.0 -> 8p0 (optional; comment out if undesired)
    if "." not in s:
        s = f"{s}.0"
    return s.replace(".", "p")


@dataclass(frozen=True)
class MassPoint:
    mA: float

    @property
    def tag(self) -> str:
        return mass_tag(self.mA)

    @property
    def folder(self) -> Path:
        return Path(f"Inputcards_M{self.tag}")


def rewrite_filename(fname: str, new_tag: str) -> str:
    """Rewrite filenames that contain maXXGeV to the new mass tag."""
    # Replace the specific template substring first (most common)
    if "ma15GeV" in fname:
        return fname.replace("ma15GeV", f"ma{new_tag}GeV")

    # Generic fallback: replace ma<digits>(p<digits>)?GeV
    return re.sub(r"ma\d+(?:p\d+)?GeV", f"ma{new_tag}GeV", fname)


def update_customizecards(path: Path, mA: float) -> None:
    """Overwrite customizecards.dat content for the given mA."""
    mzdinput = 2.0 * mA

    lines = [
        f"set param_card mzdinput {mzdinput:.6e}",
        f"set param_card mhsinput {mA:.6e}",
        "set param_card epsilon 1.000000e-10",
        "set param_card kap 5.000000e-01",
    ]
    if SET_WHS:
        lines.append(f"set param_card whs {WHS_VALUE_GEV:.6e}")

    # Mass entries used by the provided HAHM example
    lines += [
        f"set param_card mass 35 {mA:.6e}",
        f"set param_card mass 1023 {mzdinput:.6e}",
        "",
    ]

    path.write_text("\n".join(lines))


def update_proc_card_output(path: Path, mA_tag: str) -> None:
    """Patch the 'output ...' line in proc_card.dat."""
    text = path.read_text().splitlines()

    new_output = f"output {BASE_OUTPUT_PREFIX}{mA_tag}{BASE_OUTPUT_SUFFIX}"

    for i, line in enumerate(text):
        if line.strip().startswith("output "):
            text[i] = new_output
            break
    else:
        # No output line found; append one.
        text.append(new_output)

    path.write_text("\n".join(text) + "\n")


def main(mass_points: Iterable[float]) -> None:
    if not TEMPLATE_DIR.is_dir():
        raise FileNotFoundError(
            f"Template directory '{TEMPLATE_DIR}' not found. "
            "Set TEMPLATE_DIR to the folder that contains your reference cards."
        )

    points = [MassPoint(m) for m in mass_points]

    for pt in points:
        pt.folder.mkdir(parents=True, exist_ok=True)

        for src in TEMPLATE_DIR.iterdir():
            if not src.is_file():
                continue

            new_fname = rewrite_filename(src.name, pt.tag)
            dst = pt.folder / new_fname
            shutil.copy(src, dst)

            if "customizecards" in src.name:
                update_customizecards(dst, pt.mA)
            elif "proc_card" in src.name:
                update_proc_card_output(dst, pt.tag)

    print("Generated inputcard folders:")
    for pt in points:
        print(f"  - {pt.folder}/")


if __name__ == "__main__":
    MASS_POINTS = frange(MASS_MIN, MASS_MAX, MASS_STEP)
    main(MASS_POINTS)
