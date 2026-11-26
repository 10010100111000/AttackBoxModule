#!/usr/bin/env python3
"""Validate the Web curriculum and granular topic matrix using Python stdlib."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    matrix = read_json("catalog/web-competencies.json")
    catalog = read_json("catalog/web-curriculum.json")

    groups = Counter(t["academy_group"] for t in matrix["topics"])
    topic_names = [t["id"] for t in matrix["topics"]]
    need(len(topic_names) == len(set(topic_names)), "duplicate Academy topic ID")
    need(groups == matrix["topic_counts"], "incorrect Academy group totals")
    need(len(topic_names) == 31, "expected snapshot of 31 Academy topics")

    levels = {"beginner", "intermediate", "advanced"}
    skill_ids: set[str] = set()
    for topic in matrix["topics"]:
        need(topic.get("source_url", "").startswith("https://portswigger.net/"),
             f"missing official source for {topic['id']}")
        for skill in topic["skills"]:
            name = skill["id"]
            need(name.startswith(topic["id"] + "."), f"invalid prefix: {name}")
            need(name not in skill_ids, f"duplicate skill ID: {name}")
            need(skill["first_target_level"] in levels, f"invalid level for {name}")
            skill_ids.add(name)

    need(catalog["schema_version"] >= 2, "outdated machine catalog schema")
    need(catalog["skills_catalog"] == "catalog/web-competencies.json",
         "machine catalog points to the wrong skill matrix")
    need(catalog["academy_index"]["official_topics"] == len(topic_names),
         "catalog topic count mismatch")
    need(catalog["academy_index"]["learning_objectives"] == len(skill_ids),
         "catalog skill count mismatch")
    need(set(catalog["academy_index"]["topic_ids"]) == set(topic_names),
         "catalog Academy topic ID mismatch")

    policy = catalog.get("verification_policy", {})
    need(policy.get("automation") == "build_startup_health_structure_and_lab_specific_e2e",
         "CI policy must include per-Lab end-to-end acceptance")
    need(policy.get("automated_exploitation") is True,
         "per-Lab CI must exercise the real intended vulnerability path")
    need(policy.get("full_flow") == "per_lab_automated_acceptance",
         "full lab flow must be covered by a Lab-specific automated player")
    need(policy.get("end_to_end_acceptance") == "isolated_network_client_real_vulnerable_component_and_exact_flag",
         "end-to-end acceptance must use an isolated network client and verify the exact Flag")

    category_ids = {x["id"] for x in catalog["categories"]}
    need(set(topic_names) <= category_ids, "missing Academy topic from machine categories")
    machine_ids: set[str] = set()
    for machine in catalog["machines"]:
        name = machine["id"]
        need(name not in machine_ids, f"duplicate machine: {name}")
        machine_ids.add(name)
        manual = machine.get("manual_validation", {})
        need(manual.get("status") in {"not_reviewed", "in_progress", "passed", "failed"},
             f"{name}: invalid manual acceptance status")
        if manual["status"] == "passed":
            need(all(manual.get(k) for k in ("commit", "reviewer", "reviewed_at", "scope", "evidence")),
                 f"{name}: manual pass needs actual acceptance evidence")
        if manual["status"] == "failed":
            need(bool(manual.get("failure_reason")),
                 f"{name}: failed manual acceptance needs a reason")
        need(machine["primary_category"] in category_ids,
             f"{name}: unknown primary category")
        need(all(c in category_ids for c in machine["secondary_categories"]),
             f"{name}: unknown secondary category")
        need(machine.get("variant_profile", {}).get("incremental_learning_value"),
             f"{name}: missing scenario difference description")
        need((ROOT / machine["path"] / "Dockerfile").is_file(),
             f"{name}: no Dockerfile at declared path")
        need(machine["lab_ci_status"] in {"full_chain_ci", "partial", "unverified"},
             f"{name}: invalid CI status")
        e2e_status = machine.get("e2e_ci_status", "pending")
        need(e2e_status in {"pending", "configured", "passed", "failed"},
             f"{name}: invalid end-to-end CI status")
        e2e_workflow = machine.get("e2e_ci_workflow")
        if e2e_status in {"configured", "passed"}:
            need(isinstance(e2e_workflow, str) and e2e_workflow.startswith(".github/workflows/"),
                 f"{name}: configured end-to-end CI needs a workflow path")
            need((ROOT / e2e_workflow).is_file(),
                 f"{name}: configured end-to-end workflow does not exist")
        if e2e_status == "passed":
            need(machine.get("e2e_ci_evidence", "").startswith("https://github.com/"),
                 f"{name}: passed end-to-end CI needs a run URL")
            need(bool(machine.get("e2e_ci_commit")),
                 f"{name}: passed end-to-end CI needs a commit SHA")
        if e2e_status == "failed":
            need(bool(machine.get("e2e_ci_failure_reason")),
                 f"{name}: failed end-to-end CI needs a failure reason")
        need(machine["worker_status"] == "not_verified" or
             machine["worker_status"] == "verified",
             f"{name}: invalid Worker status")

    all_lab_dirs = {
        p.name for p in (ROOT / "labs").iterdir()
        if p.is_dir() and (p / "Dockerfile").is_file()
    }
    need(machine_ids == all_lab_dirs,
         f"machines and Dockerfile directories differ: {machine_ids ^ all_lab_dirs}")

    # The human-readable inventory is checked against the structured catalog.
    # This prevents stale machine counts, missing Labs, or outdated CI/release labels.
    inventory_path = ROOT / "docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md"
    need(inventory_path.is_file(), "missing current main Lab inventory")
    inventory = inventory_path.read_text(encoding="utf-8")
    need(f"**{len(machine_ids)} 台 Lab**" in inventory,
         "inventory Lab total does not match catalog")
    counts = Counter(machine["lab_ci_status"] for machine in catalog["machines"])
    for status, count in counts.items():
        pattern = rf"\| `{re.escape(status)}` \| {count} \|"
        need(re.search(pattern, inventory) is not None,
             f"inventory count for {status} does not match catalog ({count})")
    index_header = "## CI machine index"
    need(index_header in inventory, "inventory is missing the CI machine index")
    index = inventory.split(index_header, 1)[1].split("\n## ", 1)[0]
    row_pattern = re.compile(
        r"^\| `([a-z0-9-]+)` \| `(full_chain_ci|partial|unverified)` "
        r"\| `(blocked_by_marker|not_assessed)` \|$",
        re.MULTILINE,
    )
    inventory_rows = {
        lab_id: (ci_status, release_status)
        for lab_id, ci_status, release_status in row_pattern.findall(index)
    }
    expected_rows = {
        machine["id"]: (machine["lab_ci_status"], machine["release_status"])
        for machine in catalog["machines"]
    }
    missing_rows = set(expected_rows) - set(inventory_rows)
    extra_rows = set(inventory_rows) - set(expected_rows)
    changed_rows = {
        key for key in set(expected_rows) & set(inventory_rows)
        if expected_rows[key] != inventory_rows[key]
    }
    need(not (missing_rows or extra_rows or changed_rows),
         f"inventory machine index differs from catalog: missing={missing_rows}, "
         f"extra={extra_rows}, changed={changed_rows}")
    for machine in catalog["machines"]:
        marker_exists = (ROOT / machine["path"] / ".release-blocked").is_file()
        need(marker_exists == (machine["release_status"] == "blocked_by_marker"),
             f"{machine['id']}: release status does not match .release-blocked marker")

    candidates = catalog["candidate_shortlist"]
    candidates_by_id = {c["id"] for c in candidates}
    need(len(candidates) == len(candidates_by_id), "duplicate source candidate")
    for candidate in candidates:
        need(candidate["review_status"] in {"research_required", "source_verified",
             "feasible", "in_progress", "lab_ci_verified", "worker_verified"},
             f"invalid candidate status: {candidate['id']}")
        need(all(skill in skill_ids for skill in candidate["skills"]),
             f"unknown granular skill in source candidate {candidate['id']}")
        need(candidate["url"].startswith("https://"), "candidate missing HTTPS source")

    requirement_ids: set[str] = set()
    priorities: set[int] = set()
    for item in catalog["backlog"]:
        name = item["id"]
        need(name not in requirement_ids, f"duplicate backlog entry: {name}")
        requirement_ids.add(name)
        need(item["difficulty"] in levels, f"invalid difficulty: {name}")
        need(item["primary_category"] in category_ids,
             f"unknown requirement category: {name}")
        need(all(skill in skill_ids for skill in item["required_skill_coverage"]),
             f"unknown skill in backlog requirement: {name}")
        need(item["priority"] not in priorities, f"duplicate priority: {item['priority']}")
        priorities.add(item["priority"])
        need(item["status"] in {"planned", "in_progress", "done", "blocked"},
             f"invalid backlog status: {name}")
        for option in item.get("candidate_options", []):
            need(option in candidates_by_id or option in machine_ids,
                 f"{name}: unknown candidate reference {option}")

    for skill, associations in matrix.get("legacy_associations", {}).items():
        need(skill in skill_ids, f"unknown legacy skill: {skill}")
        need(all(a["lab"] in machine_ids for a in associations),
             f"missing machine in legacy associations for {skill}")
        need(all(a["skill_assertion_status"] == "requires_independent_audit"
                 for a in associations),
             f"legacy evidence wrongly marked as independently verified: {skill}")

    for path in ("README.md", "docs/WEB_LAB_DESIGN.md", "docs/EXISTING_WEB_LAB_RELEASE_INVENTORY.md"):
        need((ROOT / path).is_file(), f"missing curriculum documentation: {path}")

    print(f"PASS: {len(topic_names)} topics, {len(skill_ids)} skill objectives, "
          f"{len(machine_ids)} lab directories, {len(requirement_ids)} backlog requirements, "
          f"{len(candidates)} documented source candidates")
    print("PASS: category IDs, machine paths, skills, requirements, source refs and "
          "status separation are consistent")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f"CURRICULUM VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
