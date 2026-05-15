from tokenizer.transformer import SimpleBPE


def test_tokenizer_round_trip_preserves_spaces_and_newlines():
    text = "User: hello\nAssistant: hello there!\n"
    tok = SimpleBPE()
    tok.train(text, num_merges=20)
    ids = tok.encode(text, add_special_tokens=True)
    assert tok.decode(ids) == text


def test_tokenizer_keeps_base_characters_for_new_text():
    text = "hello hello helper"
    tok = SimpleBPE()
    tok.train(text, num_merges=20)
    assert tok.decode(tok.encode("help")) == "help"
