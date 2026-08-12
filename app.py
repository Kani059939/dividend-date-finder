import streamlit as st
import requests
from datetime import datetime, timedelta


st.set_page_config(
    page_title="Dividend Date Finder",
    page_icon="💰"
)


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

st.title("💰 Dividend Date Finder")
st.write(
    "Enter a stock or ETF ticker to find its latest and "
    "upcoming dividend information."
)


ticker = st.text_input(
    "Enter ticker",
    placeholder="Example: JEPI, JEPQ, SCHD, HAL.NSE"
).strip().upper()


# ---------------------------------------------------------
# INDIAN STOCKS
# ---------------------------------------------------------

INDIAN_STOCKS = {
    "HAL.NSE": {
        "name": "Hindustan Aeronautics Limited",
        "exchange": "NSE",
        "currency": "INR",
        "last_ex_date": "2026-08-14",
        "last_payment_date": None,
        "last_amount": 10.00
    }
}


# ---------------------------------------------------------
# US / ETF LOOKUP
# ---------------------------------------------------------

def get_us_dividend(ticker):

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "DIVIDENDS",
        "symbol": ticker,
        "apikey": API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    data = response.json()

    if "data" not in data:

        if "Note" in data:
            st.error(data["Note"])

        elif "Information" in data:
            st.error(data["Information"])

        else:
            st.error("No dividend data found.")

        return

    today = datetime.today().date()

    dividends = []

    for d in data["data"]:

        ex_date = d.get("ex_dividend_date")

        if not ex_date:
            continue

        try:

            ex_date = datetime.strptime(
                ex_date,
                "%Y-%m-%d"
            ).date()

            dividends.append({
                "ex_date": ex_date,
                "payment_date": d.get("payment_date"),
                "amount": d.get("amount")
            })

        except ValueError:
            continue


    dividends.sort(
        key=lambda x: x["ex_date"]
    )


    if not dividends:
        st.warning(
            f"No dividend history found for {ticker}."
        )
        return


    past = [
        d for d in dividends
        if d["ex_date"] <= today
    ]

    future = [
        d for d in dividends
        if d["ex_date"] > today
    ]


    # -----------------------------------------------------
    # LAST DIVIDEND
    # -----------------------------------------------------

    if past:

        latest = past[-1]

        st.subheader("Last Known Dividend")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ex-dividend date",
            latest["ex_date"].strftime("%B %d, %Y")
        )

        col2.metric(
            "Payment date",
            latest["payment_date"] or "N/A"
        )

        col3.metric(
            "Amount",
            f"${float(latest['amount']):.5f}"
        )


    # -----------------------------------------------------
    # OFFICIAL FUTURE DIVIDEND
    # -----------------------------------------------------

    if future:

        next_dividend = future[0]

        days_until = (
            next_dividend["ex_date"] - today
        ).days

        st.success(
            "NEXT OFFICIAL DIVIDEND"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ex-dividend date",
            next_dividend["ex_date"].strftime(
                "%B %d, %Y"
            )
        )

        col2.metric(
            "Payment date",
            next_dividend["payment_date"] or "N/A"
        )

        col3.metric(
            "Dividend",
            f"${float(next_dividend['amount']):.5f}"
        )

        st.info(
            f"⏰ {days_until} days away"
        )

        return


    # -----------------------------------------------------
    # ESTIMATE
    # -----------------------------------------------------

    st.warning(
        "No official future dividend has been declared."
    )

    if len(dividends) >= 3:

        recent = dividends[-4:]

        intervals = []

        for i in range(1, len(recent)):

            difference = (
                recent[i]["ex_date"]
                - recent[i - 1]["ex_date"]
            ).days

            intervals.append(difference)

        average_interval = round(
            sum(intervals) / len(intervals)
        )

        estimated_date = (
            recent[-1]["ex_date"]
            + timedelta(days=average_interval)
        )


        # Move weekends to Monday
        if estimated_date.weekday() == 5:
            estimated_date += timedelta(days=2)

        elif estimated_date.weekday() == 6:
            estimated_date += timedelta(days=1)


        days_until = (
            estimated_date - today
        ).days


        st.subheader(
            "Estimated Next Ex-dividend Date"
        )

        st.metric(
            "Estimated date",
            estimated_date.strftime(
                "%B %d, %Y"
            )
        )

        st.write(
            f"Approximately **{days_until} days away**."
        )

        st.caption(
            "⚠️ This is an estimate based on historical "
            "dividend timing. It is not an officially "
            "declared date."
        )


# ---------------------------------------------------------
# INDIAN STOCK
# ---------------------------------------------------------

def get_indian_dividend(ticker):

    stock = INDIAN_STOCKS[ticker]

    today = datetime.today().date()

    ex_date = datetime.strptime(
        stock["last_ex_date"],
        "%Y-%m-%d"
    ).date()

    days_away = (
        ex_date - today
    ).days


    st.subheader(
        stock["name"]
    )

    st.write(
        f"**Exchange:** {stock['exchange']}"
    )

    st.write(
        f"**Ticker:** {ticker}"
    )


    col1, col2 = st.columns(2)

    col1.metric(
        "Dividend per share",
        f"₹{stock['last_amount']:.2f}"
    )

    col2.metric(
        "Record / Ex-date",
        ex_date.strftime("%B %d, %Y")
    )


    if days_away >= 0:

        st.info(
            f"⏰ {days_away} days away"
        )

    else:

        st.warning(
            "This date has already passed."
        )

    st.success(
        "STATUS: Official"
    )


# ---------------------------------------------------------
# RUN SEARCH
# ---------------------------------------------------------

if ticker:

    with st.spinner("Looking up dividend information..."):

        if ticker in INDIAN_STOCKS:

            get_indian_dividend(ticker)

        else:

            get_us_dividend(ticker)
