#!/usr/bin/env python3
"""Generate a standalone HTML banking dashboard from Enable Banking CLI data.

Usage:
    python3 generate_report.py

Expects these files in /tmp/:
    - banking-accounts.json   (output of: enable-banking accounts --json)
    - banking-txns-main.json  (output of: enable-banking transactions --json --account main --limit 0)
    - banking-txns-pious.json
    - banking-txns-astoria.json

Produces: /tmp/banking-report-YYYY-MM-DD.html
"""

import json
import os
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from html import escape

ACCOUNTS_FILE = "/tmp/banking-accounts.json"
TXN_FILES = {
    "main": "/tmp/banking-txns-main.json",
    "pious": "/tmp/banking-txns-pious.json",
    "astoria": "/tmp/banking-txns-astoria.json",
}
OUTPUT = f"/tmp/banking-report-{date.today().isoformat()}.html"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)


def fmt(amount_str):
    """Format amount string to French convention: 1 234,56."""
    d = Decimal(amount_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if d < 0 else ""
    d = abs(d)
    integer = int(d)
    frac = f"{d - integer:.2f}"[1:]  # .XX
    s = f"{integer:,}".replace(",", "\u202f")
    return f"{sign}{s}{frac.replace('.', ',')}"


def mask_iban(iban):
    if len(iban) >= 4:
        return f"····{iban[-4:]}"
    return iban


MONTH_NAMES_FR = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre",
}


def month_label(ym):
    parts = ym.split("-")
    return f"{MONTH_NAMES_FR.get(parts[1], parts[1])} {parts[0]}"


def bar_width(value, max_value):
    if max_value == 0:
        return 0
    return min(100, int(abs(value) / abs(max_value) * 100))


def delta_class(d):
    return "positive" if d >= 0 else "negative"


# ---------------------------------------------------------------------------
# Data aggregation
# ---------------------------------------------------------------------------

def aggregate_transactions(txns):
    monthly = defaultdict(lambda: {"credits": Decimal("0"), "debits": Decimal("0"), "count": 0})
    by_cat = defaultdict(lambda: {"total": Decimal("0"), "count": 0})
    monthly_cats = defaultdict(lambda: defaultdict(lambda: {"total": Decimal("0"), "count": 0, "txns": []}))
    uncategorized = []

    for t in txns:
        amt = Decimal(t["Amount"])
        month = t["BookingDate"][:7]
        cat = t.get("Category") or "uncategorized"
        indicator = t["CreditDebitIndicator"]

        monthly[month]["count"] += 1
        if indicator == "CRDT":
            monthly[month]["credits"] += amt
        else:
            monthly[month]["debits"] += amt

        # Always store txns in monthly_cats for drilldown
        monthly_cats[month][cat]["txns"].append(t)
        monthly_cats[month][cat]["count"] += 1

        if indicator == "DBIT":
            by_cat[cat]["total"] += amt
            by_cat[cat]["count"] += 1
            monthly_cats[month][cat]["total"] += amt
            if cat == "uncategorized":
                uncategorized.append(t)

    for m in monthly:
        monthly[m]["delta"] = monthly[m]["credits"] - monthly[m]["debits"]

    return dict(monthly), dict(by_cat), dict(monthly_cats), uncategorized


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_balance_cards(account_data):
    balances = account_data.get("balances", {})
    if not balances:
        return ""
    labels = {"CLBD": "Solde comptable", "OTHR": "Solde courant", "XPCD": "Attendu"}
    cards = []
    for btype in ["CLBD", "OTHR", "XPCD"]:
        if btype in balances:
            cards.append(f"""
            <div class="balance-card">
                <div class="balance-label">{labels.get(btype, btype)}</div>
                <div class="balance-amount">{fmt(balances[btype])} &euro;</div>
            </div>""")
    return "\n".join(cards)


