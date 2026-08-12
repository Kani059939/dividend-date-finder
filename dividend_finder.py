#!/usr/bin/env python
# coding: utf-8

# In[13]:


get_ipython().run_line_magic('pip', 'install requests')


# In[26]:


import requests
from datetime import datetime, timedelta

API_KEY = "PASTE_YOUR_API_KEY_HERE"


def next_weekday(date):
    # Saturday -> Monday
    if date.weekday() == 5:
        return date + timedelta(days=2)

    # Sunday -> Monday
    if date.weekday() == 6:
        return date + timedelta(days=1)

    return date


def get_dividend(ticker):
    ticker = ticker.strip().upper()

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "DIVIDENDS",
        "symbol": ticker,
        "apikey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Connection error:", e)
        return

    if "data" not in data:
        print("Could not find dividend data.")
        print(data)
        return

    today = datetime.today().date()
    dividends = []

    for d in data["data"]:
        ex_date = d.get("ex_dividend_date")

        if not ex_date:
            continue

        try:
            ex_date = datetime.strptime(
                ex_date, "%Y-%m-%d"
            ).date()

            dividends.append({
                "ex_date": ex_date,
                "payment_date": d.get("payment_date"),
                "amount": d.get("amount")
            })

        except ValueError:
            continue

    dividends.sort(key=lambda x: x["ex_date"])

    if not dividends:
        print(f"No dividend history found for {ticker}.")
        return

    past = [d for d in dividends if d["ex_date"] <= today]
    future = [d for d in dividends if d["ex_date"] > today]

    print("\n" + "=" * 55)
    print(f"ETF: {ticker}")
    print("=" * 55)

    # Most recent dividend
    if past:
        latest = past[-1]

        print("\nLAST KNOWN DIVIDEND")
        print("Ex-dividend date:", latest["ex_date"])
        print("Payment date:    ", latest["payment_date"])
        print("Amount:           $", latest["amount"])

    # Official future dividend
    if future:
        next_dividend = future[0]

        print("\nNEXT OFFICIAL DIVIDEND")
        print("Ex-dividend date:", next_dividend["ex_date"])
        print("Payment date:    ", next_dividend["payment_date"])
        print("Amount:           $", next_dividend["amount"])

        days_until = (next_dividend["ex_date"] - today).days
        print("Days from today: ", days_until)

    else:
        print("\nNO OFFICIAL FUTURE DIVIDEND HAS BEEN DECLARED.")

        if len(dividends) >= 3:
            # Use the average interval of the last few dividends
            recent = dividends[-4:]

            intervals = []

            for i in range(1, len(recent)):
                days = (
                    recent[i]["ex_date"] -
                    recent[i - 1]["ex_date"]
                ).days

                intervals.append(days)

            average_interval = round(
                sum(intervals) / len(intervals)
            )

            last_ex_date = recent[-1]["ex_date"]

            estimated_date = (
                last_ex_date +
                timedelta(days=average_interval)
            )

            # Make sure estimate is a weekday
            estimated_date = next_weekday(estimated_date)

            print("\nESTIMATED NEXT EX-DIVIDEND DATE")
            print("Estimated date:", estimated_date)
            print("Estimated interval:", average_interval, "days")

            days_until = (estimated_date - today).days
            print("Days from today:", days_until)

            print("\nNOTICE:")
            print("This date is an ESTIMATE based on historical")
            print("dividend timing and is NOT officially declared.")

        else:
            print("Not enough history to estimate the next dividend.")

    print("=" * 55)


ticker = input("Enter ETF ticker: ")

get_dividend(ticker)


# In[ ]:





# In[ ]:




