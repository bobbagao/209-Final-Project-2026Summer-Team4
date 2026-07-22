import os

from flask import Flask, render_template
import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import fisher_exact, pearsonr

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
        "subtitle": "We tested three common assumptions about gas prices and the S&P 500 against 25 years of data. The results were a mixed bag — one didn't hold up, and two showed only a weak, inconclusive signal once we accounted for how little data there actually is.",
        "summary": "Scroll through three questions, each answered by a single chart built to be read at a glance — then explore the full data yourself at the end.",
        "stats": ["25 years of data", "3 testable questions", "1 flatly rejected"],
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
            "text": "No. In 2 of 4 downturns, gas bottomed out first; in the other 2, the S&P 500 did. The gap ranges from 2 to 9 months, with no consistent pattern in which market leads. Worth flagging: this is a small sample (only 4 major downturns exist in 25 years), and the exact trough dates are read off month-end prices, which can miss the true day-to-day low by a few weeks — but even allowing for that uncertainty, there's no visible sign of a reliable pattern either way.",
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
        "description": "“Volatility” means how much a price bounces around, not just where it ends up — a market that swings wildly but nets out flat is still volatile. Here we measure it annually: S&P 500 volatility is the annualized standard deviation of monthly returns for that year, and gas volatility is the absolute year-over-year change in the average California gas price. One point per year, 2001–2025. Drag across the timeline to filter the scatter to a time window, use the dropdown to highlight a specific year's event, or click a metric in the timeline legend to isolate it.",
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
        "description": "In an average year, do gas prices and the S&P 500 move in the same direction? And does that really break down during a crisis? To keep \"crisis\" consistent with Hypothesis 1 instead of picking a separate list, a year counts as a crisis year here only if it falls between when gas and the S&P actually bottomed out during one of the same four downturns from Question 1 (the Dot-Com Crash, the 2008 Financial Crisis, COVID-19, and the 2022 selloff). That gives 7 crisis years and 19 normal years, which we compared.",
        "secondary_chart_id": "chart_crisis_timeline",
        "chart_id": "chart_h3_combined",
        "chart_caption": "The colored strip above shows exactly which years fall into which category, using the same downturn windows as Question 1 — hover any year for its classification. The top chart below shows the actual percentages with a statistical significance test; the scatter shows every year at once — quadrant color tells you \"same\" from \"opposite\" directly, circles are normal years and diamonds are crisis years. Use the dropdown to isolate just normal or just crisis years, or click a point to label its year.",
        "finding": {
            "label": "The Finding",
            "text": "Inconclusive. Normal years moved in the same direction 63% of the time versus 43% in crisis years (2001-02, 2008-09, 2020, 2022-23) — a real gap in the raw numbers, and in the direction the hypothesis predicts. But with only 7 crisis years to work with, a Fisher's exact test can't rule out that this gap is just chance (p = 0.41). We can't confidently say the pattern breaks down during a crisis — only that it might, and we don't have enough data yet to tell.",
        },
        "metrics": [
            {"value": "63%", "label": "normal years moving together"},
            {"value": "43%", "label": "crisis years moving together"},
            {"value": "p = 0.41", "label": "not statistically significant"},
        ],
        "next": {"id": "conclusion", "label": "See the full conclusion"},
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
                "title": "Normal vs. crisis (split)",
                "chart_id": "chart_h3_split",
                "caption": "How often gas prices and the S&P 500 move together, normal years versus crisis years.",
            },
            {
                "title": "Normal vs. crisis (combined)",
                "chart_id": "chart_h3_combined",
                "caption": "The same comparison as one combined scatter with quadrant coloring, plus a statistical significance test.",
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


def make_chart_h2_scatter(annual_h2: pd.DataFrame, stats: dict, year_brush: alt.Parameter) -> alt.LayerChart:
    base = alt.Chart(annual_h2).transform_filter(year_brush)

    trend = base.transform_regression("SP_Volatility", "Gas_Swing").mark_line(
        color="#f7efe4", strokeWidth=2.5, strokeDash=[7, 5], opacity=0.75,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q")

    points = base.mark_circle(size=150, strokeWidth=1.5).encode(
        x=alt.X("SP_Volatility:Q", title="S&P 500 annualized volatility (%)", scale=alt.Scale(zero=True)),
        y=alt.Y("Gas_Swing:Q", title="Magnitude of annual CA gas-price change (%)", scale=alt.Scale(zero=True)),
        color=alt.Color(
            "Event_Status:N",
            title=None,
            legend=alt.Legend(orient="bottom"),
            scale=alt.Scale(domain=["Major-event year", "Other year"], range=["#f06d5d", "#64748B"]),
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
    )

    selected_label = base.transform_filter(
        "SelectedEvent != 'All years' && datum.Event == SelectedEvent"
    ).mark_text(
        align="left", baseline="bottom", dx=8, dy=-8, fontSize=11, fontWeight="bold", color="#f7efe4", limit=260,
    ).encode(x="SP_Volatility:Q", y="Gas_Swing:Q", text="Event:N")

    return (trend + points + selected_label).properties(
        title=alt.TitleParams(
            text="Do Volatile Stock-Market Years Coincide With Larger Gas-Price Swings?",
            subtitle=[
                "Each point is one year (2001-2025); the dashed line is the overall linear trend.",
                f"Pearson r = {stats['r']:.2f}, 95% CI [{stats['ci_low']:.2f}, {stats['ci_high']:.2f}], "
                f"p = {stats['p_value']:.3f}, n = {stats['n']}.",
                "Use the event dropdown, or drag across the timeline below, to explore a subset.",
            ],
        ),
        width="container",
        height=420,
    )


def make_chart_h2_timeline(annual_h2: pd.DataFrame, year_brush: alt.Parameter, metric_selection: alt.Parameter) -> alt.LayerChart:
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
        scale=alt.Scale(domain=metric_domain, range=["#ffb66b", "#4C78A8"]),
    )

    lines = alt.Chart(timeline_df).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Year_Date:T", title="Year — drag to select a time window", axis=alt.Axis(format="%Y", tickCount=13)),
        y=alt.Y("Percent:Q", title="Annual magnitude (%)", scale=alt.Scale(zero=True)),
        color=metric_color,
        detail="Metric:N",
        opacity=alt.condition(metric_selection, alt.value(1), alt.value(0.15)),
    ).add_params(year_brush, metric_selection)

    points = alt.Chart(timeline_df).mark_circle(size=70).encode(
        x="Year_Date:T",
        y="Percent:Q",
        color=alt.Color("Metric:N", scale=alt.Scale(domain=metric_domain, range=["#ffb66b", "#4C78A8"]), legend=None),
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
                "Drag horizontally to filter the scatterplot above; double-click to reset.",
                "Click a metric in the legend to emphasize or de-emphasize it.",
            ],
        ),
        width="container",
        height=210,
    )


