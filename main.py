
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from strategy_runner import run_strategy

app = FastAPI()

API_TOKEN = "0691bV33"  # Dopasuj do tego, co masz w GPT → nagłówek X-Token

class SymbolRequest(BaseModel):
    symbol: str

@app.post("/run-strategy")
async def run_trading_strategy(request: SymbolRequest, x_token: str = Header(...)):
    if x_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = run_strategy(request.symbol)
    return {"status": "success", "symbol": request.symbol, "details": result}
