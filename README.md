# BeerGuy Monitor 🍺⚔️

Official BeerGuy Monitor bot for the BeerGuy community. It tracks BGUY activity on Solana, posts Telegram buy alerts, highlights big raids, welcomes new holders, and provides community commands for price, chart, contract, holders, raid, help, and info.

## Features

- 🍺 Automatic BeerGuy buy alerts
- 🚨 Big buy alerts with configurable threshold
- 🍺 New holder welcome alerts
- 📈 DexScreener-powered market data
- 🔎 Solana RPC transaction and token supply reads
- 🤖 Telegram commands: `/price`, `/chart`, `/contract`, `/holders`, `/raid`, `/help`, `/info`
- 🐳 Docker-ready deployment
- 🧩 Modular structure for future sell, liquidity, burn, whale, volume, raid reminder, X, Discord, and website API integrations

## Project Structure

```text
beerguy-monitor/
├── bot.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── Dockerfile
├── services/
│   ├── solana.py
│   ├── dexscreener.py
│   ├── price.py
│   ├── holders.py
│   └── alerts.py
├── commands/
│   ├── price.py
│   ├── chart.py
│   ├── contract.py
│   ├── holders.py
│   ├── info.py
│   └── raid.py
├── utils/
│   ├── formatters.py
│   ├── images.py
│   └── logger.py
└── assets/
    ├── buy.png
    ├── big_buy.png
    ├── new_holder.png
    └── logo.png
```

## Requirements

- Python 3.12+
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- Telegram chat ID where alerts should be posted
- Solana RPC endpoint
- BGUY token mint address
- DexScreener chart URL

## Installation

```bash
git clone https://github.com/your-org/beerguy-monitor.git
cd beerguy-monitor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with production values:

```env
TELEGRAM_TOKEN=123456:telegram-token
TELEGRAM_CHAT_ID=-1001234567890
SOLANA_RPC=https://api.mainnet-beta.solana.com
TOKEN_MINT=BGUY_TOKEN_MINT
DEXSCREENER_URL=https://dexscreener.com/solana/BGUY_PAIR
MIN_BUY_ALERT=25
BIG_BUY_ALERT=500
POLL_INTERVAL=20
```

## Running Locally

```bash
python bot.py
```

The bot uses Telegram polling and starts the Solana alert monitor as a background task.

## Docker

```bash
docker build -t beerguy-monitor .
docker run --env-file .env beerguy-monitor
```

## Deployment Notes

### Railway or Render

1. Create a new Python or Docker service.
2. Add the environment variables from `.env.example`.
3. Use `python bot.py` as the start command for Python deployments, or deploy the included Dockerfile.

### VPS

1. Install Python 3.12+.
2. Clone the repository.
3. Install dependencies in a virtual environment.
4. Create `.env`.
5. Run with `systemd`, `supervisor`, or Docker.

## Alert Behavior

Buy alert messages include:

- SOL spent
- BGUY received
- Estimated USD value
- Shortened buyer wallet
- Solscan transaction link
- DexScreener chart link

Big buys use the `BIG_BUY_ALERT` threshold and the headline:

```text
🚨 BIG BEER RAID 🚨
```

New first-seen buyers receive a holder welcome alert:

```text
🍺 NEW BEER RAIDER 🍺
```

## Assets

Place production BeerGuy branded images in `assets/`:

- `buy.png` for standard buy alerts
- `big_buy.png` for big buy alerts
- `new_holder.png` for first-seen holder alerts
- `logo.png` for future branding use

If an image file is missing or empty, the bot automatically sends a text-only Telegram message.

## Future Extensions

The service layout is designed to add:

- Sell alerts
- Liquidity alerts
- Burn alerts
- Whale tracking
- New LP detection
- Volume tracking
- Price change alerts
- Trending notifications
- Admin commands
- Automatic raid reminders
- Twitter/X integration
- Discord integration
- Website API
- Multi-language support

## Important Implementation Note

Solana DEX parsing varies by aggregator and pool program. Version 1 includes a conservative best-effort parser based on SOL balance deltas and BGUY token balance increases. For high-volume production use, add a dedicated swap parser for the exact BeerGuy liquidity venue once the official pool address and program are finalized.
