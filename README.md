# BeerGuy Monitor 🍺⚔️

Official BeerGuy Monitor bot for the BeerGuy community. It tracks BGUY activity on Solana, posts Telegram buy alerts, highlights big raids, welcomes new holders, and provides community commands for price, chart, contract, holders, raid, help, and info.

## Features

- 🍺 Automatic BeerGuy buy alerts
- 🚨 Big buy alerts with configurable threshold
- 🍺 New holder welcome alerts
- 📈 DexScreener-powered market data
- 🔎 Solana RPC transaction and token supply reads
- 🤖 Telegram commands: `/price`, `/chart`, `/contract`, `/holders`, `/raid`, `/links`, `/help`, `/info`
- 🤝 Community admin assistant: welcomes new members, answers greetings with cooldowns, and provides official links from keywords
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
    └── images/
        ├── buy.png
        ├── sell.png
        ├── big_buy.png
        ├── big_sell.png
        ├── liquidity.png
        ├── new_holder.png
        ├── announcement.png
        ├── giveaway.png
        ├── contest.png
        └── loading.png
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
GREETING_USER_COOLDOWN_SECONDS=600
GREETING_GROUP_COOLDOWN_SECONDS=120

# Optional image names loaded from assets/images/
BUY_IMAGE=buy.png
SELL_IMAGE=sell.png
BIG_BUY_IMAGE=big_buy.png
BIG_SELL_IMAGE=big_sell.png
LIQUIDITY_IMAGE=liquidity.png
NEW_HOLDER_IMAGE=new_holder.png
ANNOUNCEMENT_IMAGE=announcement.png
GIVEAWAY_IMAGE=giveaway.png
CONTEST_IMAGE=contest.png
LOADING_IMAGE=loading.png
LOGO_IMAGE=logo.png
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

## Community Admin Behavior

The bot acts like a friendly official BeerGuy community admin in Telegram groups:

- Welcomes new non-bot members with rotating BeerGuy-branded messages and official inline buttons.
- Replies to common English and Romanian greetings such as `gm`, `good morning`, `salut`, `bună`, `neata`, and `servus`.
- Protects the group from greeting spam with `GREETING_USER_COOLDOWN_SECONDS` and `GREETING_GROUP_COOLDOWN_SECONDS`.
- Answers link helper keywords such as `contract`, `ca`, `website`, `x`, `telegram`, `chart`, and `links` with official BeerGuy links.

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

Place production BeerGuy branded images in `assets/images/`. Images should not be stored in the repository root or directly in `assets/`; Telegram alerts resolve image names from this dedicated folder automatically.

Required/standard image slots:

- `buy.png` for standard buy alerts
- `sell.png` for sell alerts
- `big_buy.png` for big buy alerts
- `big_sell.png` for big sell alerts
- `liquidity.png` for liquidity alerts
- `new_holder.png` for first-seen holder alerts
- `announcement.png` for announcements
- `giveaway.png` for giveaways
- `contest.png` for contests
- `loading.png` for loading/status messages
- `logo.png` for branded command replies

You can keep the default names above or override them in `.env` with variables such as `BUY_IMAGE`, `BIG_BUY_IMAGE`, `NEW_HOLDER_IMAGE`, or `LOGO_IMAGE`. Each value should be only a file name, and the bot will look for it inside `assets/images/`.

If an image file is missing or empty, the bot automatically sends a text-only Telegram message instead of failing.

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
