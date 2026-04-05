"""
Easy task: 10 synthetic issues with clear labels and one obvious duplicate pair.
Issues 3 and 7 are duplicates (both report the same KeyError on empty input).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.models import Issue

EASY_ISSUES = [
    Issue(
        id=1,
        title="Add support for Python 3.12",
        body="Python 3.12 was released. Our CI still tests on 3.11. We should add 3.12 to the matrix and fix any deprecation warnings.",
        labels=["enhancement", "ci"],
        author_type="contributor",
        age_days=14,
        linked_prs=[],
    ),
    Issue(
        id=2,
        title="KeyError when passing empty dict to parse()",
        body="Steps to reproduce:\n1. Call `parse({})`\n2. See `KeyError: 'items'`\n\nOS: Ubuntu 22.04, Python 3.11, lib v1.4.0",
        labels=["bug"],
        author_type="new_user",
        age_days=5,
        linked_prs=[],
    ),
    Issue(
        id=3,
        title="Crash on empty input to parse function",
        body="When I pass an empty dictionary to `parse()`, I get a `KeyError`. This is a bug.\nVersion: 1.4.0, Python 3.10",
        labels=["bug"],
        author_type="new_user",
        age_days=3,
        linked_prs=[],
    ),
    Issue(
        id=4,
        title="Add GUI interface",
        body="It would be great to have a graphical user interface so non-technical users can use the library without writing code.",
        labels=["enhancement"],
        author_type="new_user",
        age_days=120,
        linked_prs=[],
    ),
    Issue(
        id=5,
        title="Documentation typo in README",
        body="Line 42 in README.md says 'recieve' but it should be 'receive'. Small fix.",
        labels=["documentation"],
        author_type="contributor",
        age_days=2,
        linked_prs=[12],
    ),
    Issue(
        id=6,
        title="Performance regression in v1.4.0 for large files",
        body="Processing a 50 MB file now takes 12s on v1.4.0 vs 3s on v1.3.0. Profiling shows the bottleneck is in `_tokenize()`. Reproducible on macOS 13 and Linux.",
        labels=["bug", "performance"],
        author_type="contributor",
        age_days=8,
        linked_prs=[],
    ),
    Issue(
        id=7,
        title="parse({}) throws KeyError",
        body="Bug: calling `parse` with an empty dict raises `KeyError: 'items'`. Please fix.",
        labels=["bug"],
        author_type="new_user",
        age_days=1,
        linked_prs=[],
    ),
    Issue(
        id=8,
        title="Support async/await API",
        body="It would be useful to have async versions of the main parse and render functions so we can use them in async web frameworks.",
        labels=["enhancement", "api"],
        author_type="contributor",
        age_days=45,
        linked_prs=[],
    ),
    Issue(
        id=9,
        title="TypeError when input contains None values",
        body="Not sure if this is expected behavior but passing None as a value causes a TypeError deep in the stack. Is this supposed to raise a nicer error?",
        labels=["question"],
        author_type="new_user",
        age_days=10,
        linked_prs=[],
    ),
    Issue(
        id=10,
        title="Add Python 2 support",
        body="Please add support for Python 2.7. Some of us are on legacy systems and cannot upgrade.",
        labels=["enhancement"],
        author_type="new_user",
        age_days=90,
        linked_prs=[],
    ),
]

# Ground truth label set
EASY_GROUND_TRUTH = {
    1:  {"triage": "keep",      "priority": "backlog"},
    2:  {"triage": "keep",      "priority": "next_release"},
    3:  {"triage": "duplicate", "duplicate_of": 2},
    4:  {"triage": "close"},
    5:  {"triage": "keep",      "priority": "next_release"},
    6:  {"triage": "keep",      "priority": "next_release"},
    7:  {"triage": "duplicate", "duplicate_of": 2},
    8:  {"triage": "keep",      "priority": "backlog"},
    9:  {"triage": "need-info"},
    10: {"triage": "close"},
}
