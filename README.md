# BeerGuy Monitor

Modular Telegram bot for monitoring BeerGuy / BGUY on Solana.

## Structure

- `main.py` wires the Telegram application.
- `config.py` loads `.env` values.
- `bot/` contains commands, keyboards, callbacks, and alert sending.
- `chain/` contains Solana RPC, Helius, Birdeye, DexScreener, pool config, and transaction classification helpers.
- `services/` contains price, liquidity, holders, volume, LP rewards, fixed replies, and status services.
- `storage/` contains JSON and asset helpers.
- `assets/images/` contains alert/reply images. Missing images are skipped safely.

## Environment

Copy `.env.example` or set these variables:

```env
TELEGRAM_BOT_TOKEN=
ADMIN_TELEGRAM_ID=
TELEGRAM_PRIVATE_CHAT_ID=
ENABLE_PRIVATE_ALERTS=true
TELEGRAM_GROUP_CHAT_ID=
ENABLE_GROUP_ALERTS=false
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=
HELIUS_API_KEY=
BIRDEYE_API_KEY=
TOKEN_SYMBOL=BGUY
TOKEN_MINT=
TOKEN_DECIMALS=6
QUOTE_SYMBOL=SOL
QUOTE_MINT=So11111111111111111111111111111111111111112
PRICE_URL=
CHART_URL=
BUY_URL=
TWITTER_URL=
WEBSITE_URL=
TELEGRAM_URL=
MIN_ALERT_USD=25
BIG_ALERT_USD=500
WHALE_ALERT_USD=2500
```

## Commands

`/start`, `/menu`, `/status`, `/price`, `/liquidity`, `/holders`, `/buy`, `/chart`, `/testalert`, `/admin`.

## Fixed replies

The bot responds deterministically. `Hi` is a greeting, not GM. GM replies are only used for `gm`, `good morning`, or `bună dimineața`.

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Tests

```bash
pytest
```
