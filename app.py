import os

from flask import Flask, render_template
from markupsafe import escape
from typing import Optional
import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import fisher_exact, pearsonr

app = Flask(__name__)

TEXT_COLOR = "#f7efe4"
MUTED_COLOR = "#aab4c2"
SP_COLOR = "#ffb66b"
GAS_COLOR = "#4C78A8"
POSITIVE_COLOR = "#59A14F"      # "moved same direction"
NEGATIVE_COLOR = "#E15759"      # "moved opposite direction"
MAJOR_EVENT_COLOR = "#f06d5d"
OTHER_YEAR_COLOR = "#64748B"
NORMAL_YEAR_COLOR = "#3a4a63"
EPISODE_COLORS = {              # the crisis strip needs 4 distinct episode colors, not
    "Normal Year": NORMAL_YEAR_COLOR,      # 1 — collapsing to a single color would destroy
    "Dot-Com Crash": "#8E6C8A",            # the "which crisis" information the strip
    "Financial Crisis": NEGATIVE_COLOR,    # conveys.
    "COVID-19 Crash": GAS_COLOR,
    "2022 Selloff": SP_COLOR,
}

GLOSSARY = {
    "indexed value": "Value scaled so the starting year equals 100, so two series with different units (dollars vs. gallons) can be compared on the same relative scale.",
    "percent change": "The size of a move from one period to the next, expressed as a percentage of the starting value.",
    "volatility": "How much a price bounces around during a period, not just where it ends up — a market that swings wildly but nets out flat is still volatile.",
    "trend-line slope": "The steepness of the fitted line: how much the y-value changes, on average, for each one-unit increase in the x-value.",
    "crisis year": "A year that falls between when gas and the S&P actually bottomed out during one of four major downturns (Dot-Com, 2008 Financial Crisis, COVID-19, the 2022 selloff).",
}


def term(label: str, key: Optional[str] = None) -> str:
    """Wraps `label` in a hoverable span with a plain-language definition
    (see static/styles.css .term / .term::after) so jargon in the prose
    doesn't need a separate glossary section. Only used on the exact
    description/finding.text fields marked `| safe` in the template."""
    definition = GLOSSARY[key or label.lower()]
    return f'<span class="term" tabindex="0" data-def="{escape(definition)}">{escape(label)}</span>'


@alt.theme.register("energy_market_dark", enable=True)
def energy_market_dark_theme():
    """Matches static/styles.css so charts blend into the page instead of
    sitting on top of it as a pasted-in white card."""
    text_color = TEXT_COLOR
    muted_color = MUTED_COLOR
    grid_color = "rgba(255,255,255,0.10)"
    line_color = "rgba(255,255,255,0.25)"
    accent = SP_COLOR
    accent2 = MAJOR_EVENT_COLOR
    font = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

    return {
        "background": "transparent",
        "padding": {"left": 8, "right": 16, "top": 12, "bottom": 8},
        "config": {
            "background": "transparent",
            "font": font,
            "title": {
                "color": text_color,
                "subtitleColor": muted_color,
                "font": font,
                "fontSize": 16,
                "subtitleFontSize": 12,
                "anchor": "start",
            },
            "axis": {
                "labelColor": muted_color,
                "titleColor": text_color,
                "gridColor": grid_color,
                "domainColor": line_color,
                "tickColor": line_color,
                "labelFont": font,
                "titleFont": font,
            },
            "legend": {
                "labelColor": muted_color,
                "titleColor": text_color,
                "labelFont": font,
                "titleFont": font,
            },
            "header": {"labelColor": muted_color, "titleColor": text_color, "labelFont": font, "titleFont": font},
            "view": {"stroke": "transparent"},
            "range": {
                "category": [
                    GAS_COLOR, accent, accent2, POSITIVE_COLOR, "#8E6C8A", "#EDC948", "#79706E", "#D37295",
                ],
            },
        },
    }


sections = [
    {
        "id": "cover",
        "type": "hero",
        "eyebrow": "W209 • Data Visualization",
        "title": "Do Gas Prices Really Predict the Stock Market?",
        "subtitle": "We tested three common assumptions about gas prices and the S&P 500 against 25 years of data. The results were a mixed bag — one didn't hold up, and two showed only a weak, inconclusive signal once we accounted for how little data there actually is.",
        "summary": "Scroll through three questions, each answered by a single chart built to be read at a glance — then explore the full data yourself at the end.",
    },
    {
        "id": "introduction",
        "type": "story",
        "eyebrow": "01 • Introduction",
        "title": "Why this relationship matters",
        "description": "Gas prices and the stock market are often assumed to move together, but that assumption is rarely tested carefully. This report investigates the relationship through three specific, falsifiable questions — each paired with a visualization designed to let you see the pattern for yourself, rather than take our word for it.",
        "highlights": [
            "Gas prices react quickly to supply and policy changes.",
            "The S&P 500 reflects expectations about growth and inflation.",
            "We test three specific questions instead of assuming they move together."
        ],
        "next": {"id": "hypothesis-1", "label": "Question 1: Does gas lead the market down?"},
    },
    {
        "id": "hypothesis-1",
        "type": "hypothesis",
        "eyebrow": "02 • Question 1",
        "title": "Does a gas-price dip really happen before a stock-market dip?",
        "description": "The original idea: falling gas prices act as an early warning sign for a stock market downturn. Annual averages can't show monthly timing, so instead we found the exact month each major downturn bottomed out in both markets and compared the dates directly.",
        "chart_items": [
            {
                "title": "Indexed trend",
                "chart_id": "chart1",
                "caption": "A long-view comparison of the indexed S&P 500 and gas prices over time.",
            },
            {
                "title": "Yearly change",
                "chart_id": "chart2",
                "caption": "Year-by-year percent change for both markets.",
            },
            {        
                "title": "Does a gas-price dip really happen before a stock-market dip?",
                "chart_id": "chart_h1_timeline",
                "chart_caption": "The month each market bottomed out during four major downturns — no consistent leader emerges.",

            },

        ],
        "finding": {
            "label": "The Finding",
            "text": "No. In 2 of 4 downturns, gas bottomed out first; in the other 2, the S&P 500 did. The gap ranges from 2 to 9 months, with no consistent pattern in which market leads. Worth flagging: this is a small sample (only 4 major downturns exist in 25 years), and the exact trough dates are read off month-end prices, which can miss the true day-to-day low by a few weeks — but even allowing for that uncertainty, there's no visible sign of a reliable pattern either way.",
        },
        "metrics": [
            {"value": "No consistent leader", "label": "gas dipped first in 2 of 4 downturns, the S&P 500 in the other 2"},
            {"value": "Not supported", "label": "no reliable lead-lag pattern across 25 years"},
        ],
        "next": {"id": "hypothesis-2", "label": "Question 2: Do bigger gains mean bigger gas swings?"},
    },
    {
        "id": "hypothesis-2",
        "type": "hypothesis",
        "eyebrow": "03 • Question 2",
        "title": "Do bigger stock market swings come with bigger gas-price swings?",
        "description": (
            f"{term('Volatility', 'volatility')} means how much a price bounces around, not just where it ends up — a market that swings wildly but nets out flat is still volatile. "
            "Here we measure it annually: S&P 500 volatility is the annualized standard deviation of monthly returns for that year, and gas volatility is the absolute year-over-year change in the average California gas price. "
            f"One point per year, 2001–2025. Use the year-range dropdowns to zoom the scatter to a window — its {term('trend-line slope')} updates live."
        ),
        "chart_id": "chart_h2_combined",
        "chart_title": "Annual volatility vs. gas-price swing",
        "chart_caption": "Each dot in the scatter is one year; the linked timeline below shows both measures on the same scale.",
        "finding": {
            "label": "The Finding",
            "text": "Weak, and not statistically significant. Across the 25 years from 2001–2025, S&P 500 volatility and the size of that year's gas-price swing show only a weak positive relationship (r = 0.31). The 95% confidence interval, [-0.10, 0.63], crosses zero, and the correlation doesn't clear the standard bar for statistical significance (p = 0.136). There's a hint of the pattern the hypothesis predicts, but with only 25 annual observations, we can't rule out that it's just noise.",
        },
        "metrics": [
            {"value": "r = 0.31", "label": "weak positive association"},
            {"value": "p = 0.136", "label": "not statistically significant"},
            {"value": "n = 25", "label": "annual observations, 2001-2025"},
        ],
        "next": {"id": "hypothesis-3", "label": "Question 3: Do crises break the link?"},
    },
    {
        "id": "hypothesis-3",
        "type": "hypothesis",
        "eyebrow": "04 • Question 3",
        "title": "Does the normal link between gas prices and stocks hold up during a crisis?",
        "description": (
            "In an average year, do gas prices and the S&P 500 move in the same direction? And does that really break down during a crisis? "
            f"To keep {term('crisis year')} consistent with Hypothesis 1 instead of picking a separate list, a year counts as one here only if it falls between when gas and the S&P actually bottomed out during one of the same four downturns from Question 1 (the Dot-Com Crash, the 2008 Financial Crisis, COVID-19, and the 2022 selloff). "
            "That gives 7 crisis years and 19 normal years, which we compared."
        ),
        "chart_caption": "Every point in the scatter is labeled with its year. Quadrant color tells you \"same\" from \"opposite\" directly; circles are normal years, diamonds are crisis years.",
        "finding": {
            "label": "The Finding",
            "text": "Inconclusive. Normal years moved in the same direction 63% of the time versus 43% in crisis years (2001-02, 2008-09, 2020, 2022-23) — a real gap in the raw numbers, and in the direction the hypothesis predicts. But with only 7 crisis years to work with, a Fisher's exact test can't rule out that this gap is just chance (p = 0.41). We can't confidently say the pattern breaks down during a crisis — only that it might, and we don't have enough data yet to tell.",
        },
        "metrics": [],
        "technical_details": "",
        "next": {"id": "event-impact", "label": "See the event impact map"},
    },
    {
        "id": "event-impact",
        "type": "event_map",
        "eyebrow": "07 • Event Impact",
        "title": "Which shocks moved the market most?",
        "description": "Each tile is a major global event since 2001. Tile size = magnitude of change after the event; color shows whether the S&P 500 or California gas price gained or lost over the selected window.",
        "chart_caption": "Adjust the window or switch the metric to see how impact compounds or fades over time.",
        "metrics": [],
        "next": {"id": "conclusion", "label": "See the conclusion"},
    },
    {
        "id": "conclusion",
        "type": "story",
        "eyebrow": "05 • Conclusion",
        "title": "What the data actually shows",
        "description": "Testing three specific, falsifiable questions instead of assuming a single story produced three answers that all point the same way: one hypothesis wasn't supported at all, and the other two showed only weak signals that don't clear statistical significance once the (small) amount of data is accounted for. That consistency is itself the finding — the gas-price/S&P relationship isn't the strong, reliable story it's often assumed to be, and claiming more certainty than the data actually supports would have been misleading.",
        "highlights": [
            "Hypothesis 1 (gas leads stocks down): not supported — across four major downturns, the lead varied both ways.",
            "Hypothesis 2 (high volatility pairs with high volatility): weak and inconclusive — annual S&P volatility and the size of that year's gas-price swing show only a weak positive relationship (r = 0.31), and it isn't statistically significant (p = 0.136, n = 25).",
            "Hypothesis 3 (crises break the link): inconclusive — normal years moved together more often than crisis years (63% vs. 43%), using a crisis-year definition kept consistent with Hypothesis 1, but with only 7 crisis years to work with, that gap isn't statistically significant (p = 0.41)."
        ],
        "next": {"id": "chart-explorer", "label": "Explore the full data yourself"},
    },
    {
        "id": "chart-explorer",
        "type": "explorer",
        "eyebrow": "06 • Explore",
        "title": "Explore the data yourself",
        "description": "Now that you've seen the story, dig into any of the underlying visualizations directly — including the supporting charts that didn't make the main narrative.",
        "chart_items": [
            {
                "title": "Who dipped first",
                "chart_id": "chart_h1_timeline",
                "caption": "The month each market bottomed out during four major downturns.",
            },
            {
                "title": "Annual volatility vs. gas swing",
                "chart_id": "chart_h2_combined",
                "caption": "Annualized S&P volatility vs. the size of that year's gas-price swing, one point per year — the chart behind Question 2.",
            },
            {
                "title": "Event volatility (timeline, alternate)",
                "chart_id": "chart_event_window",
                "caption": "An earlier version of the volatility analysis: S&P 500 and gas price volatility after every major event since 2001, with an adjustable time window.",
            },
            {
                "title": "Event volatility (scatter, alternate)",
                "chart_id": "chart_event_scatter",
                "caption": "The same earlier-version data as a scatter — each dot is one event.",
            },
            {
                "title": "Event volatility (dumbbell)",
                "chart_id": "chart_event_dumbbell",
                "caption": "All 52 tracked events, one row each, connecting S&P 500 and gas-price volatility for the selected window.",
            },
            {
                "title": "Normal vs. crisis (split)",
                "chart_id": "chart_h3_split",
                "caption": "How often gas prices and the S&P 500 move together, normal years versus crisis years.",
            },
            {
                "title": "Normal vs. crisis (combined)",
                "chart_id": "chart_h3_quadrant",
                "caption": "The same comparison as one combined scatter with quadrant coloring — every point labeled with its year.",
            },
            {
                "title": "Yearly bars",
                "chart_id": "chart3",
                "caption": "Yearly percent change bars make the ups and downs easier to compare.",
            },
        ]
    },
]


