from typing import Union
from fastapi import FastAPI
import yfinance as yf

def getDividendRate(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    try:
        return float(stock.info['dividendRate'])
    except:
        return 0

# Gets total investment of x initial capital, with m monthly contributions for n number of years.
# And, if there is dividend d, it will be reinvested
def getTotalInvestment(ticker_symbol, initial_capital, number_of_investment_years, monthly_contribution):
    
    stock_info = yf.download([ticker_symbol], interval='1mo', rounding=False, group_by='ticker', progress=False)
    
    number_of_investment_months = number_of_investment_years * 12
    values = stock_info.get(ticker_symbol.upper())['Close'].to_list()
    number_of_months_since_stock_inception = len(values)
    
    # Usually the rate is in percentage, change it to rate first 
    dividendRate = getDividendRate(ticker_symbol) / 100

    roi_monthly = (values[number_of_months_since_stock_inception-1] - values[0]) / number_of_months_since_stock_inception
    roi_annually = roi_monthly * 12  
    
    future_value_initial = initial_capital * (1 + roi_annually / 100 + dividendRate) ** number_of_investment_years
    
    dividendRateMonthly = dividendRate / 12
    future_value_annuity = monthly_contribution * (((1 + roi_monthly/100 + dividendRateMonthly) ** number_of_investment_months) - 1) / (roi_monthly/100 + dividendRateMonthly)
    future_value_total = future_value_initial + future_value_annuity

    return {
        "ticker_symbol": ticker_symbol,
        "initial_capital": initial_capital,
        "investment_years": number_of_investment_years,
        "monthly_contribution": monthly_contribution,
        "dividendRate": dividendRate,
        "future_value_initial": f"{future_value_initial:,.2f}",
        "future_value_annuity": f"{future_value_annuity:,.2f}",
        "future_value_total": f"{future_value_total:,.2f}"
    }

app = FastAPI()

@app.get("/")
def getMessage():
    return {"message": "Howdy! Welcome to the total future investment calculator for a given stock"}

@app.get("/getTotalInvestment/{ticker_symbol}/{initial_capital}/{investment_years}/{monthly_contribution}")
def fetchTotalInvestment(ticker_symbol: str, initial_capital: int, investment_years: int, monthly_contribution: int):
    result = getTotalInvestment(ticker_symbol, initial_capital, investment_years, monthly_contribution)
    return result