def render_category_bars(by_cat, inline=False, with_txns=False):
    if not by_cat:
        return "<p class='empty'>Aucune dépense</p>"
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]["total"], reverse=True)
    grand = sum(v["total"] for v in by_cat.values())
    css_extra = " inline" if inline else ""
    rows = []
    for cat, info in sorted_cats:
        pct = (info["total"] / grand * 100) if grand else Decimal("0")
        w = bar_width(info["total"], grand)
        css_class = "uncat" if cat == "uncategorized" else ""

        txn_html = ""
        if with_txns and "txns" in info and info["txns"]:
            txn_items = []
            for t in sorted(info["txns"], key=lambda x: x["BookingDate"], reverse=True):
                desc = escape(" ".join(t.get("RemittanceInfo", []))[:80])
                is_credit = t["CreditDebitIndicator"] == "CRDT"
                css = "credit" if is_credit else "debit"
                sign = "+" if is_credit else "-"
                d = t['BookingDate']
                txn_items.append(f"""
                <div class="cat-txn-item">
                    <span class="cat-txn-date">{d[8:]}/{d[5:7]}</span>
                    <span class="cat-txn-desc">{desc}</span>
                    <span class="cat-txn-amount {css}">{sign}{fmt(t['Amount'])} &euro;</span>
                </div>""")
            txn_html = f"""
            <div class="cat-txn-list" style="display:none">
                {"".join(txn_items)}
            </div>"""

        clickable = ' onclick="toggleCatTxns(this)"' if with_txns and txn_html else ""
        cursor = " clickable" if clickable else ""

        rows.append(f"""
        <div class="cat-row {css_class}{cursor}"{clickable}>
            <div class="cat-name">{escape(cat)}</div>
            <div class="cat-bar-wrap">
                <div class="cat-bar" style="width:{w}%"></div>
            </div>
            <div class="cat-amount">{fmt(str(info['total']))} &euro;</div>
            <div class="cat-pct">{pct:.1f}%</div>
            <div class="cat-count">{info['count']}</div>
        </div>{txn_html}""")
    return f'<div class="category-chart{css_extra}">{"".join(rows)}</div>'


def render_monthly_table(monthly, monthly_cats):
    if not monthly:
        return "<p class='empty'>Aucune donnée</p>"
    sorted_months = sorted(monthly.keys(), reverse=True)
    max_val = max(
        max(abs(v["credits"]), abs(v["debits"]))
        for v in monthly.values()
    ) if monthly else Decimal("1")

    rows = []
    for ym in sorted_months:
        m = monthly[ym]
        dc = delta_class(m["delta"])
        cw = bar_width(m["credits"], max_val)
        dw = bar_width(m["debits"], max_val)
        sign = "+" if m["delta"] >= 0 else ""

        # Category breakdown for this month
        cats = monthly_cats.get(ym, {})
        cat_breakdown = render_category_bars(cats, inline=True, with_txns=True) if cats else "<p class='empty'>Aucune dépense ce mois</p>"

        rows.append(f"""
        <tr class="month-row" onclick="toggleMonthDetail(this)">
            <td class="month-name">{month_label(ym)}</td>
            <td class="credit-cell">
                <div class="bar-container"><div class="bar credit-bar" style="width:{cw}%"></div></div>
                <span class="credit">{fmt(str(m['credits']))} &euro;</span>
            </td>
            <td class="debit-cell">
                <div class="bar-container"><div class="bar debit-bar" style="width:{dw}%"></div></div>
                <span class="debit">{fmt(str(m['debits']))} &euro;</span>
            </td>
            <td class="delta-cell {dc}">{sign}{fmt(str(m['delta']))} &euro;</td>
            <td class="count-cell">{m['count']}</td>
        </tr>
        <tr class="month-detail" style="display:none">
            <td colspan="5">
                <div class="month-detail-content">
                    <div class="month-detail-title">Détail — {month_label(ym)}</div>
                    {cat_breakdown}
                </div>
            </td>
        </tr>""")

    return f"""
    <table class="monthly-table">
        <thead><tr>
            <th>Mois</th><th>Crédits</th><th>Débits</th><th>Delta</th><th>Txns</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody>
    </table>"""


