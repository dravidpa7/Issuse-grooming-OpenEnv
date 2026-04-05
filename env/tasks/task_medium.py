"""
Medium task: 30 issues with noisy descriptions, borderline cases,
multiple duplicate clusters, and stale items.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.models import Issue

MEDIUM_ISSUES = [
    # -- Bug cluster: unicode handling (1, 8 are dupes of 1) --
    Issue(id=1, title="UnicodeDecodeError on files with BOM", body="When loading UTF-8 files that start with a BOM character, I get UnicodeDecodeError. Python 3.11, Windows 10, v1.5.2.", labels=["bug"], author_type="contributor", age_days=12, linked_prs=[]),
    Issue(id=2, title="Feature: export to CSV", body="It would be helpful to export results directly to CSV format without converting manually.", labels=["enhancement"], author_type="new_user", age_days=60, linked_prs=[]),
    Issue(id=3, title="Segfault on Python 3.11 with large files", body="I get a segfault when processing files above 200MB. This is consistent on Linux x86_64.", labels=["bug", "crash"], author_type="contributor", age_days=20, linked_prs=[]),
    Issue(id=4, title="Docs: missing return type annotations", body="Many public functions lack return type hints in the docstrings. Makes IDE support worse.", labels=["documentation"], author_type="contributor", age_days=30, linked_prs=[22]),
    Issue(id=5, title="please add dark mode", body="dark mode would be nice", labels=[], author_type="new_user", age_days=180, linked_prs=[]),
    Issue(id=6, title="ValueError when schema has circular references", body="If the schema dict contains a key that references itself, we get infinite recursion and a ValueError. Steps: create schema with `s['a'] = s`. Version 1.5.0.", labels=["bug"], author_type="contributor", age_days=7, linked_prs=[]),
    Issue(id=7, title="Add plugin architecture", body="It would be nice to support third-party plugins so users can extend the parser without forking.", labels=["enhancement", "architecture"], author_type="contributor", age_days=90, linked_prs=[]),
    Issue(id=8, title="BOM in UTF-8 files causes crash", body="UTF-8 BOM at start of file throws UnicodeDecodeError. Confirmed on v1.5.2 Windows.", labels=["bug"], author_type="new_user", age_days=5, linked_prs=[]),
    Issue(id=9, title="CI fails on Windows intermittently", body="The GitHub Actions CI workflow fails maybe 1 in 5 runs on the Windows runner with a timeout. Not deterministic. Could be a flaky test.", labels=["ci", "flaky"], author_type="contributor", age_days=15, linked_prs=[]),
    Issue(id=10, title="Support for YAML config files", body="Allow loading configuration from YAML files in addition to the current JSON-only support.", labels=["enhancement"], author_type="contributor", age_days=45, linked_prs=[]),
    # -- Need info cluster --
    Issue(id=11, title="it doesn't work on my machine", body="the library doesn't work", labels=[], author_type="new_user", age_days=3, linked_prs=[]),
    Issue(id=12, title="Performance slower on v1.5", body="Things feel slower but I haven't benchmarked. Just a feeling from everyday use.", labels=["performance"], author_type="new_user", age_days=22, linked_prs=[]),
    Issue(id=13, title="Memory leak when processing many files in a loop", body="After processing ~500 files in a loop, RAM usage climbs to 4GB and doesn't drop. Reproducible with the attached script on Python 3.10, Linux, v1.5.1.", labels=["bug", "memory"], author_type="contributor", age_days=18, linked_prs=[]),
    Issue(id=14, title="Add support for Python 2", body="We need Python 2.7 compatibility for our legacy codebase.", labels=["enhancement"], author_type="new_user", age_days=200, linked_prs=[]),
    Issue(id=15, title="make it faster", body="can you make the library faster please", labels=[], author_type="new_user", age_days=50, linked_prs=[]),
    # -- Bug cluster: config loading (16, 21 are dupes of 16) --
    Issue(id=16, title="Config file not loaded when path contains spaces", body="Passing a config file path with spaces in the directory name causes a FileNotFoundError even when the file exists. Reproducible on all platforms. v1.5.2.", labels=["bug"], author_type="contributor", age_days=9, linked_prs=[]),
    Issue(id=17, title="Expose internal tokenizer API", body="The `_tokenize` function is useful but marked private. Could it be made part of the public API?", labels=["enhancement", "api"], author_type="contributor", age_days=35, linked_prs=[]),
    Issue(id=18, title="KeyError in nested schema validation", body="When validating a schema with 3+ levels of nesting, intermittent KeyError occurs. Hard to reproduce consistently — happens about 1 in 10 runs.", labels=["bug"], author_type="contributor", age_days=14, linked_prs=[]),
    Issue(id=19, title="Incorrect output for schemas with optional fields", body="Optional fields marked with `?` are sometimes included in output when they should be absent. Full reproduction in the attached test case. v1.5.1.", labels=["bug"], author_type="contributor", age_days=11, linked_prs=[23]),
    Issue(id=20, title="Add type stubs (.pyi files)", body="Provide .pyi stub files for better mypy and pyright integration.", labels=["enhancement", "typing"], author_type="contributor", age_days=40, linked_prs=[]),
    Issue(id=21, title="FileNotFoundError when config path has spaces", body="Same as another issue I saw — config path with spaces breaks. v1.5.2.", labels=["bug"], author_type="new_user", age_days=2, linked_prs=[]),
    Issue(id=22, title="PR: Add return type annotations to public API", body="Adds return type hints to all public functions. Resolves #4.", labels=["documentation"], author_type="contributor", age_days=28, linked_prs=[], is_pr=True),
    Issue(id=23, title="PR: Fix optional field exclusion bug", body="Fixes incorrect output for optional fields. Resolves #19.", labels=["bug"], author_type="contributor", age_days=10, linked_prs=[], is_pr=True),
    Issue(id=24, title="Misleading error message for invalid schema type", body="When passing a string where a dict is expected, error says 'internal error' instead of something useful. Simple fix with better isinstance check.", labels=["bug", "ux"], author_type="contributor", age_days=6, linked_prs=[]),
    Issue(id=25, title="Support environment variable interpolation in config", body="Allow `${ENV_VAR}` syntax in config files so users don't have to hardcode secrets.", labels=["enhancement"], author_type="contributor", age_days=55, linked_prs=[]),
    Issue(id=26, title="Thread safety issues in v1.5", body="Using the parser from multiple threads causes occasional data corruption. Confirmed with threading.Thread and multiprocessing. v1.5.2.", labels=["bug", "concurrency"], author_type="contributor", age_days=16, linked_prs=[]),
    Issue(id=27, title="stale: timezone support?", body="Any plans for timezone-aware datetime parsing? Asked a year ago with no response.", labels=["question"], author_type="new_user", age_days=365, linked_prs=[]),
    Issue(id=28, title="Deprecate legacy `parse_v1()` function", body="The `parse_v1()` function has been superseded by `parse()`. Should be formally deprecated with a warning and removed in v2.", labels=["maintenance"], author_type="maintainer", age_days=25, linked_prs=[]),
    Issue(id=29, title="Wrong line numbers in error messages", body="When validation fails, the line numbers reported in error messages are off by one. This makes debugging unnecessarily hard. Confirmed in v1.5.0 and v1.5.2.", labels=["bug"], author_type="contributor", age_days=19, linked_prs=[]),
    Issue(id=30, title="Add changelog to releases", body="GitHub releases have no changelog. Would be helpful to list what changed between versions.", labels=["documentation", "maintenance"], author_type="contributor", age_days=70, linked_prs=[]),
]

MEDIUM_GROUND_TRUTH = {
    1:  {"triage": "keep",      "priority": "next_release"},
    2:  {"triage": "keep",      "priority": "backlog"},
    3:  {"triage": "keep",      "priority": "next_release"},
    4:  {"triage": "keep",      "priority": "next_release"},
    5:  {"triage": "close"},
    6:  {"triage": "keep",      "priority": "next_release"},
    7:  {"triage": "keep",      "priority": "backlog"},
    8:  {"triage": "duplicate", "duplicate_of": 1},
    9:  {"triage": "need-info"},
    10: {"triage": "keep",      "priority": "backlog"},
    11: {"triage": "need-info"},
    12: {"triage": "need-info"},
    13: {"triage": "keep",      "priority": "next_release"},
    14: {"triage": "close"},
    15: {"triage": "need-info"},
    16: {"triage": "keep",      "priority": "next_release"},
    17: {"triage": "keep",      "priority": "backlog"},
    18: {"triage": "need-info"},
    19: {"triage": "keep",      "priority": "next_release"},
    20: {"triage": "keep",      "priority": "backlog"},
    21: {"triage": "duplicate", "duplicate_of": 16},
    22: {"triage": "keep",      "priority": "next_release"},
    23: {"triage": "keep",      "priority": "next_release"},
    24: {"triage": "keep",      "priority": "next_release"},
    25: {"triage": "keep",      "priority": "backlog"},
    26: {"triage": "keep",      "priority": "next_release"},
    27: {"triage": "close"},
    28: {"triage": "keep",      "priority": "next_release"},
    29: {"triage": "keep",      "priority": "next_release"},
    30: {"triage": "keep",      "priority": "backlog"},
}
