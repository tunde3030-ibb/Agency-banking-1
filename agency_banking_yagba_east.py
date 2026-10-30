"""
Agency Banking & Financial Inclusion in Yagba East LGA, Kogi State
-------------------------------------------------------------------
A Streamlit dashboard for exploring how banking agents extend financial
services to underserved communities.

IMPORTANT: The built-in dataset is ILLUSTRATIVE (simulated) and is meant for
demonstration and teaching. Replace it with real field-survey data by using
the "Upload your own CSV" option in the sidebar.

Run with:
    streamlit run agency_banking_yagba_east.py
"""

import io

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Agency Banking & Financial Inclusion - Yagba East LGA",
    page_icon="🏦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #f7f9f8; }
    .banner { background-color: #008751; height: 10px; border-radius: 4px; margin-bottom: 12px; }
    .title-box {
        background-color: #ffffff; padding: 14px; border-radius: 12px;
        border: 2px solid #008751; text-align: center; margin-bottom: 12px;
    }
    .title-main { color: #008751; font-weight: 900; font-size: 22px; margin: 0; }
    .title-sub  { color: #1b5e20; font-size: 13px; font-weight: 600; margin: 4px 0 0 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CONSTANTS
# ============================================================
REQUIRED_COLUMNS = [
    "community",
    "adult_population",
    "agents",
    "bank_branches",
    "avg_distance_km",
    "account_ownership_pct",
    "phone_ownership_pct",
    "network_coverage_pct",
]

SERVICES = ["Cash Withdrawal", "Cash Deposit", "Transfers", "Bill Payments", "Account Opening"]


# ============================================================
# DATA FUNCTIONS
# ============================================================
@st.cache_data
def load_sample_communities() -> pd.DataFrame:
    """Illustrative community-level data (simulated, not official statistics)."""
    return pd.DataFrame(
        {
            "community": ["Isanlu", "Ejuku", "Ife-Olukotun", "Itedo", "Ponyan"],
            "adult_population": [9500, 6200, 4800, 5400, 3900],
            "agents": [14, 7, 4, 5, 2],
            "bank_branches": [2, 0, 0, 0, 0],
            "avg_distance_km": [1.5, 6.0, 9.5, 8.0, 12.5],
            "account_ownership_pct": [58, 41, 33, 36, 27],
            "phone_ownership_pct": [82, 71, 64, 67, 58],
            "network_coverage_pct": [90, 75, 62, 68, 50],
        }
    )


@st.cache_data
def load_sample_transactions() -> pd.DataFrame:
    """Illustrative monthly agent transactions (simulated)."""
    rng = np.random.default_rng(42)
    months = pd.period_range("2025-01", periods=12, freq="M").astype(str)
    base = {
        "Cash Withdrawal": 4200,
        "Cash Deposit": 2600,
        "Transfers": 3100,
        "Bill Payments": 900,
        "Account Opening": 250,
    }
    rows = []
    for i, month in enumerate(months):
        growth = 1 + 0.03 * i  # steady adoption trend
        for service, level in base.items():
            volume = int(level * growth * rng.uniform(0.9, 1.1))
            rows.append({"month": month, "service": service, "transactions": volume})
    return pd.DataFrame(rows)


def prepare_communities(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names and add the derived indicators."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    df["agents_per_10k_adults"] = (df["agents"] / df["adult_population"] * 10_000).round(2)
    access = (1 - (df["avg_distance_km"] / 15).clip(upper=1)) * 100

    # Simple, transparent composite index (0-100). Weights are adjustable.
    df["inclusion_index"] = (
        0.35 * df["account_ownership_pct"]
        + 0.25 * access
        + 0.20 * df["phone_ownership_pct"]
        + 0.20 * df["network_coverage_pct"]
    ).round(1)

    df["priority"] = pd.cut(
        df["inclusion_index"],
        bins=[-1, 45, 60, 101],
        labels=["High priority", "Medium priority", "Better served"],
    )
    return df


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="banner"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="title-box">
        <p class="title-main">Agency Banking & Financial Inclusion</p>
        <p class="title-sub">Yagba East Local Government Area, Kogi State, Nigeria</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR: DATA SOURCE
# ============================================================
st.sidebar.header("Data Source")
source = st.sidebar.radio("Choose data:", ["Illustrative sample data", "Upload your own CSV"])

if source == "Upload your own CSV":
    st.sidebar.caption("Required columns: " + ", ".join(REQUIRED_COLUMNS))
    uploaded = st.sidebar.file_uploader("Community data (CSV)", type=["csv"])
    if uploaded is None:
        st.info("Upload a CSV in the sidebar, or switch back to the sample data.")
        st.stop()
    raw_communities = pd.read_csv(uploaded)
else:
    raw_communities = load_sample_communities()
    st.sidebar.warning("Showing simulated data for demonstration only.")

try:
    communities = prepare_communities(raw_communities)
except ValueError as err:
    st.error(str(err))
    st.stop()

transactions = load_sample_transactions()

selected = st.sidebar.multiselect(
    "Filter communities:",
    options=communities["community"].tolist(),
    default=communities["community"].tolist(),
)
view = communities[communities["community"].isin(selected)]
if view.empty:
    st.warning("Select at least one community in the sidebar.")
    st.stop()

# ============================================================
# TABS
# ============================================================
tab_overview, tab_comm, tab_tx, tab_ideas, tab_data = st.tabs(
    ["📌 Overview", "🏘️ Communities", "💳 Agent Transactions", "💡 Challenges & Recommendations", "🗂️ Data"]
)

# ---------------- OVERVIEW ----------------
with tab_overview:
    st.subheader("What is agency banking?")
    st.write(
        "Agency banking lets licensed banks and fintechs deliver basic services such as cash "
        "deposits, withdrawals, transfers and bill payments through trained agents (often shop "
        "owners or POS operators). For rural areas like Yagba East, where bank branches are few "
        "and distances are long, agents can bring services closer to residents, farmers and "
        "small traders."
    )

    total_pop = int(view["adult_population"].sum())
    weighted_accounts = (view["account_ownership_pct"] * view["adult_population"]).sum() / total_pop

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Adults covered", f"{total_pop:,}")
    c2.metric("Active agents", int(view["agents"].sum()))
    c3.metric("Agents per 10,000 adults", round(view["agents"].sum() / total_pop * 10_000, 1))
    c4.metric("Adults with an account", f"{weighted_accounts:.1f}%")

    st.markdown("#### Financial Inclusion Index by community")
    st.bar_chart(view.set_index("community")["inclusion_index"], color="#008751")
    st.caption(
        "Index (0-100) = 35% account ownership + 25% proximity to an access point "
        "+ 20% phone ownership + 20% network coverage."
    )

# ---------------- COMMUNITIES ----------------
with tab_comm:
    st.subheader("Community comparison")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Agents per 10,000 adults**")
        st.bar_chart(view.set_index("community")["agents_per_10k_adults"], color="#1b5e20")
    with col_b:
        st.markdown("**Average distance to nearest access point (km)**")
        st.bar_chart(view.set_index("community")["avg_distance_km"], color="#d32f2f")

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Account ownership (%)**")
        st.bar_chart(view.set_index("community")["account_ownership_pct"], color="#008751")
    with col_d:
        st.markdown("**Network coverage (%)**")
        st.bar_chart(view.set_index("community")["network_coverage_pct"], color="#4caf50")

    st.markdown("#### Priority ranking")
    ranking = view.sort_values("inclusion_index")[
        ["community", "inclusion_index", "priority", "agents", "avg_distance_km"]
    ]
    st.dataframe(ranking, use_container_width=True, hide_index=True)

    weakest = ranking.iloc[0]
    st.info(
        f"**{weakest['community']}** has the lowest inclusion index "
        f"({weakest['inclusion_index']}) and is the strongest candidate for new agents."
    )

# ---------------- TRANSACTIONS ----------------
with tab_tx:
    st.subheader("Agent transaction trends (illustrative)")
    pivot = transactions.pivot(index="month", columns="service", values="transactions")
    st.line_chart(pivot)

    totals = transactions.groupby("service")["transactions"].sum().sort_values(ascending=False)
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown("**Total transactions by service**")
        st.bar_chart(totals, color="#008751")
    with col_f:
        first, last = pivot.iloc[0].sum(), pivot.iloc[-1].sum()
        st.metric("Monthly volume growth (Jan to Dec)", f"{(last / first - 1) * 100:.1f}%")
        st.metric("Most used service", totals.index[0])

# ---------------- CHALLENGES & RECOMMENDATIONS ----------------
with tab_ideas:
    left, right = st.columns(2)
    with left:
        st.subheader("Key challenges")
        st.markdown(
            """
            - **Poor network coverage** in remote communities disrupts transactions.
            - **Agent liquidity shortages**: agents run out of cash, especially on market days.
            - **Low digital and financial literacy** among older and rural residents.
            - **Fraud and trust concerns** around POS and mobile money.
            - **Poor roads and power supply** raise agents' operating costs.
            - **Limited bank branches**, so agents struggle to rebalance cash.
            """
        )
    with right:
        st.subheader("Recommendations")
        st.markdown(
            """
            - **Expand agents** to the lowest-ranked communities first.
            - **Improve liquidity support**: super-agents and scheduled cash replenishment.
            - **Run community education** in local languages on safe banking.
            - **Partner with telecoms** to improve coverage in weak-signal areas.
            - **Add solar power** and offline-capable devices for agents.
            - **Target farmers, traders and women** with tailored products and savings groups.
            """
        )

    st.subheader("Suggested indicators to track")
    st.table(
        pd.DataFrame(
            {
                "Indicator": [
                    "Agents per 10,000 adults",
                    "Average distance to nearest access point",
                    "Adults with an account",
                    "Active agents (transacting monthly)",
                    "Failed transaction rate",
                ],
                "Why it matters": [
                    "Measures physical access",
                    "Measures convenience and cost of access",
                    "Core financial inclusion measure",
                    "Shows agent viability, not just registration",
                    "Reflects network and system quality",
                ],
            }
        )
    )

# ---------------- DATA ----------------
with tab_data:
    st.subheader("Community dataset")
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button(
        "📥 Download community data (CSV)",
        data=to_csv_bytes(view),
        file_name="yagba_east_agency_banking.csv",
        mime="text/csv",
    )

    st.caption(
        "Sample figures are simulated for demonstration. For research or policy use, "
        "collect real data (e.g., CBN/NIBSS agent records, EFInA surveys, or your own field survey)."
    )

st.markdown("---")
st.caption("Agency Banking & Financial Inclusion • Yagba East LGA, Kogi State")