def render_transaction_list(txns, account_alias):
    if not txns:
        return ""

    sorted_txns = sorted(txns, key=lambda x: x["BookingDate"], reverse=True)
    rows = []
    for t in sorted_txns:
        amt = Decimal(t["Amount"])
        ind = t["CreditDebitIndicator"]
        css = "credit" if ind == "CRDT" else "debit"
        cat = t.get("Category") or "uncategorized"
        cat_css = "uncat-tag" if cat == "uncategorized" else "cat-tag"
        desc = escape(" ".join(t.get("RemittanceInfo", []))[:100])
        amount_display = f"+{fmt(str(amt))}" if ind == "CRDT" else f"-{fmt(str(amt))}"

        rows.append(f"""
            <tr class="txn-row" data-category="{escape(cat)}" data-direction="{ind}" data-desc="{desc.lower()}">
                <td class="txn-date">{t['BookingDate']}</td>
                <td class="txn-amount {css}">{amount_display} &euro;</td>
                <td><span class="{cat_css}">{escape(cat)}</span></td>
                <td class="txn-desc">{desc}</td>
            </tr>""")

    return f"""
        <table class="txn-table">
            <thead><tr><th>Date</th><th>Montant</th><th>Catégorie</th><th>Description</th></tr></thead>
            <tbody>{"".join(rows)}</tbody>
        </table>"""


# ---------------------------------------------------------------------------
# Main HTML assembly
# ---------------------------------------------------------------------------

def generate_html(accounts_data, all_txns):
    accounts = accounts_data["data"]
    last_synced = accounts_data.get("last_synced", "N/A")
    totals = accounts_data.get("totals", [])

    account_map = {}
    for a in accounts:
        alias = a.get("alias") or mask_iban(a.get("iban", ""))
        account_map[alias] = a

    account_aggs = {}
    for alias, txns in all_txns.items():
        monthly, by_cat, monthly_cats, uncat = aggregate_transactions(txns)
        account_aggs[alias] = {
            "monthly": monthly,
            "by_cat": by_cat,
            "monthly_cats": monthly_cats,
            "uncategorized": uncat,
            "txns": txns,
            "total_txns": len(txns),
        }

    # Global aggregation
    global_monthly = defaultdict(lambda: {"credits": Decimal("0"), "debits": Decimal("0"), "count": 0})
    global_by_cat = defaultdict(lambda: {"total": Decimal("0"), "count": 0})
    global_monthly_cats = defaultdict(lambda: defaultdict(lambda: {"total": Decimal("0"), "count": 0}))
    for alias, agg in account_aggs.items():
        for ym, data in agg["monthly"].items():
            global_monthly[ym]["credits"] += data["credits"]
            global_monthly[ym]["debits"] += data["debits"]
            global_monthly[ym]["count"] += data["count"]
        for cat, data in agg["by_cat"].items():
            global_by_cat[cat]["total"] += data["total"]
            global_by_cat[cat]["count"] += data["count"]
        for ym, cats in agg["monthly_cats"].items():
            for cat, data in cats.items():
                global_monthly_cats[ym][cat]["total"] += data["total"]
                global_monthly_cats[ym][cat]["count"] += data["count"]
    for ym in global_monthly:
        global_monthly[ym]["delta"] = global_monthly[ym]["credits"] - global_monthly[ym]["debits"]

    total_clbd = "N/A"
    if totals:
        total_clbd = totals[0].get("totals", {}).get("CLBD", "N/A")

    # Tab buttons
    tab_buttons = ['<button class="tab-btn active" data-tab="global">Vue globale</button>']
    for alias in account_map:
        tab_buttons.append(f'<button class="tab-btn" data-tab="{escape(alias)}">{escape(alias)}</button>')

    # Global tab
    global_tab = f"""
    <div class="tab-content active" id="tab-global">
        <div class="balance-cards">
            <div class="balance-card total-card">
                <div class="balance-label">Total tous comptes (CLBD)</div>
                <div class="balance-amount">{fmt(total_clbd) if total_clbd != 'N/A' else 'N/A'} &euro;</div>
            </div>
        </div>
        <h3>Évolution mensuelle <span class="hint">cliquer sur un mois pour voir la répartition</span></h3>
        {render_monthly_table(dict(global_monthly), dict(global_monthly_cats))}
    </div>"""

    # Per-account tabs
    account_tabs = []
    for alias in account_map:
        acct = account_map[alias]
        agg = account_aggs.get(alias, {"monthly": {}, "by_cat": {}, "monthly_cats": {}, "uncategorized": [], "txns": [], "total_txns": 0})

        uncat_count = len(agg["uncategorized"])
        uncat_badge = f'<span class="uncat-badge">{uncat_count} non catégorisées</span>' if uncat_count else ""

        cats = sorted(set(t.get("Category") or "uncategorized" for t in agg["txns"]))
        cat_options = '<option value="all">Toutes</option>'
        for c in cats:
            cat_options += f'<option value="{escape(c)}">{escape(c)}</option>'

        account_tabs.append(f"""
    <div class="tab-content" id="tab-{escape(alias)}">
        <div class="account-header">
            <h2>{escape(alias)}</h2>
            {uncat_badge}
            <a href="#" class="txn-toggle" id="txn-toggle-{escape(alias)}" onclick="toggleTxnSection('{escape(alias)}'); return false;">{agg['total_txns']} transactions</a>
        </div>

        <div class="view-dashboard" id="dashboard-{escape(alias)}">
            <div class="balance-cards">{render_balance_cards(acct)}</div>
            <h3>Évolution mensuelle <span class="hint">cliquer sur un mois pour voir la répartition</span></h3>
            {render_monthly_table(agg['monthly'], agg['monthly_cats'])}
        </div>

        <div class="view-transactions" id="txn-section-{escape(alias)}">
            <div class="filters">
                <select class="filter-cat" onchange="filterAndPaginate('{escape(alias)}')">{cat_options}</select>
                <select class="filter-dir" onchange="filterAndPaginate('{escape(alias)}')">
                    <option value="all">Toutes</option>
                    <option value="DBIT">Débits</option>
                    <option value="CRDT">Crédits</option>
                </select>
                <input type="text" class="filter-search" placeholder="Rechercher..." oninput="filterAndPaginate('{escape(alias)}')">
            </div>
            <div class="txn-list" data-alias="{escape(alias)}">{render_transaction_list(agg['txns'], alias)}</div>
            <div class="pagination" id="pagination-{escape(alias)}"></div>
        </div>
    </div>""")

    today = date.today().strftime("%d/%m/%Y")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Banking Report — {today}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, system-ui, 'Segoe UI', sans-serif;
    background: #f5f5f7;
    color: #1d1d1f;
    line-height: 1.6;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}

