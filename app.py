import os

from flask import Flask, render_template
import pandas as pd
import numpy as np
import altair as alt

app = Flask(__name__)


@alt.theme.register("energy_market_dark", enable=True)
def energy_market_dark_theme():
    """Matches static/styles.css so charts blend into the page instead of
    sitting on top of it as a pasted-in white card."""
    text_color = "#f7efe4"
    muted_color = "#aab4c2"
    grid_color = "rgba(255,255,255,0.10)"
    line_color = "rgba(255,255,255,0.25)"
    accent = "#ffb66b"
    accent2 = "#f06d5d"
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
                    "#4C78A8", accent, accent2, "#59A14F", "#8E6C8A", "#EDC948", "#79706E", "#D37295",
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
        "subtitle": "We tested three common assumptions about gas prices and the S&P 500 against 25 years of data. Two of them didn't hold up the way you'd expect.",
        "summary": "Scroll through three questions, each answered by a single chart built to be read at a glance — then explore the full data yourself at the end.",
        "stats": ["25 years of data", "3 testable questions", "2 overturned by the data"],
        "next": {"id": "introduction", "label": "Start the story"},
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
        "chart_id": "chart_h1_timeline",
        "chart_title": "Who dipped first?",
        "chart_caption": "The month each market bottomed out during four major downturns — no consistent leader emerges.",
        "finding": {
            "label": "The Finding",
            "text": "No. In 2 of 4 downturns, gas bottomed out first; in the other 2, the S&P 500 did. The gap ranges from 2 to 9 months, with no consistent pattern in which market leads.",
        },
        "metrics": [
            {"value": "2 of 4", "label": "downturns where gas dipped first"},
            {"value": "2 of 4", "label": "downturns where the S&P dipped first"},
            {"value": "Not supported", "label": "no consistent lead-lag pattern"},
        ],
        "next": {"id": "hypothesis-2", "label": "Question 2: Do bigger gains mean bigger gas swings?"},
    },
    {
        "id": "hypothesis-2",
        "type": "hypothesis",
        "eyebrow": "03 • Question 2",
        "title": "Do bigger stock market swings come with bigger gas-price swings?",
        "description": "“Volatility” means the size of a price swing, regardless of direction — not whether the market went up or down. To compare S&P 500 volatility and gas price volatility fairly, we measure both the same way: the size of the change (up or down) in the months after every major event since 2001. Adjust the window below to see the relationship shift.",
        "chart_id": "chart_event_window",
        "chart_title": "Event impact window",
        "chart_caption": "S&P 500 volatility (dots, colored by event category, with an orange trend line) and gas price volatility (blue bars) after every major event since 2001. Use the dropdown to change how many months out you're looking.",
        "finding": {
            "label": "The Finding",
            "text": "Yes, but only in the near term. In the 1-6 months after a major event, more S&P volatility tends to line up with more gas-price volatility — peaking around 3 months out (r = +0.38). That relationship fades to almost nothing by 12 months out (r = +0.03).",
        },
        "metrics": [
            {"value": "r = +0.38", "label": "S&P volatility vs. gas volatility, 3 months out"},
            {"value": "Fades by 12mo", "label": "drops to r = +0.03 a year out"},
            {"value": "Short-term only", "label": "volatility co-moves, but doesn't last"},
        ],
        "next": {"id": "hypothesis-3", "label": "Question 3: Do crises break the link?"},
    },
    {
        "id": "hypothesis-3",
        "type": "hypothesis",
        "eyebrow": "04 • Question 3",
        "title": "Does the normal link between gas prices and stocks hold up during a crisis?",
        "description": "In an average year, do gas prices and the S&P 500 move in the same direction? And does that really break down during a crisis? We split 25 years of data into two groups and compared how often each moved together. “Crisis years” are 2008-09 (Financial Crisis), 2020-21 (COVID), 2022 (Energy Shock), and 2023-25 (Recent Conflict/Geopolitical) — every other year since 2000 counts as “normal.”",
        "secondary_chart_id": "chart_crisis_timeline",
        "chart_id": "chart_h3_split",
        "chart_title": "Normal years vs. crisis years",
        "chart_caption": "The colored strip above shows exactly which years fall into which category — hover any year for its classification. \"Crisis\" here means a broad, sustained, globally-recognized economic disruption (a recession, pandemic, energy shock, or major conflict), not just a bad headline, which is why most years are still \"normal.\" Below, each dot is one year, labeled by year and colored by whether gas and the S&P moved in the same direction that year.",
        "finding": {
            "label": "The Finding",
            "text": "Yes. Gas prices and the S&P 500 moved in the same direction about 72% of the time in normal years, but only 25% of the time during crisis years (2008-09, 2020-22, 2023-25) — a real, sizable break in the pattern.",
        },
        "metrics": [
            {"value": "72%", "label": "normal years moving together"},
            {"value": "25%", "label": "crisis years moving together"},
            {"value": "Supported", "label": "crisis decoupling is real"},
        ],
        "next": {"id": "conclusion", "label": "See the full conclusion"},
    },
    {
        "id": "conclusion",
        "type": "story",
        "eyebrow": "05 • Conclusion",
        "title": "What the data actually shows",
        "description": "Testing three specific, falsifiable questions instead of assuming a single story produced three different answers: one hypothesis wasn't supported at all, one held up only in the short term before fading, and one held up strongly across the board. That mix is itself the finding — the gas-price/S&P relationship isn't one consistent story, and treating it as one would have been misleading.",
        "highlights": [
            "Hypothesis 1 (gas leads stocks down): not supported — across four major downturns, the lead varied both ways.",
            "Hypothesis 2 (high volatility pairs with high volatility): supported short-term — S&P and gas volatility move together for a few months after a major event, but that relationship fades to near-zero by the one-year mark.",
            "Hypothesis 3 (crises break the link): supported — normal years move together about three times more often than crisis years."
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
                "title": "Event impact window",
                "chart_id": "chart_event_window",
                "caption": "S&P performance and gas volatility after every major event since 2001, with an adjustable time window.",
            },
            {
                "title": "Normal vs. crisis years",
                "chart_id": "chart_h3_split",
                "caption": "How often gas prices and the S&P 500 move together, normal years versus crisis years.",
            },
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
                "title": "Yearly bars",
                "chart_id": "chart3",
                "caption": "Yearly percent change bars make the ups and downs easier to compare.",
            },
            {
                "title": "Event patterns",
                "chart_id": "chart6",
                "caption": "The event-pattern matrix behind the normal-vs-crisis split.",
            },
        ],
    },
]


