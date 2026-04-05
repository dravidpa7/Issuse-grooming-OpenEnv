"""
Hard task: 61 issues across v2.6 and v3.0 milestones.
Includes security issues, cascading duplicates, conflicting community signals,
old stale items, and tricky borderline triage decisions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.models import Issue

HARD_ISSUES = [
    # === SECURITY (must be next_release) ===
    Issue(id=1, title="[SECURITY] Path traversal in file loader", body="The file loader does not sanitize paths. An attacker can pass `../../etc/passwd` as input and read arbitrary files. PoC attached. v2.5.0.", labels=["security", "bug"], author_type="maintainer", age_days=3, linked_prs=[]),
    Issue(id=2, title="Arbitrary code execution via eval() in expression parser", body="The expression parser uses eval() on user-supplied strings. This allows arbitrary Python execution. CVE pending. Please treat as critical.", labels=["security", "bug"], author_type="contributor", age_days=7, linked_prs=[50]),
    Issue(id=3, title="Path traversal - same as #1?", body="I think #1 covers this. Reporting for visibility: passing `../secret` to the loader reads outside working dir.", labels=["bug"], author_type="new_user", age_days=2, linked_prs=[]),

    # === V3.0 BREAKING CHANGES ===
    Issue(id=4, title="[v3.0] Remove deprecated parse_v1() function", body="parse_v1() was deprecated in v2.4. v3.0 is the right time to remove it. Track here.", labels=["v3.0", "breaking-change"], author_type="maintainer", age_days=40, linked_prs=[]),
    Issue(id=5, title="[v3.0] Rename `schema` param to `spec` across all APIs", body="Unify terminology: `schema` -> `spec`. Requires major version bump. Breaking change tracker.", labels=["v3.0", "breaking-change"], author_type="maintainer", age_days=38, linked_prs=[]),
    Issue(id=6, title="[v3.0] Drop Python 3.8 and 3.9 support", body="Python 3.8 EOL is Oct 2024. v3.0 should require Python 3.10+. Update CI matrix and classifiers.", labels=["v3.0", "maintenance"], author_type="maintainer", age_days=35, linked_prs=[]),

    # === BUGS - next_release ===
    Issue(id=7, title="Memory leak when parse() called 1000+ times in a loop", body="RSS grows by ~2MB per call in a tight loop. Profile attached. v2.5.1, Python 3.11, Linux.", labels=["bug", "memory"], author_type="contributor", age_days=10, linked_prs=[]),
    Issue(id=8, title="Wrong output for schemas with mutual exclusion constraints", body="If schema has `oneOf` with 3+ options, the parser selects the first matching option instead of the most specific. Reproducible test case attached.", labels=["bug"], author_type="contributor", age_days=15, linked_prs=[]),
    Issue(id=9, title="Race condition in thread pool executor", body="Using `process_parallel()` with 8+ workers causes occasional data corruption. Confirmed with -X dev and sanitizers. v2.5.0.", labels=["bug", "concurrency"], author_type="contributor", age_days=12, linked_prs=[]),
    Issue(id=10, title="Incorrect line number in ParseError for multiline strings", body="ParseError.lineno is off by the number of newlines in preceding multiline strings. Off-by-N bug.", labels=["bug"], author_type="contributor", age_days=18, linked_prs=[51]),
    Issue(id=11, title="StreamParser does not flush on context manager exit", body="Using `with StreamParser(...) as p:` — final chunk is not flushed if the loop ends cleanly (no exception).", labels=["bug"], author_type="contributor", age_days=8, linked_prs=[]),
    Issue(id=12, title="Cache key collision for schemas with same hash but different structure", body="Two structurally different schemas can produce the same cache key. Results in incorrect cached output.", labels=["bug", "cache"], author_type="contributor", age_days=22, linked_prs=[]),

    # === DUPLICATE CLUSTER: memory leak (13 dupes 7) ===
    Issue(id=13, title="Memory usage grows unbounded in batch processing", body="Similar to a memory leak issue I saw. RSS keeps growing. Running v2.5.1.", labels=["bug", "memory"], author_type="new_user", age_days=4, linked_prs=[]),

    # === NEED INFO ===
    Issue(id=14, title="Fails on my data", body="The parser fails on my data files. Please fix.", labels=[], author_type="new_user", age_days=6, linked_prs=[]),
    Issue(id=15, title="Weird behavior with unicode", body="Unicode doesn't work right sometimes. Hard to describe exactly.", labels=["bug"], author_type="new_user", age_days=20, linked_prs=[]),
    Issue(id=16, title="Intermittent timeout in CI", body="Our CI job times out sometimes. Not sure if it's the library or our infra. Python 3.10.", labels=["ci"], author_type="contributor", age_days=14, linked_prs=[]),

    # === CLOSE ===
    Issue(id=17, title="Please support Python 2.7", body="We have a large Python 2 codebase. Please don't drop Python 2 support.", labels=["enhancement"], author_type="new_user", age_days=300, linked_prs=[]),
    Issue(id=18, title="Build a web UI", body="It would be amazing to have a web interface to use this library without coding.", labels=["enhancement"], author_type="new_user", age_days=150, linked_prs=[]),
    Issue(id=19, title="Make the library use less memory (no details)", body="Memory seems high but I have no numbers.", labels=["performance"], author_type="new_user", age_days=80, linked_prs=[]),
    Issue(id=20, title="Stale: support PostgreSQL backend", body="Asked a year ago, no response, closing if no interest.", labels=["question"], author_type="new_user", age_days=400, linked_prs=[]),

    # === ENHANCEMENTS - backlog ===
    Issue(id=21, title="Support streaming output for large result sets", body="Currently all output is buffered. Streaming would reduce peak memory for large files.", labels=["enhancement", "performance"], author_type="contributor", age_days=30, linked_prs=[]),
    Issue(id=22, title="Add JSON Schema draft 2020-12 support", body="Currently supports draft-07. Draft 2020-12 has new keywords (prefixItems, unevaluatedItems). Tracking issue.", labels=["enhancement"], author_type="contributor", age_days=60, linked_prs=[]),
    Issue(id=23, title="Plugin system for custom validators", body="Allow third-party validators to be registered and run as part of the validation pipeline.", labels=["enhancement", "architecture"], author_type="contributor", age_days=55, linked_prs=[]),
    Issue(id=24, title="Add CLI interface", body="A CLI would let users run the parser from shell scripts without writing Python.", labels=["enhancement"], author_type="contributor", age_days=45, linked_prs=[]),
    Issue(id=25, title="Async API for parse() and validate()", body="Async versions of main functions for use in FastAPI / asyncio applications.", labels=["enhancement", "async"], author_type="contributor", age_days=50, linked_prs=[]),

    # === ENHANCEMENTS - next_release ===
    Issue(id=26, title="Improve error messages: include path to failing node", body="Error messages show the failing key but not the full JSON path. Adding the path would halve debugging time.", labels=["enhancement", "ux"], author_type="contributor", age_days=25, linked_prs=[]),
    Issue(id=27, title="Add .pyi type stubs for mypy", body="No type stubs exist. mypy treats everything as Any. PR welcome if we can agree on the shape.", labels=["enhancement", "typing"], author_type="contributor", age_days=28, linked_prs=[52]),

    # === OPEN PRs (keep, next_release) ===
    Issue(id=50, title="PR: Fix eval() usage in expression parser", body="Replaces eval() with a safe AST-based evaluator. Resolves #2.", labels=["security"], author_type="contributor", age_days=6, linked_prs=[], is_pr=True),
    Issue(id=51, title="PR: Fix line number offset in ParseError", body="Fixes off-by-N lineno bug. Resolves #10.", labels=["bug"], author_type="contributor", age_days=16, linked_prs=[], is_pr=True),
    Issue(id=52, title="PR: Add .pyi type stubs", body="Initial .pyi stubs for all public API. Resolves #27.", labels=["enhancement"], author_type="contributor", age_days=20, linked_prs=[], is_pr=True),

    # === MORE BUGS - mixed priority ===
    Issue(id=28, title="validate() returns True for schemas with unknown keywords (strict mode off by default)", body="Unknown keywords in schema are silently ignored even when strict=True is passed. Regression in v2.5.", labels=["bug"], author_type="contributor", age_days=11, linked_prs=[]),
    Issue(id=29, title="Encoding detection wrong for latin-1 files", body="Files with latin-1 encoding are misdetected as utf-8, causing mojibake in output. v2.5.1.", labels=["bug"], author_type="contributor", age_days=16, linked_prs=[]),
    Issue(id=30, title="PR stale: async refactor from 2022", body="This PR was opened 2 years ago, has merge conflicts, and the author hasn't responded to review comments for 18 months.", labels=["stale"], author_type="contributor", age_days=730, linked_prs=[], is_pr=True),

    # === DUPLICATE CLUSTER: encoding (31 dupes 29) ===
    Issue(id=31, title="Latin-1 / ISO-8859-1 files not parsed correctly", body="Same bug as someone else reported — latin-1 files come out garbled. v2.5.1.", labels=["bug"], author_type="new_user", age_days=5, linked_prs=[]),

    # === MAINTENANCE ===
    Issue(id=32, title="Update dependencies: pydantic v2 compatibility", body="We currently pin pydantic<2. v2 has breaking changes but is widely adopted. Need a migration plan.", labels=["maintenance", "dependencies"], author_type="maintainer", age_days=30, linked_prs=[]),
    Issue(id=33, title="Set up automated security scanning (Bandit / Snyk)", body="No SAST tooling in CI. Given recent security issues (#1, #2) this is urgent.", labels=["security", "ci"], author_type="maintainer", age_days=4, linked_prs=[]),

    # === WONT FIX ===
    Issue(id=34, title="Support XML output format", body="The library is JSON-focused. XML output is out of scope per the project charter.", labels=["enhancement"], author_type="new_user", age_days=200, linked_prs=[]),
    Issue(id=35, title="Rewrite in Rust for 10x speed", body="Rewriting in Rust would make this much faster. Python is slow.", labels=["enhancement"], author_type="new_user", age_days=100, linked_prs=[]),

    # === MORE NEED INFO ===
    Issue(id=36, title="Error when using with pandas DataFrames", body="I'm trying to use this with pandas but get an error. I can't share the full stack trace due to company policy.", labels=["question"], author_type="new_user", age_days=9, linked_prs=[]),
    Issue(id=37, title="Inconsistent results on Windows vs Linux", body="Same input produces different output on Windows 11 vs Ubuntu 22. Couldn't narrow it down further.", labels=["bug"], author_type="contributor", age_days=25, linked_prs=[]),

    # === DUPLICATE CLUSTER: strict mode (38 dupes 28) ===
    Issue(id=38, title="strict=True doesn't reject unknown schema keywords", body="Setting strict=True still allows unknown keywords. Seems like the flag is ignored?", labels=["bug"], author_type="new_user", age_days=3, linked_prs=[]),

    # === V3.0 BACKLOG ===
    Issue(id=39, title="[v3.0] New event-based API for incremental parsing", body="Design and implement an event-based API (SAX-style) for incremental processing. Long-horizon feature.", labels=["v3.0", "enhancement"], author_type="maintainer", age_days=50, linked_prs=[]),
    Issue(id=40, title="[v3.0] Formal specification document", body="Write a formal spec for the schema language to stabilize semantics before v3.0.", labels=["v3.0", "documentation"], author_type="maintainer", age_days=45, linked_prs=[]),

    # === ADDITIONAL BUGS - next_release ===
    Issue(id=41, title="Null byte in input causes silent data loss", body="If the input contains a null byte (\\x00), the parser silently drops everything after it. Should raise an error.", labels=["bug"], author_type="contributor", age_days=13, linked_prs=[]),
    Issue(id=42, title="setup.py still present alongside pyproject.toml", body="We migrated to pyproject.toml but setup.py is still there and causes confusion. Remove it.", labels=["maintenance"], author_type="contributor", age_days=20, linked_prs=[]),

    # === COMMUNITY CONFLICT: feature request with both upvotes and objections ===
    Issue(id=43, title="Add global mutable config singleton", body="A global config object would simplify setup. 20 upvotes. BUT: several contributors argue this is an anti-pattern that breaks thread safety.", labels=["enhancement", "api"], author_type="contributor", age_days=55, linked_prs=[]),

    # === ENHANCEMENTS - clear backlog ===
    Issue(id=44, title="Support TOML config files", body="TOML is increasingly popular (PEP 518). Supporting it alongside JSON and YAML would be useful.", labels=["enhancement"], author_type="contributor", age_days=40, linked_prs=[]),
    Issue(id=45, title="Add benchmarks to CI", body="No formal benchmarks exist. Adding a benchmark suite would catch performance regressions automatically.", labels=["ci", "performance"], author_type="contributor", age_days=35, linked_prs=[]),

    # === STALE / CLOSE ===
    Issue(id=46, title="Question from 2021: what is the roadmap?", body="Asked about roadmap 3 years ago. No response. Closing.", labels=["question"], author_type="new_user", age_days=1095, linked_prs=[]),
    Issue(id=47, title="Is this project abandoned?", body="No commits in 6 months. Are you still maintaining this?", labels=["question"], author_type="new_user", age_days=60, linked_prs=[]),

    # === DUPLICATE CLUSTER: cache collision (48 dupes 12) ===
    Issue(id=48, title="Getting wrong cached results for different schemas", body="Looks like there's a cache bug — different schemas return the same cached output. v2.5.", labels=["bug", "cache"], author_type="contributor", age_days=8, linked_prs=[]),

    # === TRICKY BORDERLINE ===
    Issue(id=49, title="Deprecation warning in Python 3.12 from datetime.utcnow()", body="Python 3.12 emits DeprecationWarning for datetime.utcnow() which we use internally. Low severity but noisy for users.", labels=["maintenance"], author_type="contributor", age_days=21, linked_prs=[]),

    # === ADDITIONAL ENHANCEMENTS ===
    Issue(id=53, title="Support for custom error formatters", body="Allow users to plug in custom error formatting so they can control error message style.", labels=["enhancement"], author_type="contributor", age_days=33, linked_prs=[]),
    Issue(id=54, title="Add examples directory with real-world schemas", body="The repo lacks practical examples. An examples/ folder with 5-10 real schemas would help new users.", labels=["documentation"], author_type="contributor", age_days=28, linked_prs=[]),
    Issue(id=55, title="Wrong boolean coercion: '0' should not be falsy", body="The string '0' is being coerced to False when type is boolean. Should raise a type error instead.", labels=["bug"], author_type="contributor", age_days=17, linked_prs=[]),
    Issue(id=56, title="[v3.0] Remove undocumented _internal_parse() from public namespace", body="_internal_parse() is accessible but undocumented. It should be moved to a private module in v3.0.", labels=["v3.0", "maintenance"], author_type="maintainer", age_days=42, linked_prs=[]),
    Issue(id=57, title="Logging output goes to stdout instead of stderr", body="Library log messages pollute stdout. Should use stderr or a named logger that users can silence.", labels=["bug", "ux"], author_type="contributor", age_days=19, linked_prs=[]),
    Issue(id=58, title="make it work with django", body="need django support", labels=[], author_type="new_user", age_days=90, linked_prs=[]),
    Issue(id=59, title="Duplicate: memory grows in batch", body="Already reported but just in case: memory grows when processing many files. v2.5.1.", labels=["bug"], author_type="new_user", age_days=1, linked_prs=[]),
    Issue(id=60, title="Docs: API reference out of date with v2.5 changes", body="Several v2.5 API changes are not reflected in the API reference docs. Confusing for new users.", labels=["documentation"], author_type="contributor", age_days=24, linked_prs=[]),
    Issue(id=61, title="Add SECURITY.md policy file", body="No SECURITY.md in the repo. GitHub recommends it for responsible disclosure. Quick add.", labels=["security", "documentation"], author_type="contributor", age_days=5, linked_prs=[]),
]

HARD_GROUND_TRUTH = {
    1:  {"triage": "keep",      "priority": "next_release"},
    2:  {"triage": "keep",      "priority": "next_release"},
    3:  {"triage": "duplicate", "duplicate_of": 1},
    4:  {"triage": "keep",      "priority": "next_release"},
    5:  {"triage": "keep",      "priority": "next_release"},
    6:  {"triage": "keep",      "priority": "next_release"},
    7:  {"triage": "keep",      "priority": "next_release"},
    8:  {"triage": "keep",      "priority": "next_release"},
    9:  {"triage": "keep",      "priority": "next_release"},
    10: {"triage": "keep",      "priority": "next_release"},
    11: {"triage": "keep",      "priority": "next_release"},
    12: {"triage": "keep",      "priority": "next_release"},
    13: {"triage": "duplicate", "duplicate_of": 7},
    14: {"triage": "need-info"},
    15: {"triage": "need-info"},
    16: {"triage": "need-info"},
    17: {"triage": "close"},
    18: {"triage": "close"},
    19: {"triage": "close"},
    20: {"triage": "close"},
    21: {"triage": "keep",      "priority": "backlog"},
    22: {"triage": "keep",      "priority": "backlog"},
    23: {"triage": "keep",      "priority": "backlog"},
    24: {"triage": "keep",      "priority": "backlog"},
    25: {"triage": "keep",      "priority": "backlog"},
    26: {"triage": "keep",      "priority": "next_release"},
    27: {"triage": "keep",      "priority": "next_release"},
    28: {"triage": "keep",      "priority": "next_release"},
    29: {"triage": "keep",      "priority": "next_release"},
    30: {"triage": "close"},
    31: {"triage": "duplicate", "duplicate_of": 29},
    32: {"triage": "keep",      "priority": "next_release"},
    33: {"triage": "keep",      "priority": "next_release"},
    34: {"triage": "close"},
    35: {"triage": "close"},
    36: {"triage": "need-info"},
    37: {"triage": "need-info"},
    38: {"triage": "duplicate", "duplicate_of": 28},
    39: {"triage": "keep",      "priority": "backlog"},
    40: {"triage": "keep",      "priority": "backlog"},
    41: {"triage": "keep",      "priority": "next_release"},
    42: {"triage": "keep",      "priority": "next_release"},
    43: {"triage": "keep",      "priority": "backlog"},
    44: {"triage": "keep",      "priority": "backlog"},
    45: {"triage": "keep",      "priority": "backlog"},
    46: {"triage": "close"},
    47: {"triage": "close"},
    48: {"triage": "duplicate", "duplicate_of": 12},
    49: {"triage": "keep",      "priority": "next_release"},
    50: {"triage": "keep",      "priority": "next_release"},
    51: {"triage": "keep",      "priority": "next_release"},
    52: {"triage": "keep",      "priority": "next_release"},
    53: {"triage": "keep",      "priority": "backlog"},
    54: {"triage": "keep",      "priority": "backlog"},
    55: {"triage": "keep",      "priority": "next_release"},
    56: {"triage": "keep",      "priority": "next_release"},
    57: {"triage": "keep",      "priority": "next_release"},
    58: {"triage": "close"},
    59: {"triage": "duplicate", "duplicate_of": 7},
    60: {"triage": "keep",      "priority": "next_release"},
    61: {"triage": "keep",      "priority": "next_release"},
}
