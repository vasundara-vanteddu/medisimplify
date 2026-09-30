"""Hallucination check: values in the output must appear in the source text."""
import re


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def _numbers(s):
    return re.findall(r"\d+(?:\.\d+)?", str(s))


def _present(value, src, src_nums) -> bool:
    if not value:
        return True
    if _norm(value) in src:
        return True
    nums = _numbers(value)
    return bool(nums) and all(n in src_nums for n in nums)


def _name_present(name, src) -> bool:
    if not name:
        return True
    n = _norm(name)
    if n in src:
        return True
    first = n.split(" ")[0]
    return len(first) > 2 and first in src


def validate(result: dict, source_text: str) -> dict:
    src = _norm(source_text)
    src_nums = set(_numbers(source_text))
    checked = flagged = 0

    for med in result.get("medications", []):
        ok = _name_present(med.get("name"), src) and _present(med.get("dose_as_written"), src, src_nums)
        med["verified"] = ok
        checked += 1
        flagged += 0 if ok else 1

    for lab in result.get("lab_results", []):
        ok = (_name_present(lab.get("test"), src) and _present(lab.get("value"), src, src_nums)
              and _present(lab.get("reference_range_as_written"), src, src_nums))
        lab["verified"] = ok
        checked += 1
        flagged += 0 if ok else 1

    result["verification_summary"] = {"checked": checked, "flagged": flagged}
    return result