def event_group(year: int) -> str:
    """A year's classification, derived from CRISIS_YEAR_MAP (see
    compute_crisis_years) so this matches Hypothesis 1's downturn episodes
    exactly instead of using a separately hand-picked list."""
    return CRISIS_YEAR_MAP.get(year, "Normal Year")


def load_analysis_data():
    base_path = os.path.dirname(__file__)
    market_file = os.path.join(base_path, "SP500_GasPrices_Tableau_v3.xlsx")
    events_file = os.path.join(base_path, "Major_Global_Events_2001_Present (1).xlsx")

    annual = pd.read_excel(market_file, sheet_name="Annual_Data", engine="openpyxl")
    annual = annual.rename(columns={
        "Avg CA Gas Price ($/gal)": "Gas_Price",
        "Avg S&P 500 Close": "SP_Avg",
    })
    annual = annual.dropna(subset=["Year", "Gas_Price", "SP_Avg"])
    annual["Year"] = annual["Year"].astype(int)
    annual = annual.sort_values("Year")
    annual["SP_Return"] = annual["SP_Avg"].pct_change() * 100
    annual["Gas_Change"] = annual["Gas_Price"].pct_change() * 100
    annual["SP_Index"] = annual["SP_Avg"] / annual["SP_Avg"].iloc[0] * 100
    annual["Gas_Index"] = annual["Gas_Price"] / annual["Gas_Price"].iloc[0] * 100
    annual["Date"] = pd.to_datetime(annual["Year"].astype(str) + "-01-01")
    annual["Event"] = annual["Year"].apply(event_group)
    annual["Gas_Direction"] = np.where(annual["Gas_Change"] >= 0, "Gas Up", "Gas Down")
    annual["SP_Direction"] = np.where(annual["SP_Return"] >= 0, "S&P Up", "S&P Down")
    annual["Pattern"] = annual["SP_Direction"] + " / " + annual["Gas_Direction"]

    long_index = annual.melt(
        id_vars=["Year", "Date", "Event", "Gas_Price"],
        value_vars=["SP_Index", "Gas_Index"],
        var_name="Type",
        value_name="Index_Value",
    )
    long_index["Type"] = long_index["Type"].replace({
        "SP_Index": "S&P 500",
        "Gas_Index": "Gas Prices",
    })

    long_change = annual.melt(
        id_vars=["Year", "Date", "Event"],
        value_vars=["SP_Return", "Gas_Change"],
        var_name="Type",
        value_name="Percent_Change",
    )
    long_change["Type"] = long_change["Type"].replace({
        "SP_Return": "S&P 500 Return",
        "Gas_Change": "Gas Price Change",
    })

    pattern_counts = annual.groupby(["Event", "Pattern"]).size().reset_index(name="Count")

    return {
        "annual": annual,
        "long_index": long_index,
        "long_change": long_change,
        "pattern_counts": pattern_counts,
    }


EVENT_CATEGORIES = {
    "9/11 Terrorist Attacks": "Terror & Security",
    "U.S. Invasion of Afghanistan (Operation Enduring Freedom)": "Geopolitical Conflict",
    "Enron Scandal / Collapse": "Markets & Finance",
    "SARS Outbreak": "Health Crisis",
    "U.S. Invasion of Iraq (Operation Iraqi Freedom)": "Geopolitical Conflict",
    "Hurricane Katrina": "Natural Disaster",
    "U.S. Housing Market Crash Begins": "Economic Crisis",
    "Bear Stearns Collapse": "Economic Crisis",
    "Global Financial Crisis / Lehman Brothers Collapse": "Economic Crisis",
    "TARP Bailout Passed": "Policy & Politics",
    "European Sovereign Debt Crisis (Greece Bailout)": "Economic Crisis",
    "Flash Crash": "Markets & Finance",
    "Arab Spring Begins": "Geopolitical Conflict",
    "Libyan Civil War / Oil Supply Disruption": "Energy & Supply Shock",
    "Fukushima Nuclear Disaster / Japan Earthquake": "Natural Disaster",
    "U.S./NATO Intervention in Libya (Operation Odyssey Dawn)": "Geopolitical Conflict",
    "Killing of Osama bin Laden (Operation Neptune Spear)": "Terror & Security",
    "U.S. Credit Rating Downgrade (S&P)": "Markets & Finance",
    "Eurozone Crisis Escalation (Greek Debt Restructuring)": "Economic Crisis",
    "Federal Reserve 'Taper Tantrum'": "Policy & Politics",
    "Russia Annexation of Crimea": "Geopolitical Conflict",
    "U.S. Military Intervention Against ISIS (Operation Inherent Resolve)": "Geopolitical Conflict",
    "Oil Price Collapse (OPEC Supply Glut)": "Energy & Supply Shock",
    "Chinese Stock Market Crash": "Markets & Finance",
    "Brexit Referendum": "Policy & Politics",
    "U.S. Presidential Election (Trump Win)": "Policy & Politics",
    "U.S.-China Trade War Begins": "Policy & Politics",
    "U.S. Stock Market Selloff (Q4)": "Markets & Finance",
    "Killing of Qasem Soleimani / U.S.-Iran Tensions": "Geopolitical Conflict",
    "OPEC+ Oil Price War (Saudi-Russia)": "Energy & Supply Shock",
    "COVID-19 Pandemic Declared / Market Crash": "Health Crisis",
    "U.S. Oil Futures Go Negative": "Energy & Supply Shock",
    "COVID-19 Vaccine Rollout Begins": "Health Crisis",
    "GameStop / Meme Stock Short Squeeze": "Markets & Finance",
    "Suez Canal Blockage (Ever Given)": "Energy & Supply Shock",
    "U.S. Withdrawal from Afghanistan": "Geopolitical Conflict",
    "Russia Invades Ukraine": "Geopolitical Conflict",
    "Federal Reserve Aggressive Rate Hikes Begin": "Policy & Politics",
    "U.S. Inflation Peaks at 40-Year High": "Economic Crisis",
    "Silicon Valley Bank Collapse": "Markets & Finance",
    "Credit Suisse Collapse / Forced UBS Merger": "Markets & Finance",
    "OPEC+ Surprise Production Cuts": "Energy & Supply Shock",
    "U.S. Debt Ceiling Crisis": "Policy & Politics",
    "Israel-Hamas War Begins": "Geopolitical Conflict",
    "Red Sea Shipping Crisis (Houthi Attacks)": "Energy & Supply Shock",
    "U.S. Airstrikes on Houthi Targets in Yemen (Operation Poseidon Archer)": "Geopolitical Conflict",
    "Israel-Iran Conflict Escalation": "Geopolitical Conflict",
    "Federal Reserve Begins Rate Cuts": "Policy & Politics",
    "DeepSeek AI Shock to Tech Stocks": "Markets & Finance",
    "U.S. Tariff Announcements ('Liberation Day' Tariffs)": "Policy & Politics",
    "U.S. Strikes on Iranian Nuclear Facilities (Operation Midnight Hammer)": "Geopolitical Conflict",
}