/* Header */
header {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 0; border-bottom: 1px solid #d2d2d7;
    margin-bottom: 24px;
}}
header h1 {{ font-size: 1.5em; font-weight: 700; color: #1d1d1f; }}
.sync-info {{ color: #86868b; font-size: 0.85em; }}

/* Tabs */
.tab-bar {{
    display: flex; gap: 2px; margin-bottom: 28px;
    background: #e8e8ed; border-radius: 10px; padding: 3px;
    width: fit-content;
}}
.tab-btn {{
    padding: 8px 20px; border: none; background: transparent;
    color: #86868b; cursor: pointer; font-size: 0.9em; font-weight: 500;
    border-radius: 8px; transition: all 0.2s;
}}
.tab-btn:hover {{ color: #1d1d1f; }}
.tab-btn.active {{ background: #fff; color: #1d1d1f; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* Balance cards */
.balance-cards {{ display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }}
.balance-card {{
    background: #fff; border-radius: 14px; padding: 20px 28px;
    flex: 1; min-width: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e8e8ed;
}}
.total-card {{ border-color: #0071e3; }}
.balance-label {{ color: #86868b; font-size: 0.82em; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.03em; }}
.balance-amount {{ font-size: 1.7em; font-weight: 700; font-family: 'SF Mono', 'Menlo', monospace; color: #1d1d1f; }}

/* Category bars */
.category-chart {{ margin-bottom: 28px; }}
.category-chart.inline {{ margin-bottom: 0; }}
.cat-row {{
    display: flex; align-items: center; gap: 12px; padding: 7px 0;
    border-bottom: 1px solid #f0f0f2;
}}
.cat-row.uncat {{ background: #fff5f5; border-radius: 6px; padding: 7px 10px; }}
.cat-name {{ width: 130px; font-size: 0.88em; font-weight: 500; flex-shrink: 0; color: #1d1d1f; }}
.cat-bar-wrap {{ flex: 1; height: 18px; background: #f0f0f2; border-radius: 9px; overflow: hidden; }}
.cat-bar {{ height: 100%; background: linear-gradient(90deg, #0071e3, #5856d6); border-radius: 9px; }}
.cat-row.uncat .cat-bar {{ background: linear-gradient(90deg, #ff3b30, #ff6961); }}
.cat-amount {{ width: 100px; text-align: right; font-family: 'SF Mono', monospace; font-size: 0.88em; font-weight: 500; flex-shrink: 0; }}
.cat-pct {{ width: 45px; text-align: right; color: #86868b; font-size: 0.82em; flex-shrink: 0; }}
.cat-count {{ width: 30px; text-align: right; color: #aeaeb2; font-size: 0.78em; flex-shrink: 0; }}

/* Monthly table */
.monthly-table {{ width: 100%; border-collapse: collapse; margin-bottom: 28px; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
.monthly-table th {{
    text-align: left; padding: 12px 16px; border-bottom: 1px solid #e8e8ed;
    color: #86868b; font-size: 0.8em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
}}
.monthly-table td {{ padding: 12px 16px; }}
.month-row {{ cursor: pointer; transition: background 0.15s; border-bottom: 1px solid #f5f5f7; }}
.month-row:hover {{ background: #f5f5f7; }}
.month-name {{ font-weight: 600; color: #1d1d1f; }}
.bar-container {{ display: inline-block; width: 80px; height: 10px; background: #f0f0f2; border-radius: 5px; vertical-align: middle; margin-right: 8px; overflow: hidden; }}
.bar {{ height: 100%; border-radius: 5px; }}
.credit-bar {{ background: #34c759; }}
.debit-bar {{ background: #ff3b30; }}
.credit {{ color: #248a3d; font-family: 'SF Mono', monospace; font-size: 0.88em; }}
.debit {{ color: #d70015; font-family: 'SF Mono', monospace; font-size: 0.88em; }}
.delta-cell {{ font-family: 'SF Mono', monospace; font-weight: 600; }}
.positive {{ color: #248a3d; }}
.negative {{ color: #d70015; }}
.count-cell {{ color: #86868b; text-align: center; }}

/* Month detail (category breakdown) */
.month-detail td {{ padding: 0 !important; }}
.month-detail-content {{ padding: 12px 24px 16px; background: #fafafa; border-bottom: 1px solid #e8e8ed; }}
.month-detail-title {{ font-size: 0.82em; font-weight: 600; color: #86868b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em; }}

/* Account header */
.account-header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }}
.account-header h2 {{ font-size: 1.4em; font-weight: 700; color: #1d1d1f; text-transform: capitalize; }}
.uncat-badge {{
    background: #fff0f0; color: #d70015; padding: 4px 12px;
    border-radius: 20px; font-size: 0.78em; font-weight: 600;
}}
.txn-total {{ color: #86868b; font-size: 0.85em; }}
.txn-toggle {{
    color: #0071e3; font-size: 0.85em; text-decoration: none; font-weight: 500;
    cursor: pointer; transition: color 0.15s;
}}
.txn-toggle:hover {{ color: #0062cc; text-decoration: underline; }}
.txn-toggle.active {{ color: #86868b; }}
.txn-toggle.active::before {{ content: "\\2190 "; }}

/* View switching */
.view-dashboard, .view-transactions {{
    animation: viewFadeIn 0.3s ease;
}}
.view-transactions {{ display: none; }}
@keyframes viewFadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Filters */
.filters {{
    display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap;
}}
.filters select, .filters input {{
    background: #fff; color: #1d1d1f; border: 1px solid #d2d2d7;
    padding: 8px 14px; border-radius: 8px; font-size: 0.88em;
}}
.filters input {{ flex: 1; min-width: 200px; }}
.filters select:focus, .filters input:focus {{ outline: none; border-color: #0071e3; box-shadow: 0 0 0 3px rgba(0,113,227,0.15); }}

/* Transactions */
.txn-table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e8e8ed; border-top: none; border-radius: 0 0 10px 10px; overflow: hidden; }}
.txn-table th {{
    text-align: left; padding: 8px 14px; color: #86868b; font-size: 0.78em;
    border-bottom: 1px solid #f0f0f2; font-weight: 600; text-transform: uppercase;
}}
.txn-row td {{ padding: 7px 14px; border-bottom: 1px solid #f5f5f7; font-size: 0.85em; }}
.txn-row:last-child td {{ border-bottom: none; }}
.txn-date {{ color: #86868b; white-space: nowrap; width: 50px; }}
.txn-amount {{ font-family: 'SF Mono', monospace; white-space: nowrap; width: 120px; font-weight: 500; }}
.txn-desc {{ color: #6e6e73; font-size: 0.82em; max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.cat-tag {{
    background: #f0f0f2; color: #1d1d1f; padding: 2px 8px; border-radius: 4px;
    font-size: 0.78em; white-space: nowrap;
}}
.uncat-tag {{
    background: #fff0f0; color: #d70015; padding: 2px 8px;
    border-radius: 4px; font-size: 0.78em; white-space: nowrap;
}}
/* Category transaction drilldown */
.cat-row.clickable {{ cursor: pointer; position: relative; }}
.cat-row.clickable:hover {{ background: #f5f5f7; border-radius: 8px; }}
.cat-row.clickable::after {{
    content: "\\25B8"; position: absolute; right: -16px; top: 50%;
    transform: translateY(-50%); color: #aeaeb2; font-size: 0.7em;
    transition: transform 0.2s;
}}
.cat-txn-list {{
    margin: 2px 0 8px 140px; padding: 4px 0;
    background: #fafafa; border-radius: 8px;
}}
.cat-txn-item {{
    display: flex; align-items: center; gap: 12px;
    padding: 5px 14px; font-size: 0.82em;
}}
.cat-txn-item:hover {{ background: #f0f0f2; }}
.cat-txn-date {{ color: #86868b; min-width: 36px; font-variant-numeric: tabular-nums; }}
.cat-txn-desc {{ flex: 1; color: #3a3a3c; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.cat-txn-amount {{ font-family: 'SF Mono', ui-monospace, monospace; font-weight: 500; white-space: nowrap; font-variant-numeric: tabular-nums; }}

.empty {{ color: #86868b; font-style: italic; padding: 20px 0; }}

/* Pagination */
.pagination {{
    display: flex; justify-content: center; align-items: center; gap: 4px;
    margin-top: 16px; padding: 12px 0;
}}
.pagination button {{
    padding: 6px 12px; border: 1px solid #d2d2d7; background: #fff;
    border-radius: 6px; font-size: 0.85em; cursor: pointer;
    color: #1d1d1f; transition: all 0.15s;
}}
.pagination button:hover {{ border-color: #0071e3; color: #0071e3; }}
.pagination button.active {{ background: #0071e3; color: #fff; border-color: #0071e3; }}
.pagination button:disabled {{ opacity: 0.4; cursor: default; }}
.pagination .page-info {{ color: #86868b; font-size: 0.82em; margin: 0 8px; }}

h3 {{
    color: #1d1d1f; font-size: 1em; margin-bottom: 14px; margin-top: 12px;
    display: flex; align-items: center; gap: 10px;
}}
.hint {{ font-size: 0.75em; color: #aeaeb2; font-weight: 400; }}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>Banking Dashboard</h1>
        <div class="sync-info">Dernière synchro : {escape(last_synced[:10] if last_synced != 'N/A' else 'N/A')} &middot; Rapport du {today}</div>
    </header>

    <div class="tab-bar">
        {"".join(tab_buttons)}
    </div>

    {global_tab}
    {"".join(account_tabs)}
</div>

<script>
// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    }});
}});

// Category row click → toggle transaction list
function toggleCatTxns(row) {{
    const txnList = row.nextElementSibling;
    if (txnList && txnList.classList.contains('cat-txn-list')) {{
        txnList.style.display = txnList.style.display === 'none' ? '' : 'none';
    }}
}}

// Monthly row click → toggle category detail
function toggleMonthDetail(row) {{
    const detail = row.nextElementSibling;
    if (detail && detail.classList.contains('month-detail')) {{
        detail.style.display = detail.style.display === 'none' ? '' : 'none';
    }}
}}

// Toggle between dashboard and transactions view
function toggleTxnSection(alias) {{
    const dashboard = document.getElementById('dashboard-' + alias);
    const txnSection = document.getElementById('txn-section-' + alias);
    const toggle = document.getElementById('txn-toggle-' + alias);
    if (!dashboard || !txnSection) return;

    const showingTxns = txnSection.style.display === 'block';

    if (showingTxns) {{
        // Back to dashboard
        txnSection.style.display = 'none';
        dashboard.style.display = '';
        dashboard.style.animation = 'none';
        dashboard.offsetHeight;
        dashboard.style.animation = '';
        toggle.classList.remove('active');
    }} else {{
        // Show transactions
        dashboard.style.display = 'none';
        txnSection.style.display = 'block';
        txnSection.style.animation = 'none';
        txnSection.offsetHeight;
        txnSection.style.animation = '';
        toggle.classList.add('active');
        filterAndPaginate(alias);
    }}
}}

// Filter + paginate transactions
const PAGE_SIZE = 100;
const pageState = {{}};

function filterAndPaginate(alias, page) {{
    const tab = document.getElementById('tab-' + alias);
    if (!tab) return;
    const catFilter = tab.querySelector('.filter-cat').value;
    const dirFilter = tab.querySelector('.filter-dir').value;
    const searchFilter = tab.querySelector('.filter-search').value.toLowerCase();

    const allRows = Array.from(tab.querySelectorAll('.txn-row'));
    const matched = allRows.filter(row => {{
        const cat = row.dataset.category;
        const dir = row.dataset.direction;
        const desc = row.dataset.desc;
        return (catFilter === 'all' || cat === catFilter)
            && (dirFilter === 'all' || dir === dirFilter)
            && (!searchFilter || desc.includes(searchFilter));
    }});

    const totalPages = Math.max(1, Math.ceil(matched.length / PAGE_SIZE));
    const currentPage = Math.min(page || 1, totalPages);
    pageState[alias] = currentPage;

    const start = (currentPage - 1) * PAGE_SIZE;
    const end = start + PAGE_SIZE;

    allRows.forEach(r => r.style.display = 'none');
    matched.forEach((r, i) => {{
        r.style.display = (i >= start && i < end) ? '' : 'none';
    }});

    // Render pagination
    const pag = document.getElementById('pagination-' + alias);
    if (!pag) return;
    if (totalPages <= 1) {{ pag.innerHTML = `<span class="page-info">${{matched.length}} résultats</span>`; return; }}

    let html = `<button onclick="filterAndPaginate('${{alias}}', ${{currentPage - 1}})" ${{currentPage <= 1 ? 'disabled' : ''}}>&lsaquo;</button>`;
    for (let p = 1; p <= totalPages; p++) {{
        html += `<button class="${{p === currentPage ? 'active' : ''}}" onclick="filterAndPaginate('${{alias}}', ${{p}})">${{p}}</button>`;
    }}
    html += `<button onclick="filterAndPaginate('${{alias}}', ${{currentPage + 1}})" ${{currentPage >= totalPages ? 'disabled' : ''}}>&rsaquo;</button>`;
    html += `<span class="page-info">${{matched.length}} résultats</span>`;
    pag.innerHTML = html;
}}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Error: {ACCOUNTS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    accounts_data = load_json(ACCOUNTS_FILE)

    all_txns = {}
    for alias, path in TXN_FILES.items():
        if os.path.exists(path):
            data = load_json(path)
            all_txns[alias] = data.get("data", [])
        else:
            print(f"Warning: {path} not found, skipping {alias}", file=sys.stderr)
            all_txns[alias] = []

    html = generate_html(accounts_data, all_txns)

    with open(OUTPUT, "w") as f:
        f.write(html)

    print(f"Report generated: {OUTPUT}")


if __name__ == "__main__":
    main()
