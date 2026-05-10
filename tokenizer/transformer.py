# tokenizer/transformer.py
import numpy as np
from collections import defaultdict, Counter


class SimpleBPE:
    def __init__(self):
        self.vocab = {}
        self.vocab_r = {}
        self.merges = []

    def get_stats(self, word_freqs):
        pairs = defaultdict(int)
        for word, freq in word_freqs.items():
            symbols = list(word)
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i+1])] += freq
        return pairs

    def merge_vocab(self, pair, word_freqs):
        new_vocab = {}
        replacement = ''.join(pair)
        for word, freq in word_freqs.items():
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == pair[0] and word[i+1] == pair[1]:
                    new_word.append(replacement)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_vocab[''.join(new_word)] = freq
        return new_vocab

    def tokenize_word(self, word):
        pieces = list(word)
        for a, b in self.merges:
            new_pieces = []
            i = 0
            while i < len(pieces):
                if i < len(pieces) - 1 and pieces[i] == a and pieces[i+1] == b:
                    new_pieces.append(a + b)
                    i += 2
                else:
                    new_pieces.append(pieces[i])
                    i += 1
            pieces = new_pieces
        return pieces

    def train(self, text, num_merges=12):
        words = text.split()
        word_freqs = {}
        for word in words:
            word_freqs[word] = word_freqs.get(word, 0) + 1

        for i in range(num_merges):
            pairs = self.get_stats(word_freqs)
            if not pairs:
                break

            best_pair = max(pairs, key=pairs.get)
            self.merges.append(best_pair)
            word_freqs = self.merge_vocab(best_pair, word_freqs)

        # Build vocab from all tokens
        seen = set()
        idx = 0
        for word in word_freqs:
            tokens = self.tokenize_word(word)
            for t in tokens:
                if t not in seen:
                    self.vocab[t] = idx
                    self.vocab_r[idx] = t
                    seen.add(t)
                    idx += 1

    def encode(self, text):
        words = text.split()
        tokens = []
        for word in words:
            pieces = self.tokenize_word(word)
            for p in pieces:
                tid = self.vocab.get(p, 0)  # 0 = UNK
                tokens.append(tid)
        return tokens

    def decode(self, token_ids):
        pieces = [self.vocab_r.get(tid, "?") for tid in token_ids]
        return "".join(pieces)
