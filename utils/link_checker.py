from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from config import settings

URL_RE = re.compile(r'(?i)\b(?:https?://|www\.|t\.me/|telegram\.me/)[^\s<>()]+')
SUSPICIOUS_KEYWORDS = {
    'airdrop', 'claim', 'free', 'bonus', 'reward', 'rewards', 'connect', 'wallet',
    'verify', 'validation', 'validate', 'support', 'drain', 'mint', 'presale', 'giveaway',
}
SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'cutt.ly', 'rebrand.ly'}
OFFICIAL_DOMAINS = {
    'x.com', 'twitter.com', 'dexscreener.com', 'jup.ag', 'raydium.io', 'birdeye.so',
    'solscan.io', 'solana.fm', 'pump.fun', 'www.pump.fun',
}


def _host(url: str) -> str:
    candidate = url if '://' in url else f'https://{url}'
    return (urlparse(candidate).hostname or '').lower().strip('.')


def _domain_matches(host: str, allowed: str) -> bool:
    allowed = allowed.lower().strip('.')
    return host == allowed or host.endswith(f'.{allowed}')


def official_hosts() -> set[str]:
    hosts = set(OFFICIAL_DOMAINS)
    for url in [settings.website_url, settings.twitter_url, settings.telegram_url, settings.chart_url, settings.buy_url]:
        if url:
            host = _host(url)
            if host:
                hosts.add(host)
    return hosts


@dataclass(frozen=True)
class LinkCheckResult:
    suspicious: bool
    reason: str = ''
    urls: tuple[str, ...] = ()


def extract_urls(text: str) -> list[str]:
    return [m.group(0).rstrip('.,!?;:)]}') for m in URL_RE.finditer(text or '')]


def is_official_or_safe(url: str) -> bool:
    host = _host(url)
    return bool(host and any(_domain_matches(host, allowed) for allowed in official_hosts()))


def check_links(text: str) -> LinkCheckResult:
    urls = tuple(extract_urls(text))
    if not urls:
        return LinkCheckResult(False, urls=urls)
    if len(urls) >= 4:
        return LinkCheckResult(True, 'excessive repeated links', urls)
    lowered = (text or '').casefold()
    for url in urls:
        host = _host(url)
        if not host:
            continue
        if is_official_or_safe(url):
            continue
        try:
            ipaddress.ip_address(host)
            return LinkCheckResult(True, 'raw IP address link', urls)
        except ValueError:
            pass
        if host in SHORTENERS:
            return LinkCheckResult(True, 'link shortener', urls)
        if any(word in lowered for word in SUSPICIOUS_KEYWORDS):
            return LinkCheckResult(True, 'suspicious wallet/claim link', urls)
        if host.endswith(('.zip', '.mov', '.click', '.quest', '.top', '.xyz', '.icu', '.cyou')):
            return LinkCheckResult(True, 'high-risk domain', urls)
        if host in {'t.me', 'telegram.me'} and not is_official_or_safe(url):
            return LinkCheckResult(True, 'unrelated Telegram invite link', urls)
    return LinkCheckResult(False, urls=urls)