EVENT_WINDOW_MONTHS = list(range(2, 13))


def load_monthly_market_data() -> pd.DataFrame:
    base_path = os.path.dirname(__file__)
    market_file = os.path.join(base_path, "SP500_GasPrices_Tableau_v3.xlsx")

    monthly = pd.read_excel(market_file, sheet_name="Monthly_Data", engine="openpyxl")
    monthly = monthly.rename(columns={
        "S&P 500 Close": "SP_Close",
        "CA Gas Price ($/gal)": "Gas_Price",
    })
    monthly["Date"] = pd.to_datetime(monthly["Date"])
    monthly = monthly.dropna(subset=["Date", "SP_Close", "Gas_Price"]).sort_values("Date")
    return monthly


def load_event_window_data() -> pd.DataFrame:
    """For every event in the Major Global Events file, compute the actual
    volatility (standard deviation of monthly % returns, the textbook
    definition — not just the size of the net move from start to end) of
    the S&P 500 and CA gas price during a 2-12 month window starting at the
    event's start date. Windows shorter than 2 months can't produce a
    meaningful standard deviation, so 1 month is excluded."""
    base_path = os.path.dirname(__file__)
    events_file = os.path.join(base_path, "Major_Global_Events_2001_Present (1).xlsx")

    events = pd.read_excel(events_file, sheet_name="Global Events", engine="openpyxl")
    events = events.dropna(subset=["Event Name", "Start Date"])
    events["Start Date"] = pd.to_datetime(events["Start Date"])
    events["Category"] = events["Event Name"].map(EVENT_CATEGORIES).fillna("Other")

    monthly = load_monthly_market_data()
    monthly["SP_MoM"] = monthly["SP_Close"].pct_change() * 100
    monthly["Gas_MoM"] = monthly["Gas_Price"].pct_change() * 100

    records = []
    for _, ev in events.iterrows():
        start = ev["Start Date"]

        for window in EVENT_WINDOW_MONTHS:
            window_end = start + pd.DateOffset(months=window)
            in_window = monthly[(monthly["Date"] > start) & (monthly["Date"] <= window_end)]
            if len(in_window) < 2:
                continue

            sp_volatility = in_window["SP_MoM"].std()
            gas_volatility = in_window["Gas_MoM"].std()
            if pd.isna(sp_volatility) or pd.isna(gas_volatility):
                continue

            for market, volatility in (("S&P 500", sp_volatility), ("Gas Price", gas_volatility)):
                records.append({
                    "Event": ev["Event Name"],
                    "Category": ev["Category"],
                    "Start Date": start,
                    "Window": window,
                    "Market": market,
                    "Volatility": volatility,
                })

    return pd.DataFrame(records)


def compute_event_window_correlations(event_window: pd.DataFrame) -> pd.DataFrame:
    """Correlation between S&P volatility and gas volatility (both the
    standard-deviation-based measure, so directly comparable) at each
    window length, for the plain-language annotation under the chart."""
    records = []
    for window in EVENT_WINDOW_MONTHS:
        sub = event_window[event_window["Window"] == window]
        pivoted = sub.pivot(index=["Event", "Start Date"], columns="Market", values="Volatility").dropna()
        r = pivoted["S&P 500"].corr(pivoted["Gas Price"])
        strength = "little to no" if abs(r) < 0.1 else ("a weak" if abs(r) < 0.3 else "a moderate")
        direction = "move together" if r > 0 else "move oppositely"
        label = f"At this window: S&P volatility and gas volatility show {strength} tendency to {direction} (r = {r:+.2f})"
        records.append({"Window": window, "Correlation": r, "Label": label})
    return pd.DataFrame(records)


def load_h2_annual_data() -> pd.DataFrame:
    """One row per calendar year (2001-2025): S&P 500 volatility (annualized
    standard deviation of monthly % returns — the closest equivalent to
    daily-return volatility this dataset supports, since only monthly S&P
    closes are available) against the magnitude of that year's gas-price
    swing (absolute year-over-year % change in the average CA gas price).
    Ports the annual-level analysis from the team's exploratory notebook to
    this app's own data source."""
    monthly = load_monthly_market_data()
    monthly["SP_MoM"] = monthly["SP_Close"].pct_change() * 100
    annual_volatility = (
        monthly.groupby(monthly["Date"].dt.year)["SP_MoM"]
        .std()
        .mul(np.sqrt(12))
        .rename("SP_Volatility")
        .reset_index()
        .rename(columns={"Date": "Year"})
    )

    base_path = os.path.dirname(__file__)
    gas = pd.read_excel(
        os.path.join(base_path, "SP500_GasPrices_Tableau_v3.xlsx"),
        sheet_name="Annual_Data",
        engine="openpyxl",
    )
    gas = gas.rename(columns={
        "Avg CA Gas Price ($/gal)": "Gas_Price",
        "Avg S&P 500 Close": "SP_Avg",
    })
    gas = gas.dropna(subset=["Year", "Gas_Price", "SP_Avg"]).sort_values("Year")
    gas["Year"] = gas["Year"].astype(int)
    gas["Gas_Change"] = gas["Gas_Price"].pct_change() * 100
    gas["Gas_Swing"] = gas["Gas_Change"].abs()
    gas["SP_Return"] = gas["SP_Avg"].pct_change() * 100

    events = pd.read_excel(
        os.path.join(base_path, "Major_Global_Events_2001_Present (1).xlsx"),
        sheet_name="Global Events",
        engine="openpyxl",
    ).dropna(subset=["Event Name", "Start Date"])
    events["Start Date"] = pd.to_datetime(events["Start Date"])
    events["Category"] = events["Event Name"].map(EVENT_CATEGORIES).fillna("Other")
    # One event per year (the earliest by start date) so each year can be
    # highlighted from a single dropdown entry, same as the notebook.
    first_event_per_year = (
        events.sort_values("Start Date")
        .groupby(events["Start Date"].dt.year)
        .first()[["Event Name", "Category"]]
        .rename(columns={"Event Name": "Event"})
    )

    df = gas.merge(annual_volatility, on="Year", how="inner")
    df = df.merge(first_event_per_year, left_on="Year", right_index=True, how="left")
    df["Event"] = df["Event"].fillna("No major event")
    df["Category"] = df["Category"].fillna("Other year")
    df["Event_Status"] = np.where(df["Event"].eq("No major event"), "Other year", "Major-event year")
    df = df.dropna(subset=["SP_Volatility", "Gas_Swing"]).sort_values("Year").reset_index(drop=True)
    df["Year_Date"] = pd.to_datetime(df["Year"].astype(str) + "-01-01")
    return df


def compute_h2_correlation(annual_h2: pd.DataFrame) -> dict:
    result = pearsonr(annual_h2["SP_Volatility"], annual_h2["Gas_Swing"])
    ci = result.confidence_interval(confidence_level=0.95)
    return {
        "r": float(result.statistic),
        "p_value": float(result.pvalue),
        "ci_low": float(ci.low),
        "ci_high": float(ci.high),
        "n": len(annual_h2),
    }


