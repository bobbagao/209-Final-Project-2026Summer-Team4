import os

from flask import Flask, render_template
import pandas as pd
import numpy as np
import altair as alt

app = Flask(__name__)

CHART_DIR = os.path.join(os.path.dirname(__file__), "static", "charts")
CHART_FILES = {
    "chart1": "chart1.png",
    "chart2": "chart2.png",
    "chart3": "chart3.png",
    "chart4": "chart4.png",
    "chart6": "chart6.png",
}

app.config["CHART_DIR"] = CHART_DIR

sections = [
    {
        "id": "cover",
        "type": "hero",
        "eyebrow": "W209 • Data Visualization",
        "title": "Energy and Equity Market Story",
        "subtitle": "Exploratory analysis of gas prices and the S&P 500 through three hypotheses.",
        "summary": "This page is restructured as a narrative report so the full analysis can unfold from a strong opening, through each hypothesis, to a concluding synthesis.",
    },
    {
        "id": "introduction",
        "type": "story",
        "eyebrow": "02 • Introduction",
        "title": "Why this relationship matters",
        "description": "The connection between energy costs and equity performance is often discussed as a broad macro trend, but the relationship can shift depending on timing, volatility, and external shocks.",
        "highlights": [
            "Gas prices react quickly to supply and policy changes.",
            "The S&P 500 reflects expectations about growth and inflation.",
            "Their interaction can reveal whether markets are moving in sync or diverging."
        ],
    },
    {
        "id": "chart-explorer",
        "type": "explorer",
        "eyebrow": "03 • Visual Explorer",
        "title": "Compare the charts side by side",
        "description": "Switch between the key visualizations to see how the gas-price and S&P story changes across time, returns, and crisis context.",
        "chart_items": [
            {
                "title": "Indexed trend",
                "src": "charts/chart1.png",
                "alt": "Indexed S&P and gas price trend",
                "caption": "A long-view comparison of the indexed S&P 500 and gas prices over time.",
            },
            {
                "title": "Yearly change",
                "src": "charts/chart2.png",
                "alt": "Yearly change lines for the S&P and gas",
                "caption": "This view highlights the yearly percent change in both markets.",
            },
            {
                "title": "Return scatter",
                "src": "charts/chart4.png",
                "alt": "Scatter plot of gas change and S&P return",
                "caption": "A scatter view shows how annual returns cluster around gas-price movement.",
            },
            {
                "title": "Event patterns",
                "src": "charts/chart6.png",
                "alt": "Pattern matrix for market behavior by event type",
                "caption": "The event-pattern matrix shows how normal years and crises diverge.",
            },
        ],
    },
    {
        "id": "hypothesis-1",
        "type": "explorer",
        "eyebrow": "04 • Hypothesis 1",
        "title": "A dip in gas prices will consistently precede a dip in the S&P 500",
        "description": "This hypothesis tests whether falling fuel costs are an early signal of weakening investor sentiment and softer economic expectations.",
        "highlights": [
            "Leading indicator framing",
            "Lag-window testing",
            "Directional movement comparison"
        ],
        "metrics": [
            {"value": "Early signal", "label": "Potential lead effect"},
            {"value": "Lag window", "label": "Time-based test"},
            {"value": "Direction", "label": "Up/down comparison"},
        ],
        "chart_items": [
            {
                "title": "Return scatter",
                "src": "charts/chart4.png",
                "alt": "Annual S&P return versus gas price change",
                "caption": "Annual S&P 500 returns compared with gas price changes.",
            },
            {
                "title": "Yearly change",
                "src": "charts/chart2.png",
                "alt": "Yearly percent change for S&P 500 and gas prices",
                "caption": "Yearly percent change trajectories for both markets.",
            },
            {
                "title": "Indexed trend",
                "src": "charts/chart1.png",
                "alt": "Indexed S&P 500 and gas prices over time",
                "caption": "A long-view comparison of the indexed series.",
            },
        ],
    },
    {
        "id": "hypothesis-2",
        "type": "explorer",
        "eyebrow": "05 • Hypothesis 2",
        "title": "Periods with high S&P 500 performance also have high gas price volatility",
        "description": "This section explores whether strong market rallies are paired with unstable energy prices, suggesting shared exposure to macroeconomic stress.",
        "highlights": [
            "Volatility comparison",
            "Market-regime mapping",
            "Cross-signal clustering"
        ],
        "metrics": [
            {"value": "High volatility", "label": "Energy sensitivity"},
            {"value": "Shared regime", "label": "Macro overlap"},
            {"value": "Complex relationship", "label": "Not purely linear"},
        ],
        "chart_items": [
            {
                "title": "Indexed trend",
                "src": "charts/chart1.png",
                "alt": "Indexed S&P 500 and gas prices over time",
                "caption": "Indexed S&P 500 and gas prices show how each market moved through the same period.",
            },
            {
                "title": "Yearly bars",
                "src": "charts/chart3.png",
                "alt": "Bar chart of yearly percent changes for S&P 500 and gas",
                "caption": "Yearly percent change bars make the ups and downs easier to compare.",
            },
            {
                "title": "Return scatter",
                "src": "charts/chart4.png",
                "alt": "Scatter plot linking gas change and S&P return",
                "caption": "This view shows whether stronger returns cluster with larger gas swings.",
            },
        ],
    },
    {
        "id": "hypothesis-3",
        "type": "explorer",
        "eyebrow": "06 • Hypothesis 3",
        "title": "Normal economic years show strong correlation, but crises break the pattern",
        "description": "This hypothesis frames the baseline relationship and then contrasts it with major disruptions such as financial crises, pandemics, and supply shocks.",
        "highlights": [
            "Baseline correlation",
            "Event disruption",
            "Crisis decoupling"
        ],
        "metrics": [
            {"value": "Normal years", "label": "Baseline alignment"},
            {"value": "Crisis years", "label": "Decoupled movement"},
            {"value": "Policy shock", "label": "Structural break"},
        ],
        "chart_items": [
            {
                "title": "Event patterns",
                "src": "charts/chart6.png",
                "alt": "Market patterns during normal years and crisis events",
                "caption": "Crisis and normal-year market patterns reveal how the relationship shifts during major events.",
            },
            {
                "title": "Indexed trend",
                "src": "charts/chart1.png",
                "alt": "Indexed S&P 500 and gas prices over time",
                "caption": "The indexed trend shows how long-run trajectories deviate around shock periods.",
            },
            {
                "title": "Return scatter",
                "src": "charts/chart4.png",
                "alt": "Scatter plot of gas change and S&P return",
                "caption": "The scatter view helps separate normal years from crisis-years visually.",
            },
        ],
    },
    {
        "id": "conclusion",
        "type": "story",
        "eyebrow": "07 • Conclusion",
        "title": "What the data reveals",
        "description": "Across the three hypotheses, the story becomes clearer: the gas-price and S&P 500 relationship is not fixed, but it is highly informative when studied through timing, volatility, and crisis context.",
        "highlights": [
            "The relationship is conditional, not constant.",
            "Timing and volatility matter as much as direction.",
            "Crisis events can change the structure of the signal entirely."
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


def make_chart1(long_index: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_index).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Index_Value:Q", title="Index Value"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Index_Value:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Indexed S&P 500 vs Gas Prices",
        width=900,
        height=420,
    )


def make_chart2(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Yearly Percent Change: S&P 500 vs Gas Prices",
        width=900,
        height=420,
    )


def make_chart3(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_bar().encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Bar Chart of Yearly Changes",
        width=900,
        height=420,
    )


def make_chart4(annual: pd.DataFrame) -> alt.Chart:
    return alt.Chart(annual).mark_circle(size=110).encode(
        x=alt.X("Gas_Change:Q", title="Gas Price Change (%)"),
        y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)"),
        color=alt.Color("Event:N", title="Event"),
        tooltip=["Year:O", "Event:N", alt.Tooltip("Gas_Change:Q", format=".1f"), alt.Tooltip("SP_Return:Q", format=".1f")],
    ).properties(
        title="S&P 500 Return vs Gas Price Change",
        width=760,
        height=420,
    )


def make_chart6(pattern_counts: pd.DataFrame) -> alt.Chart:
    return alt.Chart(pattern_counts).mark_rect().encode(
        x=alt.X("Pattern:N", title="Market Pattern"),
        y=alt.Y("Event:N", title="Event"),
        color=alt.Color("Count:Q", title="Number of Years"),
        tooltip=["Event:N", "Pattern:N", "Count:Q"],
    ).properties(
        title="Market Patterns by Event Type",
        width=900,
        height=420,
    )


def generate_charts() -> None:
    os.makedirs(CHART_DIR, exist_ok=True)
    data = load_analysis_data()
    alt.data_transformers.disable_max_rows()
    chart_map = {
        "chart1.png": make_chart1(data["long_index"]),
        "chart2.png": make_chart2(data["long_change"]),
        "chart3.png": make_chart3(data["long_change"]),
        "chart4.png": make_chart4(data["annual"]),
        "chart6.png": make_chart6(data["pattern_counts"]),
    }

    for file_name, chart in chart_map.items():
        output_path = os.path.join(CHART_DIR, file_name)
        if not os.path.exists(output_path):
            chart.save(output_path)


def ensure_charts() -> None:
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR, exist_ok=True)
    missing = [name for name in CHART_FILES.values() if not os.path.exists(os.path.join(CHART_DIR, name))]
    if missing:
        generate_charts()


ensure_charts()


@app.route('/')
def w209():
    return render_template('w209.html', sections=sections)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
