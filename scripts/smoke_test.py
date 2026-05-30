#!/usr/bin/env python3
"""
Live smoke test for the colacloud Python SDK.

Exercises each SDK resource against the production API to verify
end-to-end functionality: client init, request/response serialization,
Pydantic model parsing, pagination, and error handling.

Usage:
    COLA_API_KEY=... uv run python scripts/smoke_test.py
    COLA_API_KEY=... uv run python scripts/smoke_test.py --base-url http://localhost:5001/api/v1
"""

import argparse
import os
import sys
import time

results: list[tuple[bool, str]] = []


def format_total(total: int | None) -> str:
    """Format optional pagination totals returned by search-backed endpoints."""
    return str(total) if total is not None else "unknown"


def check(name: str, fn):
    """Run a single check. Calls fn(), expects it to return or raise."""
    start = time.monotonic()
    try:
        detail = fn()
        elapsed = time.monotonic() - start
        msg = f"  OK  {name} ({elapsed:.2f}s)"
        if detail:
            msg += f" — {detail}"
        results.append((True, msg))
        print(msg)
    except Exception as e:
        elapsed = time.monotonic() - start
        msg = f"FAIL  {name} — {type(e).__name__}: {e} ({elapsed:.2f}s)"
        results.append((False, msg))
        print(msg)


def main():
    parser = argparse.ArgumentParser(description="COLA Cloud Python SDK smoke test")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override API base URL (default: production)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("COLA_API_KEY")
    if not api_key:
        print("Error: COLA_API_KEY environment variable is required")
        sys.exit(1)

    from colacloud import ColaCloud

    kwargs = {"api_key": api_key}
    if args.base_url:
        kwargs["base_url"] = args.base_url

    client = ColaCloud(**kwargs)
    base = args.base_url or "https://app.colacloud.us/api/v1"
    print(f"Smoke testing colacloud Python SDK against {base}\n")

    # --- colas.list ---
    ttb_id = None

    def test_colas_list():
        nonlocal ttb_id
        resp = client.colas.list(per_page=1)
        assert resp.data, "expected at least one COLA"
        assert resp.pagination.page == 1, "expected page 1"
        assert resp.pagination.per_page == 1, "expected per_page 1"
        cola = resp.data[0]
        assert cola.ttb_id, "expected ttb_id on COLA"
        assert cola.brand_name, "expected brand_name on COLA"
        ttb_id = cola.ttb_id
        return f"total={format_total(resp.pagination.total)}, first={ttb_id}"

    check("colas.list(per_page=1)", test_colas_list)

    # --- colas.get ---
    def test_colas_get():
        if not ttb_id:
            return "skipped — no ttb_id from list"
        detail = client.colas.get(ttb_id)
        assert detail.ttb_id == ttb_id
        assert detail.product_type
        return f"ttb_id={detail.ttb_id}, type={detail.product_type}"

    check(f"colas.get({ttb_id})", test_colas_get)

    # --- colas.list with search ---
    def test_colas_search():
        resp = client.colas.list(q="bourbon", per_page=5)
        assert resp.data is not None
        return f"found {len(resp.data)} results"

    check('colas.list(q="bourbon")', test_colas_search)

    # --- colas.iterate (just take first item) ---
    def test_colas_iterate():
        for cola in client.colas.iterate(q="whiskey", per_page=5):
            assert cola.ttb_id
            return f"first={cola.ttb_id}"
        return "no results (unexpected)"

    check('colas.iterate(q="whiskey")', test_colas_iterate)

    # --- permittees.list ---
    permit_number = None

    def test_permittees_list():
        nonlocal permit_number
        resp = client.permittees.list(per_page=1)
        assert resp.data, "expected at least one permittee"
        p = resp.data[0]
        assert p.permit_number
        permit_number = p.permit_number
        return f"total={format_total(resp.pagination.total)}, first={permit_number}"

    check("permittees.list(per_page=1)", test_permittees_list)

    # --- permittees.get ---
    def test_permittees_get():
        if not permit_number:
            return "skipped — no permit_number from list"
        detail = client.permittees.get(permit_number)
        assert detail.permit_number == permit_number
        return f"permit={detail.permit_number}, company={detail.company_name}"

    check(f"permittees.get({permit_number})", test_permittees_get)

    # --- get_usage ---
    def test_usage():
        usage = client.get_usage()
        assert usage.tier
        assert usage.current_period
        assert usage.detail_views.limit >= 0
        assert usage.list_records.limit >= 0
        assert usage.per_minute_limit > 0
        return (
            f"tier={usage.tier}, "
            f"detail_views={usage.detail_views.used}/{usage.detail_views.limit}, "
            f"list_records={usage.list_records.used}/{usage.list_records.limit}"
        )

    check("get_usage()", test_usage)

    # --- quota_info ---
    def test_quota_info():
        info = client.quota_info
        if info is None:
            return "not returned by API"
        assert info.limit >= 0
        assert info.remaining >= 0
        return f"meter={info.meter}, limit={info.limit}, remaining={info.remaining}"

    check("quota_info", test_quota_info)

    # --- Summary ---
    client.close()
    total = len(results)
    passed = sum(1 for p, _ in results if p)
    failed = total - passed

    print(f"\n{'=' * 40}")
    print(f"  {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} failed")
    else:
        print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
