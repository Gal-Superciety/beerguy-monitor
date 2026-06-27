from chain.classify import TxType, classify_transaction
def test_classifies_explicit_buy(): assert classify_transaction({'type':'BUY'}) == TxType.BUY
def test_classifies_deltas_sell(): assert classify_transaction({'token_delta':-10,'quote_delta':1}) == TxType.SELL
def test_transfer_fallback(): assert classify_transaction({}) == TxType.TRANSFER
