import os

from flask import Flask, render_template
import pandas as pd
import numpy as np
import altair as alt

app = Flask(__name__)

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
                "chart_id": "chart1",
                "caption": "A long-view comparison of the indexed S&P 500 and gas prices over time.",
            },
            {
                "title": "Yearly change",
                "chart_id": "chart2",
                "caption": "This view highlights the yearly percent change in both markets.",
            },
            {
                "title": "Return scatter",
                "chart_id": "chart4",
                "caption": "A scatter view shows how annual returns cluster around gas-price movement.",
            },
            {
                "title": "Event patterns",
                "chart_id": "chart6",
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
                "chart_id": "chart4",
                "caption": "Annual S&P 500 returns compared with gas price changes.",
            },
            {
                "title": "Yearly change",
                "chart_id": "chart2",
                "caption": "Yearly percent change trajectories for both markets.",
            },
            {
                "title": "Indexed trend",
                "chart_id": "chart1",
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
                "chart_id": "chart1",
                "caption": "Indexed S&P 500 and gas prices show how each market moved through the same period.",
            },
            {
                "title": "Yearly bars",
                "chart_id": "chart3",
                "caption": "Yearly percent change bars make the ups and downs easier to compare.",
            },
            {
                "title": "Event impact window",
                "chart_id": "chart_event_window",
                "caption": "Percent change in each market during a 1-12 month window after every major event since 2001, colored by event category.",
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
                "chart_id": "chart6",
                "caption": "Crisis and normal-year market patterns reveal how the relationship shifts during major events.",
            },
            {
                "title": "Indexed trend",
                "chart_id": "chart1",
                "caption": "The indexed trend shows how long-run trajectories deviate around shock periods.",
            },
            {
                "title": "Return scatter",
                "chart_id": "chart4",
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


def load_event_window_data() -> pd.DataFrame:
    """For every event in the Major Global Events file, compute the percent
    change in S&P 500 close and CA gas price over a 1-12 month window
    starting at the event's start date, using the monthly market data."""
    base_path = os.path.dirname(__file__)
    events_file = os.path.join(base_path, "Major_Global_Events_2001_Present (1).xlsx")
    market_file = os.path.join(base_path, "SP500_GasPrices_Tableau_v3.xlsx")

    events = pd.read_excel(events_file, sheet_name="Global Events", engine="openpyxl")
    events = events.dropna(subset=["Event Name", "Start Date"])
    events["Start Date"] = pd.to_datetime(events["Start Date"])
    events["Category"] = events["Event Name"].map(EVENT_CATEGORIES).fillna("Other")

    monthly = pd.read_excel(market_file, sheet_name="Monthly_Data", engine="openpyxl")
    monthly = monthly.rename(columns={
        "S&P 500 Close": "SP_Close",
        "CA Gas Price ($/gal)": "Gas_Price",
    })
    monthly["Date"] = pd.to_datetime(monthly["Date"])
    monthly = monthly.dropna(subset=["Date", "SP_Close", "Gas_Price"]).sort_values("Date")
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
                })

    return pd.DataFrame(records)


