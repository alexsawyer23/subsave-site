#!/usr/bin/env python3
"""
audit_generator.py
-------------------

This script generates a simple subscription audit report from a list
of SaaS tools and their monthly costs.  It compares the current
spend against a curated pricing database of popular alternatives and
calculates potential savings.

Example usage:
    python audit_generator.py --subscriptions "Zoom=15.99, Notion=12, Figma=15" --output my_report.md

The output is a Markdown file containing a table with the current
service, your spend, a recommended alternative, the alternative cost
and the calculated savings.  If no cheaper alternative is known the
script still reports the current service and cost.

Note: The pricing database contained in this script is intentionally
limited.  For a more comprehensive audit, contribute additional
entries to the `PRICING_DATA` dictionary.
"""

import argparse
import sys
from datetime import date


# A minimal pricing database with known SaaS tools and their
# alternatives.  Keys are lowercase names.  Values are dicts with:
#   - cost: float (monthly price per user)
#   - currency: string ("USD" or "GBP")
#   - alternatives: list of dicts with keys name, cost, currency, and notes
PRICING_DATA = {
    "slack": {
        "cost": 8.75,
        "currency": "USD",
        "alternatives": [
            {"name": "Pumble Pro", "cost": 2.99, "currency": "USD",
             "notes": "Free plan available; cheaper paid plans"},
            {"name": "Microsoft Teams", "cost": 4.90, "currency": "GBP",
             "notes": "Business Basic plan; includes meetings"},
        ],
    },
    "microsoft teams": {
        "cost": 4.90,
        "currency": "GBP",
        "alternatives": [
            {"name": "Google Meet", "cost": 6.00, "currency": "USD",
             "notes": "Business Starter plan"},
        ],
    },
    "zoom": {
        "cost": 15.99,
        "currency": "USD",
        "alternatives": [
            {"name": "Google Meet", "cost": 6.00, "currency": "USD",
             "notes": "Business Starter plan"},
            {"name": "Microsoft Teams", "cost": 4.90, "currency": "GBP",
             "notes": "Business Basic plan"},
        ],
    },
    "notion": {
        "cost": 12.00,
        "currency": "USD",
        "alternatives": [
            {"name": "Focalboard", "cost": 0.00, "currency": "USD",
             "notes": "Free self-hosted project management"},
            {"name": "Obsidian", "cost": 0.00, "currency": "USD",
             "notes": "Free personal knowledge base (vault plugin)"},
        ],
    },
    "figma": {
        "cost": 15.00,
        "currency": "USD",
        "alternatives": [
            {"name": "Penpot", "cost": 0.00, "currency": "USD",
             "notes": "Open-source design tool"},
            {"name": "Canva", "cost": 12.99, "currency": "USD",
             "notes": "Pro plan"},
        ],
    },
    "adobe creative cloud": {
        "cost": 69.99,
        "currency": "USD",
        "alternatives": [
            {"name": "Affinity Universal License", "cost": 159.99/12, "currency": "GBP",
             "notes": "One‑time purchase for all Affinity apps"},
        ],
    },
    "quickbooks": {
        # QuickBooks Online Essentials plan (new price effective July 1, 2025
        # costs $75/month according to accounting advisory firm BCS【606224556309300†L94-L104】.
        "cost": 75.00,
        "currency": "USD",
        "alternatives": [
            # Wave offers a Starter plan that is free and a Pro plan at $16/month with
            # additional features such as bank transaction auto‑importing【892198001393548†L74-L83】.
            {"name": "Wave Pro", "cost": 16.00, "currency": "USD",
             "notes": "Pro plan with bank auto‑import"},
            # Xero’s entry‑level Ignite plan costs £16 per month【745372906036378†L245-L264】.
            {"name": "Xero Ignite", "cost": 16.00, "currency": "GBP",
             "notes": "Ignite plan"},
        ],
    },
    # Trello’s Standard plan costs $6 per user per month when billed monthly【383806120500639†L220-L280】.
    "trello": {
        "cost": 6.00,
        "currency": "USD",
        "alternatives": [
            # Freedcamp Pro plan costs $2.49 per user per month when billed monthly【991088617711956†L59-L67】.
            {"name": "Freedcamp Pro", "cost": 2.49, "currency": "USD",
             "notes": "Pro plan billed monthly"},
            # Focalboard is an open‑source self‑hosted alternative with no licensing fees【149631424145758†L130-L140】.
            {"name": "Focalboard", "cost": 0.00, "currency": "USD",
             "notes": "Free, self‑hosted"},
        ],
    },
    # Asana’s Starter plan costs $13.49 per user per month when billed monthly【449487890005048†L900-L911】.
    "asana": {
        "cost": 13.49,
        "currency": "USD",
        "alternatives": [
            {"name": "Freedcamp Pro", "cost": 2.49, "currency": "USD",
             "notes": "Pro plan billed monthly"},
            {"name": "Trello Standard", "cost": 6.00, "currency": "USD",
             "notes": "Standard plan"},
        ],
    },
    # Freedcamp itself is inexpensive: Pro costs $2.49 per user/month【991088617711956†L59-L67】.
    "freedcamp": {
        "cost": 2.49,
        "currency": "USD",
        "alternatives": [
            {"name": "Focalboard", "cost": 0.00, "currency": "USD",
             "notes": "Free self‑hosted"},
            {"name": "Trello Standard", "cost": 6.00, "currency": "USD",
             "notes": "Standard plan"},
        ],
    },
    # Xero’s Grow plan is £33 per month【745372906036378†L245-L264】.
    "xero": {
        "cost": 33.00,
        "currency": "GBP",
        "alternatives": [
            {"name": "Wave Pro", "cost": 16.00, "currency": "USD",
             "notes": "Pro plan"},
            {"name": "QuickBooks Essentials", "cost": 75.00, "currency": "USD",
             "notes": "Updated 2025 price"},
        ],
    },
    # Additional tools can be added here
}