def event_group(year: int) -> str:
    if year in [2008, 2009]:
        return "Financial Crisis"
    if year in [2020, 2021]:
        return "COVID"
    if year == 2022:
        return "Energy Shock"
    if year in [2023, 2024, 2025]:
        return "Recent Conflict"
    return "Normal Year"


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
        id_vars=["Year", "Date", "Event"],
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

EVENT_WINDOW_MONTHS = list(range(1, 13))


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
    """For every event in the Major Global Events file, compute the percent
    change in S&P 500 close and CA gas price over a 1-12 month window
    starting at the event's start date, using the monthly market data."""
    base_path = os.path.dirname(__file__)
    events_file = os.path.join(base_path, "Major_Global_Events_2001_Present (1).xlsx")

    events = pd.read_excel(events_file, sheet_name="Global Events", engine="openpyxl")
    events = events.dropna(subset=["Event Name", "Start Date"])
    events["Start Date"] = pd.to_datetime(events["Start Date"])
    events["Category"] = events["Event Name"].map(EVENT_CATEGORIES).fillna("Other")

    monthly = load_monthly_market_data()
    max_date = monthly["Date"].max()

    records = []
    for _, ev in events.iterrows():
        start = ev["Start Date"]
        before_start = monthly[monthly["Date"] <= start]
        start_row = before_start.iloc[-1] if not before_start.empty else monthly.iloc[0]

        for window in EVENT_WINDOW_MONTHS:
            window_end = min(start + pd.DateOffset(months=window), max_date)
            before_end = monthly[monthly["Date"] <= window_end]
            end_row = before_end.iloc[-1] if not before_end.empty else monthly.iloc[-1]

            sp_change = (end_row["SP_Close"] / start_row["SP_Close"] - 1) * 100
            gas_change = (end_row["Gas_Price"] / start_row["Gas_Price"] - 1) * 100

            for market, pct_change in (("S&P 500", sp_change), ("Gas Price", gas_change)):
                records.append({
                    "Event": ev["Event Name"],
                    "Category": ev["Category"],
                    "Start Date": start,
                    "Window": window,
                    "Market": market,
                    "Percent_Change": pct_change,
                    # Volatility = size of the swing regardless of direction,
                    # so both markets are measured the same way for a fair
                    # comparison (a signed "performance" number isn't volatility).
                    "Plot_Value": abs(pct_change),
                })

    return pd.DataFrame(records)