def make_chart_h2_combined(annual_h2: pd.DataFrame, stats: dict) -> alt.VConcatChart:
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

    scatter_chart = make_chart_h2_scatter(annual_h2, stats, year_brush)
    timeline_chart = make_chart_h2_timeline(annual_h2, year_brush, metric_selection)

    return alt.vconcat(scatter_chart, timeline_chart, spacing=28).add_params(event_selector).resolve_scale(
        color="independent"
    ).properties(
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


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

    sp_axis_color = "#ffb66b"
    gas_axis_color = "#4C78A8"

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
        color="#aab4c2",
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
        color="#ffb66b", strokeWidth=3, strokeDash=[6, 3]
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
        color="#aab4c2",
    ).encode(
        text="Label:N",
    ).properties(width="container", height=30)

    return alt.vconcat(combined, annotation).properties(
        title="S&P 500 Volatility vs. Gas Price Volatility After Major Events — Scatter View",
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


def make_chart_h3_significance(stats: dict) -> alt.LayerChart:
    """Point + 95% confidence interval comparison, so viewers see not just
    the two percentages but how much uncertainty surrounds them given the
    small sample — and whether the gap holds up statistically."""
    summary = pd.DataFrame([
        {
            "Group": "Normal Years",
            "Rate": stats["normal_rate"],
            "CI_Low": stats["normal_ci"][0],
            "CI_High": stats["normal_ci"][1],
            "Label": f"{stats['normal_rate']:.0f}% ({stats['normal_same']}/{stats['normal_total']})",
        },
        {
            "Group": "Crisis Years",
            "Rate": stats["crisis_rate"],
            "CI_Low": stats["crisis_ci"][0],
            "CI_High": stats["crisis_ci"][1],
            "Label": f"{stats['crisis_rate']:.0f}% ({stats['crisis_same']}/{stats['crisis_total']})",
        },
    ])

    group_order = ["Normal Years", "Crisis Years"]
    group_color = alt.Color(
        "Group:N", title=None, legend=None,
        scale=alt.Scale(domain=group_order, range=["#4C78A8", "#ffb66b"]),
    )

    fifty_rule = alt.Chart(pd.DataFrame({"z": [50]})).mark_rule(
        color="#888", strokeDash=[5, 5], opacity=0.7
    ).encode(x="z:Q")

    ci_bars = alt.Chart(summary).mark_rule(strokeWidth=5).encode(
        x=alt.X("CI_Low:Q", title="Years moving in the same direction (%)", scale=alt.Scale(domain=[0, 100])),
        x2="CI_High:Q",
        y=alt.Y("Group:N", title=None, sort=group_order),
        color=group_color,
    )

    points = alt.Chart(summary).mark_point(filled=True, size=260, stroke="white", strokeWidth=1.5).encode(
        x="Rate:Q",
        y=alt.Y("Group:N", sort=group_order),
        color=group_color,
    )

    labels = alt.Chart(summary).mark_text(align="left", dx=14, fontSize=13, fontWeight="bold", color="#f7efe4").encode(
        x="Rate:Q",
        y=alt.Y("Group:N", sort=group_order),
        text="Label:N",
    )

    significance_note = (
        f"statistically significant at the 5% level" if stats["p_value"] < 0.05
        else "not statistically significant on its own"
    )

    return (fifty_rule + ci_bars + points + labels).properties(
        title=alt.TitleParams(
            text="How Often Did Gas and the S&P Move in the Same Direction?",
            subtitle=[
                "Dots show the actual rate; bars show the 95% confidence range given how few years of data exist.",
                f"Fisher's exact test: p = {stats['p_value']:.3f} ({significance_note}).",
            ],
        ),
        width="container",
        height=150,
    )


def make_chart_h3_quadrant(annual: pd.DataFrame) -> alt.LayerChart:
    """A single combined scatter (all years at once) instead of two
    side-by-side panels: color-coded quadrant backgrounds label "same" vs.
    "opposite" directly on the plot, and point shape (circle vs. diamond)
    distinguishes normal from crisis years, so the question "do crisis-year
    diamonds cluster in the red zones?" can be read in one glance."""
    direction_data = prepare_direction_data(annual)
    x_limit = max(10, np.ceil(direction_data["Gas_Change"].abs().max() / 5) * 5)
    y_limit = max(10, np.ceil(direction_data["SP_Return"].abs().max() / 5) * 5)

    direction_domain = ["Same Direction", "Opposite Direction"]
    direction_range = ["#59A14F", "#E15759"]

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

    year_select = alt.selection_point(fields=["Year"], on="click", clear="dblclick", empty=False)
    view_group = alt.param(
        name="ViewGroup",
        value="All Years",
        bind=alt.binding_select(options=["All Years", "Normal Years", "Crisis Years"], name="Show years: "),
    )
    view_filter = "ViewGroup == 'All Years' || datum.Group == ViewGroup"

    points = alt.Chart(direction_data).transform_filter(view_filter).mark_point(filled=True, strokeWidth=1.5, stroke="white").encode(
        x=alt.X("Gas_Change:Q", title="Gas Price Change (%)", scale=alt.Scale(domain=[-x_limit, x_limit])),
        y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)", scale=alt.Scale(domain=[-y_limit, y_limit])),
        color=alt.Color("Direction:N", title="Movement", legend=alt.Legend(orient="bottom"), scale=alt.Scale(domain=direction_domain, range=direction_range)),
        shape=alt.Shape("Group:N", title="Year Type", legend=alt.Legend(orient="bottom"), scale=alt.Scale(domain=["Normal Years", "Crisis Years"], range=["circle", "diamond"])),
        size=alt.condition(year_select, alt.value(320), alt.value(160)),
        tooltip=[
            "Year:O", "Event:N", "Group:N",
            alt.Tooltip("Gas_Change:Q", format="+.1f", title="Gas Price Change (%)"),
            alt.Tooltip("SP_Return:Q", format="+.1f", title="S&P 500 Return (%)"),
            "Direction:N",
        ],
    ).add_params(year_select, view_group)

    selected_label = alt.Chart(direction_data).transform_filter(view_filter).transform_filter(year_select).mark_text(
        align="left", dx=10, dy=-10, fontSize=12, fontWeight="bold", color="#f7efe4"
    ).encode(
        x=alt.X("Gas_Change:Q", scale=alt.Scale(domain=[-x_limit, x_limit])),
        y=alt.Y("SP_Return:Q", scale=alt.Scale(domain=[-y_limit, y_limit])),
        text="Year:O",
    )

    return (quadrant_bg + zero_x + zero_y + points + selected_label).resolve_scale(color="independent").properties(
        title=alt.TitleParams(
            text="How Did Gas Prices and the S&P 500 Move Each Year?",
            subtitle=[
                "Green quadrants = moved the same direction. Red quadrants = moved opposite.",
                "Circles = normal years, diamonds = crisis years. Click a point to label its year.",
            ],
        ),
        width="container",
        height=460,
    )


