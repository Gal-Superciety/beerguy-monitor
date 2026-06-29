from utils.link_checker import check_links, extract_urls
from utils.spam_detector import SpamDetector


def test_official_links_are_allowed(monkeypatch):
    monkeypatch.setenv('WEBSITE_URL', 'https://beerguy.example')
    result = check_links('BeerGuy chart https://dexscreener.com/solana/abc')
    assert not result.suspicious


def test_fake_claim_link_is_detected():
    result = check_links('Claim your free airdrop now https://bguy-claim.xyz connect wallet')
    assert result.suspicious
    assert 'wallet/claim' in result.reason


def test_telegram_invite_is_detected_when_unrelated():
    result = check_links('Join our presale group https://t.me/random_presale_gem')
    assert result.suspicious


def test_normal_greetings_are_not_spam():
    detector = SpamDetector()
    result = detector.check(1, 2, 'GM everyone, happy to be here!', now=1.0)
    assert not result.is_spam


def test_repeated_identical_messages_are_spam():
    detector = SpamDetector(repeat_threshold=3)
    assert not detector.check(1, 2, 'buy this now', now=1.0).is_spam
    assert not detector.check(1, 2, 'buy this now', now=2.0).is_spam
    result = detector.check(1, 2, 'buy this now', now=3.0)
    assert result.is_spam
    assert result.reason == 'repeated identical messages'


def test_extract_urls_handles_www_links():
    assert extract_urls('visit www.example.com now') == ['www.example.com']