def compute_event_window_correlations(event_window: pd.DataFrame) -> pd.DataFrame:
    """Correlation between S&P volatility and gas volatility (both measured
    as magnitude of change, so the two are directly comparable) at each
    window length, for the plain-language annotation under the chart."""
    records = []
    for window in EVENT_WINDOW_MONTHS:
        sub = event_window[event_window["Window"] == window]
        pivoted = sub.pivot(index=["Event", "Start Date"], columns="Market", values="Percent_Change").dropna()
        r = pivoted["S&P 500"].abs().corr(pivoted["Gas Price"].abs())
        strength = "little to no" if abs(r) < 0.1 else ("a weak" if abs(r) < 0.3 else "a moderate")
        direction = "move together" if r > 0 else "move oppositely"
        label = f"At this window: S&P volatility and gas volatility show {strength} tendency to {direction} (r = {r:+.2f})"
        records.append({"Window": window, "Correlation": r, "Label": label})
    return pd.DataFrame(records)


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


def make_chart_h1_timeline(points: pd.DataFrame, spans: pd.DataFrame) -> alt.LayerChart:
    episode_order = list(DOWNTURN_EPISODES.keys())
    market_color = alt.Color(
        "Market:N",
        title="Market",
        legend=alt.Legend(orient="bottom"),
        scale=alt.Scale(domain=["S&P 500", "Gas Price"], range=["#F58518", "#4C78A8"]),
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

    labels = alt.Chart(spans).mark_text(dy=-22, fontSize=12, fontWeight="bold", color="#f7efe4").encode(
        y=alt.Y("Episode:N", sort=episode_order),
        x=alt.X("mid_date:T"),
        text="Label:N",
    )

    return (connector + dots + labels).properties(
        title="Who Dipped First? Gas Price vs. S&P 500 Bottom, by Downturn",
        width="container",
        height=280,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart_event_window(event_window: pd.DataFrame, correlations: pd.DataFrame) -> alt.VConcatChart:
    """One overlaid chart instead of two stacked panels: gas volatility as a
    background histogram, S&P performance as colored dots with a smoothed
    trend line on top, sharing a single time axis with a dual y-scale."""
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
        alt.Tooltip("Percent_Change:Q", format=".1f", title="Actual Percent Change"),
    ]

    base_gas = alt.Chart(event_window).transform_filter(
        alt.FieldEqualPredicate(field="Market", equal="Gas Price")
    ).transform_filter(window_select)

    base_sp = alt.Chart(event_window).transform_filter(
        alt.FieldEqualPredicate(field="Market", equal="S&P 500")
    ).transform_filter(window_select)

    gas_bars = base_gas.mark_bar(opacity=0.35, color="#4C78A8", size=5).encode(
        x=alt.X("Start Date:T", title="Event Start Date"),
        y=alt.Y("Plot_Value:Q", title="Gas Price Volatility (%)", axis=alt.Axis(orient="right")),
        tooltip=tooltip,
    ).add_params(window_select)

    sp_points = base_sp.mark_circle(size=70, stroke="white", strokeWidth=0.5).encode(
        x=alt.X("Start Date:T"),
        y=alt.Y("Plot_Value:Q", title="S&P 500 Volatility (%)"),
        color=color,
        tooltip=tooltip,
    )

    sp_trend = base_sp.transform_loess(
        "Start Date", "Plot_Value", as_=["Start Date", "Smoothed"], bandwidth=0.3
    ).mark_line(color="#ffb66b", strokeWidth=3.5, interpolate="monotone").encode(
        x="Start Date:T",
        # No y-title here: this layer shares S&P 500's axis/scale with
        # sp_points below (grouped in one sub-layer so Vega-Lite renders a
        # single axis instead of one per layer, which was drawing the title
        # twice).
        y=alt.Y("Smoothed:Q", axis=None),
    )

    sp_group = (sp_points + sp_trend)
    combined = (gas_bars + sp_group).resolve_scale(y="independent").properties(
        title="S&P 500 Volatility (line + dots) vs. Gas Price Volatility (bars)",
        width="container",
        height=420,
    )

    annotation = alt.Chart(correlations).transform_filter(window_select).mark_text(
        fontSize=13,
        fontStyle="italic",
        color="#aab4c2",
    ).encode(
        text="Label:N",
    ).properties(width="container", height=30)

    return alt.vconcat(combined, annotation).properties(
        title="S&P 500 Volatility vs. Gas Price Volatility After Major Events",
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart1(long_index: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_index).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Index_Value:Q", title="Index Value"),
        color=alt.Color("Type:N", title="Series", legend=alt.Legend(orient="bottom")),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Index_Value:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Indexed S&P 500 vs Gas Prices",
        width="container",
        height=420,
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
        height=420,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart3(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_bar().encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series", legend=alt.Legend(orient="bottom")),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Bar Chart of Yearly Changes",
        width="container",
        height=420,
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
        height=460,
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


def make_chart6(pattern_counts: pd.DataFrame) -> alt.Chart:
    return alt.Chart(pattern_counts).mark_rect().encode(
        x=alt.X("Pattern:N", title="Market Pattern"),
        y=alt.Y("Event:N", title="Event"),
        color=alt.Color("Count:Q", title="Number of Years", legend=alt.Legend(orient="bottom", gradientLength=180)),
        tooltip=["Event:N", "Pattern:N", "Count:Q"],
    ).properties(
        title="Market Patterns by Event Type",
        width="container",
        height=380,
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
        scale=alt.Scale(domain=["Same Direction", "Opposite Direction"], range=["#59A14F", "#E15759"]),
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
        labels = base.mark_text(dy=-14, fontSize=9.5, color="#f7efe4").encode(
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


def make_chart_crisis_timeline(annual: pd.DataFrame) -> alt.Chart:
    """A single-row, color-coded strip showing exactly which years are
    classified as which kind of year, and why — so "crisis year" isn't an
    unexplained label attached to the chart below."""
    strip_data = annual.copy()
    strip_data["Row"] = "Classification"

    event_color = alt.Color(
        "Event:N",
        title="Year Classification",
        legend=alt.Legend(orient="bottom", columns=3),
        scale=alt.Scale(
            domain=["Normal Year", "Financial Crisis", "COVID", "Energy Shock", "Recent Conflict"],
            range=["#3a4a63", "#E15759", "#4C78A8", "#ffb66b", "#8E6C8A"],
        ),
    )

    return alt.Chart(strip_data).mark_rect(stroke="#0b1427", strokeWidth=1.5).encode(
        x=alt.X("Year:O", title=None),
        y=alt.Y("Row:N", title=None, axis=None),
        color=event_color,
        tooltip=["Year:O", alt.Tooltip("Event:N", title="Classification")],
    ).properties(
        title="Which Years Count as a \"Crisis\" Year, and Why",
        width="container",
        height=60,
    )


def build_chart_specs() -> dict:
    """Build the Vega-Lite specs for each chart so the browser can render the
    actual Altair charts (via vega-embed) instead of static chart images."""
    alt.data_transformers.disable_max_rows()
    data = load_analysis_data()
    event_window = load_event_window_data()
    correlations = compute_event_window_correlations(event_window)
    troughs = load_downturn_trough_data()
    chart_builders = {
        "chart1": make_chart1(data["long_index"]),
        "chart2": make_chart2(data["long_change"]),
        "chart3": make_chart3(data["long_change"]),
        "chart4": make_chart4(data["annual"]),
        "chart6": make_chart6(data["pattern_counts"]),
        "chart_event_window": make_chart_event_window(event_window, correlations),
        "chart_h1_timeline": make_chart_h1_timeline(troughs["points"], troughs["spans"]),
        "chart_h3_split": make_chart_h3_split(data["annual"]),
        "chart_crisis_timeline": make_chart_crisis_timeline(data["annual"]),
    }
    return {chart_id: chart.to_dict() for chart_id, chart in chart_builders.items()}


CHART_SPECS = build_chart_specs()


@app.route('/')
def w209():
    return render_template('w209.html', sections=sections, chart_specs=CHART_SPECS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
