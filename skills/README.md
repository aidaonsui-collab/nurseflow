# Aftermath Trading Bot

Futures trading bot that combines:
- **TradingView** - Chart analysis & signal identification
- **Aftermath Finance** - Perpetuals execution on Sui

## Setup

1. Install dependencies:
```bash
pip install aiohttp python-dotenv
```

2. Set environment variables:
```bash
export WALLET_PRIVATE_KEY="your-sui-private-key"
export TELEGRAM_CHAT_ID="your-chat-id"  # Optional
```

3. Configure in `config.py`:
- Wallet address
- Risk parameters (stop loss, take profit)
- Position sizes

## How It Works

1. **Read TradingView** - Bot reads current price, EMA, RSI from your chart
2. **Calculate Signal** - Based on:
   - Price vs EMA alignment
   - RSI zone (30-70 = neutral, <30 oversold, >70 overbought)
   - Trend direction
3. **Execute Trade** - Opens position on Aftermath perpetuals
4. **Manage Risk** - Auto stop-loss and take-profit

## Current Chart Settings (Hector's)

| Indicator | Value |
|-----------|-------|
| Symbol | BTCUSD |
| Timeframe | 5m |
| EMA | 9 period |
| RSI | 7 period, 30/70 zones |
| MTI | Market Trend Indicator |

## Running

```bash
# Dry run (no real trades)
python main.py --symbol BTCUSD --dry-run

# Live trading
python main.py --symbol BTCUSD
```

## Adding More Symbols

Edit `config.py` to add:
- SOLUSDT - Solana perpetual
- SUIUSD - Sui perpetual (our focus!)
- ETHBTC - Ethereum/Bitcoin

## Files

- `main.py` - Entry point
- `aftermath-bot.py` - Aftermath API integration
- `tradingview_reader.py` - TradingView chart reading
- `config.py` - Configuration
