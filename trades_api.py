from fastapi import FastAPI, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

app = FastAPI()

class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="Value of BUY for buys, SELL for sells.")
    price: float = Field(description="Price of the Trade.")
    quantity: int = Field(description="Amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None,
                                       description="Asset class of the instrument traded.")
    counterparty: Optional[str] = Field(default=None,
                                        description="Counterparty the trade was executed with.")
    instrument_id: str = Field(alias="instrumentId", description="ISIN/ID of the instrument traded.")
    instrument_name: str = Field(alias="instrumentName", description="Name of the instrument traded.")
    trade_date_time: datetime = Field(alias="tradeDateTime", description="Date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails", description="Details of the trade.")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="Name of the Trader")

# Mocked database
database = []

@app.get("/trades")
def get_trades(page: Optional[int] = Query(1, ge=1), size: Optional[int] = Query(10, ge=1, le=100)):
    start = (page - 1) * size
    end = start + size
    return database[start:end]

@app.get("/trades/{trade_id}")
def get_trade_by_id(trade_id: str):
    for trade in database:
        if trade.trade_id == trade_id:
            return trade
    return {"error": "Trade not found"}

@app.get("/trades/search")
def search_trades(search: str):
    results = []
    for trade in database:
        if (
            search.lower() in trade.counterparty.lower()
            or search.lower() in trade.instrument_id.lower()
            or search.lower() in trade.instrument_name.lower()
            or search.lower() in trade.trader.lower()
        ):
            results.append(trade)
    return results

@app.get("/trades/filter")
def filter_trades(
    assetClass: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    tradeType: Optional[str] = None
):
    filtered_trades = []
    for trade in database:
        if (
            (assetClass is None or trade.asset_class == assetClass)
            and (start is None or trade.trade_date_time >= start)
            and (end is None or trade.trade_date_time <= end)
            and (minPrice is None or trade.trade_details.price >= minPrice)
            and (maxPrice is None or trade.trade_details.price <= maxPrice)
            and (tradeType is None or trade.trade_details.buySellIndicator == tradeType)
        ):
            filtered_trades.append(trade)
    return filtered_trades

if __name__ == "__main__":
    # Mocking data for demonstration purposes
    database = [
        Trade(
            asset_class="Equity",
            counterparty="ABC Corp",
            instrument_id="AAPL",
            instrument_name="Apple Inc.",
            trade_date_time=datetime(2023, 5, 1, 10, 30),
            trade_details=TradeDetails(
                buySellIndicator="BUY",
                price=150.0,
                quantity=100
            ),
            trade_id="1",
            trader="John Doe"
        ),
        Trade(
            asset_class="Equity",
            counterparty="XYZ Inc",
            instrument_id="TSLA",
            instrument_name="Tesla Inc.",
            trade_date_time=datetime(2023, 5, 2, 9, 45),
            trade_details=TradeDetails(
                buySellIndicator="SELL",
                price=800.0,
                quantity=50
            ),
            trade_id="2",
            trader="Jane Smith"
        ),
        # Add more mocked trades here
    ]

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)