def make_chart_event_window(event_window: pd.DataFrame) -> alt.VConcatChart:
    window_select = alt.selection_point(
        fields=["Window"],
        bind=alt.binding_select(options=EVENT_WINDOW_MONTHS, name="Months after event start: "),
        value=6,
    )

    category_domain = sorted(event_window["Category"].unique())
    color = alt.Color("Category:N", title="Event Category", scale=alt.Scale(domain=category_domain))
    tooltip = [
        "Event:N",
        "Category:N",
        alt.Tooltip("Start Date:T", format="%b %Y"),
        "Window:O",
        alt.Tooltip("Percent_Change:Q", format=".1f", title="Percent Change"),
    ]

    def market_panel(market_name: str, y_title: str, include_param: bool) -> alt.LayerChart:
        base = alt.Chart(event_window).transform_filter(
            alt.FieldEqualPredicate(field="Market", equal=market_name)
        ).transform_filter(window_select)

        rule = base.mark_rule(strokeWidth=1.5).encode(
            x=alt.X("Start Date:T", title="Event Start Date"),
            y=alt.Y("Percent_Change:Q", title=y_title),
            y2=alt.Y2(datum=0),
            color=color,
            tooltip=tooltip,
        )
        if include_param:
            rule = rule.add_params(window_select)

        point = base.mark_circle(size=65, stroke="white", strokeWidth=0.5).encode(
            x=alt.X("Start Date:T"),
            y=alt.Y("Percent_Change:Q"),
            color=color,
            tooltip=tooltip,
        )

        return (rule + point).properties(
            title=market_name,
            width=850,
            height=200,
        )

    sp_panel = market_panel("S&P 500", "S&P 500 Change (%)", include_param=True)
    gas_panel = market_panel("Gas Price", "Gas Price Change (%)", include_param=False)

    return alt.vconcat(sp_panel, gas_panel).properties(
        title="Market Change in the Months Following Major Global Events",
    ).resolve_scale(color="shared")


def make_chart1(long_index: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_index).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Index_Value:Q", title="Index Value"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Index_Value:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Indexed S&P 500 vs Gas Prices",
        width=800,
        height=400,
    )


def make_chart2(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Yearly Percent Change: S&P 500 vs Gas Prices",
        width=800,
        height=400,
    )


def make_chart3(long_change: pd.DataFrame) -> alt.Chart:
    return alt.Chart(long_change).mark_bar().encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Percent_Change:Q", title="Percent Change"),
        color=alt.Color("Type:N", title="Series"),
        tooltip=["Year:O", "Type:N", alt.Tooltip("Percent_Change:Q", format=".1f"), "Event:N"],
    ).properties(
        title="Bar Chart of Yearly Changes",
        width=800,
        height=400,
    )


def make_chart4(annual: pd.DataFrame) -> alt.Chart:
    return alt.Chart(annual).mark_circle(size=100).encode(
        x=alt.X("Gas_Change:Q", title="Gas Price Change (%)"),
        y=alt.Y("SP_Return:Q", title="S&P 500 Return (%)"),
        color=alt.Color("Event:N", title="Event"),
        tooltip=["Year:O", "Event:N", alt.Tooltip("Gas_Change:Q", format=".1f"), alt.Tooltip("SP_Return:Q", format=".1f")],
    ).properties(
        title="S&P 500 Return vs Gas Price Change",
        width=650,
        height=450,
    )


def make_chart6(pattern_counts: pd.DataFrame) -> alt.Chart:
    return alt.Chart(pattern_counts).mark_rect().encode(
        x=alt.X("Pattern:N", title="Market Pattern"),
        y=alt.Y("Event:N", title="Event"),
        color=alt.Color("Count:Q", title="Number of Years"),
        tooltip=["Event:N", "Pattern:N", "Count:Q"],
    ).properties(
        title="Market Patterns by Event Type",
        width=750,
        height=350,
    )


def build_chart_specs() -> dict:
    """Build the Vega-Lite specs for each chart so the browser can render the
    actual Altair charts (via vega-embed) instead of static chart images."""
    alt.data_transformers.disable_max_rows()
    data = load_analysis_data()
    event_window = load_event_window_data()
    chart_builders = {
        "chart1": make_chart1(data["long_index"]),
        "chart2": make_chart2(data["long_change"]),
        "chart3": make_chart3(data["long_change"]),
        "chart4": make_chart4(data["annual"]),
        "chart6": make_chart6(data["pattern_counts"]),
        "chart_event_window": make_chart_event_window(event_window),
    }
    return {chart_id: chart.to_dict() for chart_id, chart in chart_builders.items()}


CHART_SPECS = build_chart_specs()


@app.route('/')
def w209():
    return render_template('w209.html', sections=sections, chart_specs=CHART_SPECS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