def make_chart_h3_combined(annual: pd.DataFrame) -> alt.VConcatChart:
    direction_data = prepare_direction_data(annual)
    stats = compute_h3_significance(direction_data)

    significance_chart = make_chart_h3_significance(stats)
    quadrant_chart = make_chart_h3_quadrant(annual)

    return alt.vconcat(significance_chart, quadrant_chart).properties(
        autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
    )


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
            domain=["Normal Year", "Dot-Com Crash", "Financial Crisis", "COVID-19 Crash", "2022 Selloff"],
            range=["#3a4a63", "#8E6C8A", "#E15759", "#4C78A8", "#ffb66b"],
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
    annual_h2 = load_h2_annual_data()
    h2_stats = compute_h2_correlation(annual_h2)
    chart_builders = {
        "chart1": make_chart1(data["long_index"]),
        "chart2": make_chart2(data["long_change"]),
        "chart3": make_chart3(data["long_change"]),
        "chart4": make_chart4(data["annual"]),
        "chart6": make_chart6(data["pattern_counts"]),
        "chart_event_window": make_chart_event_window(event_window, correlations),
        "chart_event_scatter": make_chart_event_scatter(event_window, correlations),
        "chart_h2_combined": make_chart_h2_combined(annual_h2, h2_stats),
        "chart_h1_timeline": make_chart_h1_timeline(troughs["points"], troughs["spans"]),
        "chart_h3_split": make_chart_h3_split(data["annual"]),
        "chart_h3_combined": make_chart_h3_combined(data["annual"]),
        "chart_crisis_timeline": make_chart_crisis_timeline(data["annual"]),
    }
    return {chart_id: chart.to_dict() for chart_id, chart in chart_builders.items()}


CHART_SPECS = build_chart_specs()


@app.route('/')
def w209():
    return render_template('w209.html', sections=sections, chart_specs=CHART_SPECS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5010)))