def make_chart_h2_scatter(annual_h2: pd.DataFrame, stats: dict, year_brush: alt.Parameter, event_selector: alt.Parameter) -> alt.LayerChart:
    base = alt.Chart(annual_h2).transform_filter(year_brush)

    trend = base.transform_regression("SP_Volatility", "Gas_Swing").mark_line(
        color=TEXT_COLOR, strokeWidth=2.5, strokeDash=[7, 5], opacity=0.75,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q")

    points = base.mark_circle(size=150, strokeWidth=1.5).encode(
        x=alt.X("SP_Volatility:Q", title="S&P 500 annualized volatility (%)", scale=alt.Scale(zero=True)),
        y=alt.Y("Gas_Swing:Q", title="Magnitude of annual CA gas-price change (%)", scale=alt.Scale(zero=True)),
        color=alt.Color(
            "Event_Status:N",
            title=None,
            legend=alt.Legend(orient="bottom"),
            scale=alt.Scale(domain=["Major-event year", "Other year"], range=[MAJOR_EVENT_COLOR, OTHER_YEAR_COLOR]),
        ),
        opacity=alt.condition(
            "SelectedEvent == 'All years' || datum.Event == SelectedEvent",
            alt.value(0.95),
            alt.value(0.15),
        ),
        stroke=alt.condition(
            "SelectedEvent != 'All years' && datum.Event == SelectedEvent",
            alt.value("#ffffff"),
            alt.value("transparent"),
        ),
        tooltip=[
            alt.Tooltip("Event:N", title="Event"),
            alt.Tooltip("Year:O", title="Year"),
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("SP_Volatility:Q", title="S&P volatility (%)", format=".1f"),
            alt.Tooltip("Gas_Swing:Q", title="|Gas-price change| (%)", format=".1f"),
            alt.Tooltip("Gas_Change:Q", title="Signed gas change (%)", format="+.1f"),
            alt.Tooltip("SP_Return:Q", title="S&P annual return (%)", format="+.1f"),
            alt.Tooltip("Gas_Price:Q", title="Gas price ($/gallon)", format=".2f"),
        ],
    ).add_params(year_brush, event_selector)

    selected_label = base.transform_filter(
        "SelectedEvent != 'All years' && datum.Event == SelectedEvent"
    ).mark_text(
        align="left", baseline="bottom", dx=8, dy=-8, fontSize=11, fontWeight="bold", color=TEXT_COLOR, limit=260,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q", text="Event:N")

    return (trend + points + selected_label).properties(
        title=alt.TitleParams(
            text="Do Volatile Stock-Market Years Coincide With Larger Gas-Price Swings?",
            subtitle=[
                "Each point is one year (2001-2025); the dashed line is the overall linear trend.",
                f"Pearson r = {stats['r']:.2f}, 95% CI [{stats['ci_low']:.2f}, {stats['ci_high']:.2f}], "
                f"p = {stats['p_value']:.3f}, n = {stats['n']}.",
            ],
        ),
        width="container",
        height=340,
    )


def make_chart_h2_scatter_readout(annual_h2: pd.DataFrame, year_brush: alt.Parameter) -> alt.LayerChart:
    """Small info strip mounted above the scatter: the currently-selected
    year range and the trend-line slope for that range, both recomputed live
    as the timeline brush changes — makes the effect of dragging visible as
    text, not just a shifting dashed line."""
    base = alt.Chart(annual_h2).transform_filter(year_brush)

    slope = base.transform_regression(
        "SP_Volatility", "Gas_Swing", params=True
    ).transform_calculate(
        slope_text="'Trend-line slope: ' + format(datum.coef[1], '.2f')"
    ).mark_text(align="left", fontSize=13, fontWeight="bold", color=TEXT_COLOR).encode(text="slope_text:N")

    year_range = base.transform_aggregate(
        min_year="min(Year)", max_year="max(Year)"
    ).transform_calculate(
        range_text="'Selected years: ' + datum.min_year + '–' + datum.max_year"
    ).mark_text(align="left", dx=220, fontSize=13, color=MUTED_COLOR).encode(text="range_text:N")

    return (slope + year_range).add_params(year_brush).properties(width="container", height=30)


def make_chart_h2_timeline(annual_h2: pd.DataFrame, year_brush: alt.Parameter, metric_selection: alt.Parameter, event_selector: alt.Parameter) -> alt.LayerChart:
    timeline_df = annual_h2.melt(
        id_vars=["Year", "Year_Date", "Event", "Category"],
        value_vars=["SP_Volatility", "Gas_Swing"],
        var_name="Metric",
        value_name="Percent",
    )
    timeline_df["Metric"] = timeline_df["Metric"].map({
        "SP_Volatility": "S&P annualized volatility",
        "Gas_Swing": "|CA gas price YoY change|",
    })

    metric_domain = ["S&P annualized volatility", "|CA gas price YoY change|"]
    metric_color = alt.Color(
        "Metric:N",
        title=None,
        legend=alt.Legend(orient="bottom"),
        scale=alt.Scale(domain=metric_domain, range=[SP_COLOR, GAS_COLOR]),
    )

    lines = alt.Chart(timeline_df).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Year_Date:T", title="Year", axis=alt.Axis(format="%Y", tickCount=13)),
        y=alt.Y("Percent:Q", title="Annual magnitude (%)", scale=alt.Scale(zero=True)),
        color=metric_color,
        detail="Metric:N",
        opacity=alt.condition(metric_selection, alt.value(1), alt.value(0.15)),
    ).add_params(year_brush, metric_selection, event_selector)

    points = alt.Chart(timeline_df).mark_circle(size=70).encode(
        x="Year_Date:T",
        y="Percent:Q",
        color=alt.Color("Metric:N", scale=alt.Scale(domain=metric_domain, range=[SP_COLOR, GAS_COLOR]), legend=None),
        opacity=alt.condition(metric_selection, alt.value(0.95), alt.value(0.15)),
        tooltip=[
            alt.Tooltip("Event:N", title="Event"),
            alt.Tooltip("Year:O", title="Year"),
            alt.Tooltip("Metric:N", title="Metric"),
            alt.Tooltip("Percent:Q", title="Value (%)", format=".1f"),
        ],
    )

    selected_rule = alt.Chart(annual_h2).transform_filter(
        "SelectedEvent != 'All years' && datum.Event == SelectedEvent"
    ).mark_rule(color="#ffffff", strokeWidth=2, strokeDash=[5, 4]).encode(
        x="Year_Date:T",
        tooltip=[alt.Tooltip("Event:N", title="Selected event"), alt.Tooltip("Year:O", title="Year")],
    )

    return (lines + points + selected_rule).properties(
        title=alt.TitleParams(
            text="Annual Context and Time-Window Filter",
            subtitle=[
                "Both measures use the same percentage scale — no dual axes.",
                "Click a metric in the legend to emphasize or de-emphasize it.",
            ],
        ),
        width="container",
        height=170,
    )


def make_chart_h2_combined(annual_h2: pd.DataFrame, stats: dict) -> alt.VConcatChart:
    """Kept as the single-mount version used by the Explore section's
    alternate view — the primary Hypothesis 2 narrative uses the split specs
    below instead, so its dropdown can sit between the two panels."""
    year_brush = alt.selection_interval(encodings=["x"], name="YearWindow")
    metric_selection = alt.selection_point(fields=["Metric"], bind="legend", name="MetricSelection")
    event_selector = alt.param(
        name="SelectedEvent",
        value="All years",
        bind=alt.binding_select(
            options=["All years"] + sorted(
                annual_h2.loc[annual_h2["Event"].ne("No major event"), "Event"].unique().tolist()
            ),
            name="Highlight event: ",
        ),
    )

    scatter_chart = make_chart_h2_scatter(annual_h2, stats, year_brush, event_selector)
    timeline_chart = make_chart_h2_timeline(annual_h2, year_brush, metric_selection, event_selector)

    return alt.vconcat(scatter_chart, timeline_chart, spacing=28).resolve_scale(
        color="independent"
    ).properties(
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart_h2_scatter_ranged(annual_h2: pd.DataFrame, stats: dict, year_min: alt.Parameter, year_max: alt.Parameter, event_selector: alt.Parameter) -> alt.LayerChart:
    """Same scatter as make_chart_h2_scatter, but filtered by two plain
    YearMin/YearMax params instead of a drag-to-select interval selection.
    Split-mounted views can't share an interval selection's internal
    "_store" dataset reliably (confirmed empirically — writing into it via
    the Vega View API updates the dataset's contents but doesn't invalidate
    the downstream filter, since Vega-Lite's compiled dataflow drives that
    filter from the selection's tuple signal, not the store directly), so
    year-range filtering here uses two ordinary signals instead, synced the
    same proven way SelectedEvent already is."""
    year_filter = "datum.Year >= YearMin && datum.Year <= YearMax"
    base = alt.Chart(annual_h2).transform_filter(year_filter)

    trend = base.transform_regression("SP_Volatility", "Gas_Swing").mark_line(
        color=TEXT_COLOR, strokeWidth=2.5, strokeDash=[7, 5], opacity=0.75,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q")

    points = base.mark_circle(size=150, strokeWidth=1.5).encode(
        x=alt.X("SP_Volatility:Q", title="S&P 500 annualized volatility (%)", scale=alt.Scale(zero=True)),
        y=alt.Y("Gas_Swing:Q", title="Magnitude of annual CA gas-price change (%)", scale=alt.Scale(zero=True)),
        color=alt.Color(
            "Event_Status:N",
            title=None,
            legend=alt.Legend(orient="bottom"),
            scale=alt.Scale(domain=["Major-event year", "Other year"], range=[MAJOR_EVENT_COLOR, OTHER_YEAR_COLOR]),
        ),
        opacity=alt.condition(
            "SelectedEvent == 'All years' || datum.Event == SelectedEvent",
            alt.value(0.95),
            alt.value(0.15),
        ),
        stroke=alt.condition(
            "SelectedEvent != 'All years' && datum.Event == SelectedEvent",
            alt.value("#ffffff"),
            alt.value("transparent"),
        ),
        tooltip=[
            alt.Tooltip("Event:N", title="Event"),
            alt.Tooltip("Year:O", title="Year"),
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("SP_Volatility:Q", title="S&P volatility (%)", format=".1f"),
            alt.Tooltip("Gas_Swing:Q", title="|Gas-price change| (%)", format=".1f"),
            alt.Tooltip("Gas_Change:Q", title="Signed gas change (%)", format="+.1f"),
            alt.Tooltip("SP_Return:Q", title="S&P annual return (%)", format="+.1f"),
            alt.Tooltip("Gas_Price:Q", title="Gas price ($/gallon)", format=".2f"),
        ],
    ).add_params(year_min, year_max, event_selector)

    selected_label = base.transform_filter(
        "SelectedEvent != 'All years' && datum.Event == SelectedEvent"
    ).mark_text(
        align="left", baseline="bottom", dx=8, dy=-8, fontSize=11, fontWeight="bold", color=TEXT_COLOR, limit=260,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q", text="Event:N")

    return (trend + points + selected_label).properties(
        title=alt.TitleParams(
            text="Do Volatile Stock-Market Years Coincide With Larger Gas-Price Swings?",
            subtitle=[
                "Each point is one year (2001-2025); the dashed line is the overall linear trend.",
                f"Pearson r = {stats['r']:.2f}, 95% CI [{stats['ci_low']:.2f}, {stats['ci_high']:.2f}], "
                f"p = {stats['p_value']:.3f}, n = {stats['n']}.",
            ],
        ),
        width="container",
        height=340,
    )


def make_chart_h2_readout_ranged(annual_h2: pd.DataFrame, year_min: alt.Parameter, year_max: alt.Parameter) -> alt.LayerChart:
    """Small info strip above the scatter: the selected year range and the
    trend-line slope for that range, recomputed live from the YearMin/
    YearMax dropdowns."""
    year_filter = "datum.Year >= YearMin && datum.Year <= YearMax"
    base = alt.Chart(annual_h2).transform_filter(year_filter)

    slope = base.transform_regression(
        "SP_Volatility", "Gas_Swing", params=True
    ).transform_calculate(
        slope_text="'Trend-line slope: ' + format(datum.coef[1], '.2f')"
    ).mark_text(align="left", fontSize=13, fontWeight="bold", color=TEXT_COLOR).encode(text="slope_text:N")

    year_range = base.transform_aggregate(
        min_year="min(Year)", max_year="max(Year)"
    ).transform_calculate(
        range_text="'Selected years: ' + datum.min_year + '–' + datum.max_year"
    ).mark_text(align="left", dx=220, fontSize=13, color=MUTED_COLOR).encode(text="range_text:N")

    return (slope + year_range).add_params(year_min, year_max).properties(width="container", height=30)


def make_chart_h2_timeline_ranged(annual_h2: pd.DataFrame, metric_selection: alt.Parameter, event_selector: alt.Parameter) -> alt.LayerChart:
    """Full-context timeline (unfiltered) — the year-range dropdowns filter
    the scatter/readout above, not this chart, so it always shows the whole
    2001-2025 span for reference."""
    timeline_df = annual_h2.melt(
        id_vars=["Year", "Year_Date", "Event", "Category"],
        value_vars=["SP_Volatility", "Gas_Swing"],
        var_name="Metric",
        value_name="Percent",
    )
    timeline_df["Metric"] = timeline_df["Metric"].map({
        "SP_Volatility": "S&P annualized volatility",
        "Gas_Swing": "|CA gas price YoY change|",
    })

    metric_domain = ["S&P annualized volatility", "|CA gas price YoY change|"]
    metric_color = alt.Color(
        "Metric:N",
        title=None,
        legend=alt.Legend(orient="bottom"),
        scale=alt.Scale(domain=metric_domain, range=[SP_COLOR, GAS_COLOR]),
    )

    lines = alt.Chart(timeline_df).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Year_Date:T", title="Year", axis=alt.Axis(format="%Y", tickCount=13)),
        y=alt.Y("Percent:Q", title="Annual magnitude (%)", scale=alt.Scale(zero=True)),
        color=metric_color,
        detail="Metric:N",
        opacity=alt.condition(metric_selection, alt.value(1), alt.value(0.15)),
    ).add_params(metric_selection, event_selector)

    points = alt.Chart(timeline_df).mark_circle(size=70).encode(
        x="Year_Date:T",
        y="Percent:Q",
        color=alt.Color("Metric:N", scale=alt.Scale(domain=metric_domain, range=[SP_COLOR, GAS_COLOR]), legend=None),
        opacity=alt.condition(metric_selection, alt.value(0.95), alt.value(0.15)),
        tooltip=[
            alt.Tooltip("Event:N", title="Event"),
            alt.Tooltip("Year:O", title="Year"),
            alt.Tooltip("Metric:N", title="Metric"),
            alt.Tooltip("Percent:Q", title="Value (%)", format=".1f"),
        ],
    )

    selected_rule = alt.Chart(annual_h2).transform_filter(
        "SelectedEvent != 'All years' && datum.Event == SelectedEvent"
    ).mark_rule(color="#ffffff", strokeWidth=2, strokeDash=[5, 4]).encode(
        x="Year_Date:T",
        tooltip=[alt.Tooltip("Event:N", title="Selected event"), alt.Tooltip("Year:O", title="Year")],
    )

    return (lines + points + selected_rule).properties(
        title=alt.TitleParams(
            text="Annual Context",
            subtitle=[
                "Both measures use the same percentage scale — no dual axes.",
                "Click a metric in the legend to emphasize or de-emphasize it.",
            ],
        ),
        width="container",
        height=170,
    )


def make_chart_h2_scatter_spec(annual_h2: pd.DataFrame, stats: dict) -> alt.LayerChart:
    """Standalone scatter, mounted in its own vega-embed view so the
    'Highlight event' and year-range dropdowns (hand-authored JS, not
    Vega-Lite's auto-rendered bindings) can sit between it and the timeline
    instead of below everything."""
    year_min = alt.param(name="YearMin", value=int(annual_h2["Year"].min()))
    year_max = alt.param(name="YearMax", value=int(annual_h2["Year"].max()))
    event_selector = alt.param(name="SelectedEvent", value="All years")
    return make_chart_h2_scatter_ranged(annual_h2, stats, year_min, year_max, event_selector)


def make_chart_h2_timeline_spec(annual_h2: pd.DataFrame) -> alt.LayerChart:
    metric_selection = alt.selection_point(fields=["Metric"], bind="legend", name="MetricSelection")
    event_selector = alt.param(name="SelectedEvent", value="All years")
    return make_chart_h2_timeline_ranged(annual_h2, metric_selection, event_selector)


def make_chart_h2_readout_spec(annual_h2: pd.DataFrame) -> alt.LayerChart:
    year_min = alt.param(name="YearMin", value=int(annual_h2["Year"].min()))
    year_max = alt.param(name="YearMax", value=int(annual_h2["Year"].max()))
    return make_chart_h2_readout_ranged(annual_h2, year_min, year_max)


DOWNTURN_EPISODES = {
    "Dot-Com Crash": ("2000-06-01", "2003-06-30"),
    "Financial Crisis": ("2007-06-01", "2009-12-31"),
    "COVID-19 Crash": ("2019-10-01", "2020-12-31"),
    "2022 Selloff": ("2021-10-01", "2023-06-30"),
}


def load_downturn_trough_data() -> dict:
    """For each major market downturn, find the month gas prices bottomed
    out and the month the S&P 500 bottomed out, so we can see which one
    dipped first without needing any statistics vocabulary."""
    monthly = load_monthly_market_data()

    points, spans = [], []
    for episode, (start, end) in DOWNTURN_EPISODES.items():
        window = monthly[(monthly["Date"] >= start) & (monthly["Date"] <= end)]
        sp_row = window.loc[window["SP_Close"].idxmin()]
        gas_row = window.loc[window["Gas_Price"].idxmin()]

        gap_months = (sp_row["Date"].year * 12 + sp_row["Date"].month) - (
            gas_row["Date"].year * 12 + gas_row["Date"].month
        )
        if gap_months > 0:
            label = f"Gas dipped first, {gap_months} month{'s' if gap_months != 1 else ''} earlier"
        elif gap_months < 0:
            label = f"S&P 500 dipped first, {-gap_months} month{'s' if gap_months != -1 else ''} earlier"
        else:
            label = "Both dipped the same month"

        points.append({"Episode": episode, "Market": "Gas Price", "Trough Date": gas_row["Date"]})
        points.append({"Episode": episode, "Market": "S&P 500", "Trough Date": sp_row["Date"]})
        spans.append({
            "Episode": episode,
            "start_date": min(gas_row["Date"], sp_row["Date"]),
            "end_date": max(gas_row["Date"], sp_row["Date"]),
            "mid_date": gas_row["Date"] + (sp_row["Date"] - gas_row["Date"]) / 2,
            "Label": label,
        })

    return {"points": pd.DataFrame(points), "spans": pd.DataFrame(spans)}


def compute_crisis_years() -> dict:
    """Which calendar years count as a "crisis year" (for Hypothesis 3 and
    the classification strip), derived directly from the same downturn
    episodes and empirically-found trough dates used in Hypothesis 1 —
    a year counts if it falls between when gas and the S&P actually
    bottomed out for that episode. This replaces a separate, hand-picked
    crisis-year list so every hypothesis uses one consistent definition of
    "crisis" instead of two different, unreconciled ones."""
    spans = load_downturn_trough_data()["spans"]
    year_map = {}
    for _, row in spans.iterrows():
        for year in range(row["start_date"].year, row["end_date"].year + 1):
            year_map[year] = row["Episode"]
    return year_map


CRISIS_YEAR_MAP = compute_crisis_years()


def make_chart_h1_timeline(points: pd.DataFrame, spans: pd.DataFrame) -> alt.LayerChart:
    episode_order = list(DOWNTURN_EPISODES.keys())
    market_color = alt.Color(
        "Market:N",
        title="Market",
        legend=alt.Legend(orient="bottom"),
        scale=alt.Scale(domain=["S&P 500", "Gas Price"], range=[SP_COLOR, GAS_COLOR]),
    )

    connector = alt.Chart(spans).mark_rule(strokeWidth=3, color="#b0b0b0").encode(
        y=alt.Y("Episode:N", sort=episode_order, title=None),
        x=alt.X("start_date:T", title="Month the Market Bottomed Out"),
        x2="end_date:T",
    )

    dots = alt.Chart(points).mark_circle(size=260, stroke="white", strokeWidth=1).encode(
        y=alt.Y("Episode:N", sort=episode_order, title=None),
        x=alt.X("Trough Date:T"),
        color=market_color,
        tooltip=["Episode:N", "Market:N", alt.Tooltip("Trough Date:T", format="%B %Y")],
    )

    labels = alt.Chart(spans).mark_text(dy=-22, fontSize=12, fontWeight="bold", color=TEXT_COLOR).encode(
        y=alt.Y("Episode:N", sort=episode_order),
        x=alt.X("mid_date:T"),
        text="Label:N",
    )

    return (connector + dots + labels).properties(
        title="Who Dipped First? Gas Price vs. S&P 500 Bottom, by Downturn",
        width="container",
        height=240,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart_event_window(event_window: pd.DataFrame, correlations: pd.DataFrame) -> alt.VConcatChart:
    """Timeline view: gas volatility as bars (right axis) and S&P volatility
    as lollipops (left axis, zero-anchored to match the bars' visual
    language) sharing one time axis, so viewers can compare whether tall
    bars and tall lollipops tend to line up at the same events. No smoothed
    trend line — it added visual weight without helping the actual
    side-by-side comparison, which is the point of this view."""
    window_select = alt.selection_point(
        fields=["Window"],
        bind=alt.binding_select(options=EVENT_WINDOW_MONTHS, name="Months after event start: "),
        value=6,
    )

    category_domain = sorted(event_window["Category"].unique())
    color = alt.Color(
        "Category:N",
        title="Event Category",
        legend=alt.Legend(orient="bottom", columns=2, labelLimit=160, symbolLimit=20),
        scale=alt.Scale(domain=category_domain),
    )
    tooltip = [
        "Event:N",
        "Category:N",
        alt.Tooltip("Start Date:T", format="%b %Y"),
        "Window:O",
        alt.Tooltip("Volatility:Q", format=".1f", title="Volatility (std. dev. of monthly returns, %)"),
    ]

    base_gas = alt.Chart(event_window).transform_filter(
        alt.FieldEqualPredicate(field="Market", equal="Gas Price")
    ).transform_filter(window_select)

    base_sp = alt.Chart(event_window).transform_filter(
        alt.FieldEqualPredicate(field="Market", equal="S&P 500")
    ).transform_filter(window_select)

    sp_axis_color = SP_COLOR
    gas_axis_color = GAS_COLOR

    gas_bars = base_gas.mark_bar(opacity=0.35, color=gas_axis_color, size=5).encode(
        x=alt.X("Start Date:T", title="Event Start Date"),
        y=alt.Y(
            "Volatility:Q",
            title="Gas Price Volatility (%)",
            axis=alt.Axis(orient="right", titleColor=gas_axis_color, labelColor=gas_axis_color),
        ),
        tooltip=tooltip,
    ).add_params(window_select)

    sp_rule = base_sp.mark_rule(strokeWidth=2).encode(
        x=alt.X("Start Date:T"),
        y=alt.Y(
            "Volatility:Q",
            title="S&P 500 Volatility (%)",
            axis=alt.Axis(titleColor=sp_axis_color, labelColor=sp_axis_color),
        ),
        y2=alt.Y2(datum=0),
        color=color,
        tooltip=tooltip,
    )

    sp_point = base_sp.mark_circle(size=80, stroke="white", strokeWidth=0.6).encode(
        x=alt.X("Start Date:T"),
        # No y-title here: shares S&P 500's axis/scale with sp_rule above
        # (grouped in one sub-layer so Vega-Lite renders a single axis
        # instead of one per layer, which was drawing the title twice).
        y=alt.Y("Volatility:Q", axis=None),
        color=color,
        tooltip=tooltip,
    )

    sp_group = (sp_rule + sp_point)
    combined = (gas_bars + sp_group).resolve_scale(y="independent").properties(
        title=alt.TitleParams(
            text="S&P 500 Volatility (orange, left axis) vs. Gas Price Volatility (blue, right axis)",
            subtitle=[
                "Volatility = standard deviation of monthly % returns during the selected window.",
                "Left axis = S&P 500. Right axis = gas prices.",
            ],
        ),
        width="container",
        height=420,
    )

    annotation = alt.Chart(correlations).transform_filter(window_select).mark_text(
        fontSize=13,
        fontStyle="italic",
        color=MUTED_COLOR,
    ).encode(
        text="Label:N",
    ).properties(width="container", height=30)

    return alt.vconcat(combined, annotation).properties(
        title="S&P 500 Volatility vs. Gas Price Volatility After Major Events — Timeline View",
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart_event_scatter(event_window: pd.DataFrame, correlations: pd.DataFrame) -> alt.VConcatChart:
    """Scatter view of the same volatility data: one dot per event, gas
    volatility on the x-axis and S&P volatility on the y-axis, both on the
    same shared plane (no dual axes to reconcile). An upward-sloping cluster
    means the two tend to get volatile together; a fitted trend line makes
    that slope explicit."""
    window_select = alt.selection_point(
        fields=["Window"],
        bind=alt.binding_select(options=EVENT_WINDOW_MONTHS, name="Months after event start: "),
        value=6,
    )

    wide = event_window.pivot(
        index=["Event", "Category", "Start Date", "Window"], columns="Market", values="Volatility"
    ).reset_index()
    wide = wide.rename(columns={"S&P 500": "SP_Volatility", "Gas Price": "Gas_Volatility"})
    wide = wide.dropna(subset=["SP_Volatility", "Gas_Volatility"])

    category_domain = sorted(wide["Category"].unique())
    color = alt.Color(
        "Category:N",
        title="Event Category",
        legend=alt.Legend(orient="bottom", columns=2, labelLimit=160, symbolLimit=20),
        scale=alt.Scale(domain=category_domain),
    )
    tooltip = [
        "Event:N",
        "Category:N",
        alt.Tooltip("Start Date:T", format="%b %Y"),
        "Window:O",
        alt.Tooltip("Gas_Volatility:Q", format=".1f", title="Gas Price Volatility (%)"),
        alt.Tooltip("SP_Volatility:Q", format=".1f", title="S&P 500 Volatility (%)"),
    ]

    base = alt.Chart(wide).transform_filter(window_select)

    points = base.mark_circle(size=140, stroke="white", strokeWidth=0.6).encode(
        x=alt.X("Gas_Volatility:Q", title="Gas Price Volatility (%)"),
        y=alt.Y("SP_Volatility:Q", title="S&P 500 Volatility (%)"),
        color=color,
        tooltip=tooltip,
    ).add_params(window_select)

    trend = base.transform_regression("Gas_Volatility", "SP_Volatility").mark_line(
        color=SP_COLOR, strokeWidth=3, strokeDash=[6, 3]
    ).encode(
        x="Gas_Volatility:Q",
        y="SP_Volatility:Q",
    )

    combined = (points + trend).properties(
        title=alt.TitleParams(
            text="S&P 500 Volatility vs. Gas Price Volatility, by Event",
            subtitle=["Each dot is one event. An upward-sloping cluster means the two tend to get volatile together."],
        ),
        width="container",
        height=460,
    )

    annotation = alt.Chart(correlations).transform_filter(window_select).mark_text(
        fontSize=13,
        fontStyle="italic",
        color=MUTED_COLOR,
    ).encode(
        text="Label:N",
    ).properties(width="container", height=30)

    return alt.vconcat(combined, annotation).properties(
        title="S&P 500 Volatility vs. Gas Price Volatility After Major Events — Scatter View",
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart_event_dumbbell(event_window: pd.DataFrame) -> alt.LayerChart:
    """Ported from a teammate's (Prathik's) prototype: one row per event,
    connecting S&P 500 volatility and gas-price volatility for the selected
    window so the gap between them is a visible line, not just two nearby
    dots. His original version hand-typed 9 illustrative events; this one
    reuses the same real 52-event dataset (with real dates/categories) that
    the rest of the site's event-window charts already use, via
    load_event_window_data(), instead of a second, inconsistent event list."""
    wide = event_window.pivot(
        index=["Event", "Category", "Start Date", "Window"], columns="Market", values="Volatility"
    ).reset_index()
    wide = wide.rename(columns={"S&P 500": "SP_Volatility", "Gas Price": "Gas_Volatility"})
    wide = wide.dropna(subset=["SP_Volatility", "Gas_Volatility"])
    wide["Display_Label"] = wide["Start Date"].dt.strftime("%Y-%m") + "  —  " + wide["Event"]

    window_select = alt.selection_point(
        fields=["Window"],
        bind=alt.binding_select(options=EVENT_WINDOW_MONTHS, name="Months after event start: "),
        value=6,
    )
    category_options = ["All categories"] + sorted(wide["Category"].unique().tolist())
    category_filter = alt.param(
        name="CategoryFilter",
        value="All categories",
        bind=alt.binding_select(options=category_options, name="Event category: "),
    )
    category_expr = "CategoryFilter == 'All categories' || datum.Category == CategoryFilter"

    # Keyed on Event + Start Date, not Event alone: the events file has one
    # genuine name collision ("U.S. Presidential Election (Trump Win)" for
    # both 2016 and 2024) — matching by name only would make hovering/
    # clicking one election's row also highlight the other.
    hover = alt.selection_point(fields=["Event", "Start Date"], on="pointerover", clear="pointerout", empty=False)
    selected = alt.selection_point(fields=["Event", "Start Date"], on="click", clear="dblclick", empty=True)

    y_enc = alt.Y(
        "Display_Label:N",
        title=None,
        sort=alt.SortField(field="Start Date", order="descending"),
        axis=alt.Axis(labelLimit=360, labelPadding=10, ticks=False, domain=False),
    )
    tooltip = [
        alt.Tooltip("Event:N", title="Event"),
        alt.Tooltip("Start Date:T", title="Start date", format="%b %d, %Y"),
        alt.Tooltip("Category:N", title="Category"),
        alt.Tooltip("Window:O", title="Window (months)"),
        alt.Tooltip("SP_Volatility:Q", title="S&P 500 volatility (%)", format=".1f"),
        alt.Tooltip("Gas_Volatility:Q", title="Gas-price volatility (%)", format=".1f"),
    ]

    connectors = alt.Chart(wide).transform_filter(window_select).transform_filter(category_expr).mark_rule(
        color=MUTED_COLOR, strokeWidth=2,
    ).encode(
        y=y_enc,
        x=alt.X("SP_Volatility:Q", title="Volatility during selected window (%)", scale=alt.Scale(zero=True, nice=True)),
        x2="Gas_Volatility:Q",
        opacity=alt.condition(selected, alt.value(0.75), alt.value(0.18)),
        tooltip=tooltip,
    ).add_params(window_select, category_filter)

    long = wide.melt(
        id_vars=["Event", "Category", "Start Date", "Window", "Display_Label"],
        value_vars=["SP_Volatility", "Gas_Volatility"],
        var_name="Market", value_name="Volatility",
    )
    long["Market"] = long["Market"].replace({"SP_Volatility": "S&P 500", "Gas_Volatility": "CA gas prices"})

    points = alt.Chart(long).transform_filter(window_select).transform_filter(category_expr).mark_point(
        filled=True, stroke=TEXT_COLOR, strokeWidth=1.1,
    ).encode(
        y=y_enc,
        x=alt.X("Volatility:Q", scale=alt.Scale(zero=True, nice=True)),
        color=alt.Color(
            "Market:N", title=None,
            scale=alt.Scale(domain=["S&P 500", "CA gas prices"], range=[SP_COLOR, GAS_COLOR]),
            legend=alt.Legend(orient="top", direction="horizontal", symbolSize=140),
        ),
        shape=alt.Shape(
            "Market:N", title=None,
            scale=alt.Scale(domain=["S&P 500", "CA gas prices"], range=["circle", "diamond"]),
            legend=None,
        ),
        size=alt.condition(hover, alt.value(190), alt.value(110)),
        opacity=alt.condition(selected, alt.value(1), alt.value(0.16)),
        tooltip=[
            alt.Tooltip("Event:N", title="Event"),
            alt.Tooltip("Start Date:T", title="Start date", format="%b %d, %Y"),
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Market:N", title="Measure"),
            alt.Tooltip("Volatility:Q", title="Volatility (%)", format=".1f"),
            alt.Tooltip("Window:O", title="Window (months)"),
        ],
    ).add_params(hover, selected)

    return alt.layer(connectors, points).properties(
        title=alt.TitleParams(
            text="How Volatile Were Stocks and Gas Prices After Each Major Event?",
            subtitle=[
                "All 52 tracked events, ordered by date. Farther right means more volatility; shorter connectors mean more similar reactions.",
                "Hover for exact values. Click an event to focus it; double-click to reset.",
            ],
        ),
        width="container",
        height=alt.Step(26),
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart1(long_index: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(long_index)
    series_colors = alt.Scale(domain=["S&P 500", "Gas Prices"], range=[SP_COLOR, GAS_COLOR])

    sp500 = base.transform_filter(
        {"field": "Type", "equal": "S&P 500"}
    ).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Index_Value:Q", title="S&P 500 index"),
        color=alt.Color("Type:N", title="Series", scale=series_colors, legend=alt.Legend(orient="bottom")),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Index_Value:Q", format=".1f"), "Event:N"],
    )

    gas = base.transform_filter(
        {"field": "Type", "equal": "Gas Prices"}
    ).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y(
            "Gas_Price:Q",
            title="Gas price ($/gallon)",
            axis=alt.Axis(orient="right"),
        ),
        color=alt.Color("Type:N", title="Series", scale=series_colors, legend=None),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Gas_Price:Q", title="Gas price ($/gallon)", format=".2f"), "Event:N"],
    )

    return (sp500 + gas).resolve_scale(y="independent").properties(
        title="Indexed S&P 500 vs Gas Prices",
        width="container",
        height=360,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart2(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series", legend=alt.Legend(orient="bottom")),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Yearly Percent Change: S&P 500 vs Gas Prices",
        width="container",
        height=360,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart3(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_bar(size=11).encode(
        x=alt.X("Year:O", title="Year", scale=alt.Scale(paddingInner=0.15), axis=alt.Axis(labelAngle=-45)),
        xOffset=alt.XOffset("Type:N"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color(
            "Type:N", title="Series",
            scale=alt.Scale(domain=["S&P 500 Return", "Gas Price Change"], range=[SP_COLOR, GAS_COLOR]),
            legend=alt.Legend(orient="bottom"),
        ),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Yearly Percent Change, Grouped by Series",
        width="container",
        height=360,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart4(annual: pd.DataFrame) -> alt.Chart:
    return alt.Chart(annual).mark_circle(size=100).encode(
        x=alt.X("Gas_Change:Q", title="Gas Price Change (%)"),
        y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)"),
        color=alt.Color("Event:N", title="Event", legend=alt.Legend(orient="bottom")),
        tooltip=["Year:O", "Event:N", alt.Tooltip("Gas_Change:Q", format=".1f"), alt.Tooltip("SP_Return:Q", format=".1f")],
    ).properties(
        title="S&P 500 Return vs Gas Price Change",
        width="container",
        height=360,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def prepare_direction_data(annual: pd.DataFrame) -> pd.DataFrame:
    df = annual.copy()
    same_direction = df["SP_Direction"].str.contains("Up") == df["Gas_Direction"].str.contains("Up")
    df["Direction"] = np.where(same_direction, "Same Direction", "Opposite Direction")
    df["Group"] = np.where(df["Event"] == "Normal Year", "Normal Years", "Crisis Years")
    return df


def make_chart_h3_split(annual: pd.DataFrame) -> alt.HConcatChart:
    direction_data = prepare_direction_data(annual)
    direction_color = alt.Color(
        "Direction:N",
        title=None,
        legend=alt.Legend(orient="bottom"),
        scale=alt.Scale(domain=["Same Direction", "Opposite Direction"], range=[POSITIVE_COLOR, NEGATIVE_COLOR]),
    )
    tooltip = [
        "Year:O",
        "Event:N",
        alt.Tooltip("Gas_Change:Q", format=".1f", title="Gas Price Change (%)"),
        alt.Tooltip("SP_Return:Q", format=".1f", title="S&P 500 Return (%)"),
    ]

    def group_panel(group_name: str) -> alt.LayerChart:
        sub = direction_data[direction_data["Group"] == group_name]
        pct_together = (sub["Direction"] == "Same Direction").mean() * 100
        year_list = ", ".join(str(y) for y in sorted(sub["Year"].tolist()))

        base = alt.Chart(sub)
        zero_x = alt.Chart(pd.DataFrame({"z": [0]})).mark_rule(color="#ccc", strokeDash=[4, 4]).encode(x="z:Q")
        zero_y = alt.Chart(pd.DataFrame({"z": [0]})).mark_rule(color="#ccc", strokeDash=[4, 4]).encode(y="z:Q")
        points = base.mark_circle(size=140, stroke="white", strokeWidth=0.5).encode(
            x=alt.X("Gas_Change:Q", title="Gas Price Change (%)", scale=alt.Scale(domain=[-45, 45])),
            y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)", scale=alt.Scale(domain=[-45, 45])),
            color=direction_color,
            tooltip=tooltip,
        )
        labels = base.mark_text(dy=-14, fontSize=9.5, color=TEXT_COLOR).encode(
            x=alt.X("Gas_Change:Q", scale=alt.Scale(domain=[-45, 45])),
            y=alt.Y("SP_Return:Q", scale=alt.Scale(domain=[-45, 45])),
            text=alt.Text("Year:O"),
        )

        return (zero_x + zero_y + points + labels).properties(
            title=alt.TitleParams(
                text=group_name,
                subtitle=[
                    f"{pct_together:.0f}% of years moved in the same direction",
                    f"Years: {year_list}",
                ],
                subtitleFontSize=10.5,
            ),
            width="container",
            height=440,
        )

    return alt.hconcat(
        group_panel("Normal Years"),
        group_panel("Crisis Years"),
    ).properties(
        title="Do Gas Prices and the S&P 500 Move Together? Normal Years vs. Crisis Years",
    ).resolve_scale(color="shared")


def compute_h3_significance(direction_data: pd.DataFrame) -> dict:
    """Fisher's exact test + Wilson 95% confidence intervals comparing how
    often normal vs. crisis years move in the same direction — tests
    whether the gap we see could plausibly just be chance, given how few
    years of data exist (only 8 crisis years total)."""

    def wilson_ci(count: int, n: int, z: float = 1.96) -> tuple:
        if n == 0:
            return (0.0, 0.0)
        phat = count / n
        denom = 1 + z ** 2 / n
        center = (phat + z ** 2 / (2 * n)) / denom
        half = z * np.sqrt(phat * (1 - phat) / n + z ** 2 / (4 * n * n)) / denom
        return (max(0.0, center - half) * 100, min(1.0, center + half) * 100)

    normal = direction_data[direction_data["Group"] == "Normal Years"]
    crisis = direction_data[direction_data["Group"] == "Crisis Years"]

    normal_same = int((normal["Direction"] == "Same Direction").sum())
    crisis_same = int((crisis["Direction"] == "Same Direction").sum())
    normal_total = len(normal)
    crisis_total = len(crisis)

    _, p_value = fisher_exact([
        [crisis_same, crisis_total - crisis_same],
        [normal_same, normal_total - normal_same],
    ])

    return {
        "normal_same": normal_same,
        "normal_total": normal_total,
        "crisis_same": crisis_same,
        "crisis_total": crisis_total,
        "normal_rate": normal_same / normal_total * 100,
        "crisis_rate": crisis_same / crisis_total * 100,
        "normal_ci": wilson_ci(normal_same, normal_total),
        "crisis_ci": wilson_ci(crisis_same, crisis_total),
        "p_value": p_value,
    }


def make_chart_h3_quadrant(annual: pd.DataFrame, view_group: alt.Parameter) -> alt.LayerChart:
    """A single combined scatter (all years at once) instead of two
    side-by-side panels: color-coded quadrant backgrounds label "same" vs.
    "opposite" directly on the plot, and point shape (circle vs. diamond)
    distinguishes normal from crisis years, so the question "do crisis-year
    diamonds cluster in the red zones?" can be read in one glance. Every
    point carries a permanent year label so "which dot is 2015" never
    requires a click or a detour to the classification strip."""
    direction_data = prepare_direction_data(annual)
    x_limit = max(10, np.ceil(direction_data["Gas_Change"].abs().max() / 5) * 5)
    y_limit = max(10, np.ceil(direction_data["SP_Return"].abs().max() / 5) * 5)

    direction_domain = ["Same Direction", "Opposite Direction"]
    direction_range = [POSITIVE_COLOR, NEGATIVE_COLOR]

    quadrants = pd.DataFrame([
        {"x1": 0, "x2": x_limit, "y1": 0, "y2": y_limit, "Quadrant": "Same Direction"},
        {"x1": -x_limit, "x2": 0, "y1": -y_limit, "y2": 0, "Quadrant": "Same Direction"},
        {"x1": -x_limit, "x2": 0, "y1": 0, "y2": y_limit, "Quadrant": "Opposite Direction"},
        {"x1": 0, "x2": x_limit, "y1": -y_limit, "y2": 0, "Quadrant": "Opposite Direction"},
    ])

    quadrant_bg = alt.Chart(quadrants).mark_rect(opacity=0.08).encode(
        x=alt.X("x1:Q", scale=alt.Scale(domain=[-x_limit, x_limit]), title="Gas Price Change (%)"),
        x2="x2:Q",
        y=alt.Y("y1:Q", scale=alt.Scale(domain=[-y_limit, y_limit]), title="S&P 500 Return (%)"),
        y2="y2:Q",
        color=alt.Color("Quadrant:N", scale=alt.Scale(domain=direction_domain, range=direction_range), legend=None),
    )

    zero_x = alt.Chart(pd.DataFrame({"z": [0]})).mark_rule(color="#ccc", strokeDash=[4, 4], opacity=0.6).encode(x="z:Q")
    zero_y = alt.Chart(pd.DataFrame({"z": [0]})).mark_rule(color="#ccc", strokeDash=[4, 4], opacity=0.6).encode(y="z:Q")

    view_filter = "ViewGroup == 'All Years' || datum.Group == ViewGroup"

    points = alt.Chart(direction_data).transform_filter(view_filter).mark_point(
        filled=True, strokeWidth=1.5, stroke="white", size=220,
    ).encode(
        x=alt.X("Gas_Change:Q", title="Gas Price Change (%)", scale=alt.Scale(domain=[-x_limit, x_limit])),
        y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)", scale=alt.Scale(domain=[-y_limit, y_limit])),
        color=alt.Color("Direction:N", title="Movement", legend=alt.Legend(orient="bottom"), scale=alt.Scale(domain=direction_domain, range=direction_range)),
        shape=alt.Shape("Group:N", title="Year Type", legend=alt.Legend(orient="bottom"), scale=alt.Scale(domain=["Normal Years", "Crisis Years"], range=["circle", "diamond"])),
        tooltip=[
            "Year:O", "Event:N", "Group:N",
            alt.Tooltip("Gas_Change:Q", format="+.1f", title="Gas Price Change (%)"),
            alt.Tooltip("SP_Return:Q", format="+.1f", title="S&P 500 Return (%)"),
            "Direction:N",
        ],
    ).add_params(view_group)

    year_labels = alt.Chart(direction_data).transform_filter(view_filter).mark_text(
        align="left", dx=8, dy=-8, fontSize=9.5, color=TEXT_COLOR, opacity=0.85,
    ).encode(
        x=alt.X("Gas_Change:Q", scale=alt.Scale(domain=[-x_limit, x_limit])),
        y=alt.Y("SP_Return:Q", scale=alt.Scale(domain=[-y_limit, y_limit])),
        text="Year:O",
    )

    return (quadrant_bg + zero_x + zero_y + points + year_labels).resolve_scale(color="independent").properties(
        title=alt.TitleParams(
            text="How Did Gas Prices and the S&P 500 Move Each Year?",
            subtitle=[
                "Green quadrants = moved the same direction. Red quadrants = moved opposite.",
                "Circles = normal years, diamonds = crisis years — every point is labeled with its year.",
            ],
        ),
        width="container",
        height=380,
    )


def make_chart_h3_quadrant_spec(annual: pd.DataFrame) -> alt.LayerChart:
    view_group = alt.param(name="ViewGroup", value="All Years")
    return make_chart_h3_quadrant(annual, view_group)


def make_chart_crisis_timeline(annual: pd.DataFrame, view_group: alt.Parameter) -> alt.Chart:
    """A single-row, color-coded strip showing exactly which years are
    classified as which kind of year, and why — so "crisis year" isn't an
    unexplained label attached to the chart below. Responds to the same
    "Show years" control as the quadrant scatter by dimming years outside
    the selected group."""
    strip_data = prepare_direction_data(annual).copy()
    strip_data["Row"] = "Classification"

    event_color = alt.Color(
        "Event:N",
        title="Year Classification",
        legend=alt.Legend(orient="bottom", columns=3),
        scale=alt.Scale(domain=list(EPISODE_COLORS), range=list(EPISODE_COLORS.values())),
    )

    view_filter = "ViewGroup == 'All Years' || datum.Group == ViewGroup"

    return alt.Chart(strip_data).mark_rect(strokeWidth=1.5).encode(
        x=alt.X("Year:O", title=None),
        y=alt.Y("Row:N", title=None, axis=None),
        color=event_color,
        opacity=alt.condition(view_filter, alt.value(1), alt.value(0.25)),
        stroke=alt.condition(view_filter, alt.value("#ffffff"), alt.value("#0b1427")),
        tooltip=["Year:O", alt.Tooltip("Event:N", title="Classification")],
    ).add_params(view_group).properties(
        title="Which Years Count as a \"Crisis\" Year, and Why",
        width="container",
        height=110,
    )


_h3_direction_data = prepare_direction_data(load_analysis_data()["annual"])
H3_STATS = compute_h3_significance(_h3_direction_data)

_h3_section = next(s for s in sections if s["id"] == "hypothesis-3")
_h3_section["metrics"] = [
    {
        "value": f"{H3_STATS['normal_same']} of {H3_STATS['normal_total']} normal years — {H3_STATS['normal_rate']:.0f}%",
        "label": "moved in the same direction",
    },
    {
        "value": f"{H3_STATS['crisis_same']} of {H3_STATS['crisis_total']} crisis years — {H3_STATS['crisis_rate']:.0f}%",
        "label": "moved in the same direction",
    },
    {"value": f"p = {H3_STATS['p_value']:.2f}", "label": "not statistically significant"},
]
_h3_section["technical_details"] = (
    f"Fisher's exact test: p = {H3_STATS['p_value']:.3f}. 95% confidence intervals — "
    f"normal years: [{H3_STATS['normal_ci'][0]:.0f}%, {H3_STATS['normal_ci'][1]:.0f}%]; "
    f"crisis years: [{H3_STATS['crisis_ci'][0]:.0f}%, {H3_STATS['crisis_ci'][1]:.0f}%]. "
    "The wide crisis-year interval reflects how few crisis years (7) there are to test against."
)


def build_chart_specs() -> dict:
    """Build the Vega-Lite specs for each chart so the browser can render the
    actual Altair charts (via vega-embed) instead of static chart images."""
    alt.data_transformers.disable_max_rows()
    data = load_analysis_data()
    event_window = load_event_window_data()
    correlations = compute_event_window_correlations(event_window)
    troughs = load_downturn_trough_data()
    annual_h2 = load_h2_annual_data()
    h2_stats = compute_h2_correlation(annual_h2)
    chart_builders = {
        "chart1": make_chart1(data["long_index"]),
        "chart2": make_chart2(data["long_change"]),
        "chart3": make_chart3(data["long_change"]),
        "chart4": make_chart4(data["annual"]),
        "chart_event_window": make_chart_event_window(event_window, correlations),
        "chart_event_scatter": make_chart_event_scatter(event_window, correlations),
        "chart_event_dumbbell": make_chart_event_dumbbell(event_window),
        "chart_h2_combined": make_chart_h2_combined(annual_h2, h2_stats),
        "chart_h2_scatter": make_chart_h2_scatter_spec(annual_h2, h2_stats),
        "chart_h2_timeline": make_chart_h2_timeline_spec(annual_h2),
        "chart_h2_readout": make_chart_h2_readout_spec(annual_h2),
        "chart_h1_timeline": make_chart_h1_timeline(troughs["points"], troughs["spans"]),
        "chart_h3_split": make_chart_h3_split(data["annual"]),
        "chart_h3_quadrant": make_chart_h3_quadrant_spec(data["annual"]),
        "chart_crisis_timeline": make_chart_crisis_timeline(data["annual"], alt.param(name="ViewGroup", value="All Years")),
    }
    return {chart_id: chart.to_dict() for chart_id, chart in chart_builders.items()}


CHART_SPECS = build_chart_specs()
_h2_data_for_options = load_h2_annual_data()
H2_EVENT_OPTIONS = sorted(
    _h2_data_for_options.loc[_h2_data_for_options["Event"].ne("No major event"), "Event"].unique().tolist()
)
H2_YEARS = sorted(_h2_data_for_options["Year"].unique().tolist())


@app.route('/')
def w209():
    return render_template(
        'w209.html', sections=sections, chart_specs=CHART_SPECS,
        h2_event_options=H2_EVENT_OPTIONS, h2_years=H2_YEARS, term=term,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5010)))