def parse_subscriptions(subs_str: str):
    """Parse a comma-separated list of `Name=cost` pairs into a list of tuples."""
    subscriptions = []
    for item in subs_str.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            print(f"Skipping malformed item: {item}", file=sys.stderr)
            continue
        name, cost_str = item.split('=', 1)
        name = name.strip()
        try:
            cost = float(cost_str)
        except ValueError:
            print(f"Invalid cost for {name}: {cost_str}", file=sys.stderr)
            continue
        subscriptions.append((name, cost))
    return subscriptions


def find_best_alternative(name: str, current_cost: float):
    """
    Given a subscription name and cost, return the best (cheapest) alternative.

    Returns a dict with the alternative name, cost, currency, notes and savings.
    If no alternative is cheaper or known, returns None.
    """
    key = name.lower()
    data = PRICING_DATA.get(key)
    if not data:
        return None
    best_alt = None
    for alt in data["alternatives"]:
        alt_cost = alt["cost"]
        # Compare costs in USD equivalent; assume 1 GBP = 1.2 USD for simplicity
        current_cost_usd = current_cost if data["currency"] == "USD" else current_cost * 1.2
        alt_cost_usd = alt_cost if alt["currency"] == "USD" else alt_cost * 1.2
        if alt_cost_usd < current_cost_usd:
            savings = current_cost_usd - alt_cost_usd
            if not best_alt or savings > best_alt["savings"]:
                best_alt = {
                    "name": alt["name"],
                    "cost": alt_cost,
                    "currency": alt["currency"],
                    "notes": alt.get("notes", ""),
                    "savings": savings,
                }
    return best_alt


def generate_report(subscriptions, output_file=None):
    """Generate a Markdown report given a list of subscription tuples."""
    today = date.today().isoformat()
    lines = []
    lines.append(f"# Subscription Audit Report\n\nDate: {today}\n")
    lines.append("This report summarises your current subscription spend and suggests cheaper alternatives where available.\n")
    lines.append("| Current Tool | Your Cost (monthly) | Recommended Alternative | Alt Cost | Savings | Notes |\n")
    lines.append("| --- | --- | --- | --- | --- | --- |\n")
    total_savings = 0.0
    for name, cost in subscriptions:
        alt = find_best_alternative(name, cost)
        if alt:
            savings = alt["savings"]
            total_savings += savings
            alt_name = alt["name"]
            alt_cost = f"{alt['currency']} {alt['cost']:.2f}"
            savings_str = f"$ {savings:.2f}"
            notes = alt["notes"]
        else:
            alt_name = "—"
            alt_cost = "—"
            savings_str = "$ 0.00"
            notes = "No cheaper alternative found"
        lines.append(f"| {name} | $ {cost:.2f} | {alt_name} | {alt_cost} | {savings_str} | {notes} |\n")
    lines.append(f"\n**Total potential monthly savings: $ {total_savings:.2f}**\n")
    report_text = "".join(lines)
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
    return report_text


def main():
    parser = argparse.ArgumentParser(description="Generate a subscription audit report.")
    parser.add_argument("--subscriptions", type=str, required=True,
                        help="Comma-separated list of Name=cost pairs (monthly cost)")
    parser.add_argument("--output", type=str, help="Output Markdown file (optional)")
    args = parser.parse_args()
    subs = parse_subscriptions(args.subscriptions)
    if not subs:
        print("No valid subscriptions provided.", file=sys.stderr)
        sys.exit(1)
    report = generate_report(subs, args.output)
    if args.output is None:
        print(report)


if __name__ == '__main__':
    main()