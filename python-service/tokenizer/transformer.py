from collections import defaultdict


class SimpleBPE:
    def __init__(self):
        self.vocab = {}
        self.vocab_r = {}
        self.merges = []
        self.unk_token = "<unk>"
        self.bos_token = "<bos>"
        self.eos_token = "<eos>"

    def get_stats(self, word_freqs):
        pairs = defaultdict(int)
        for word, freq in word_freqs.items():
            symbols = list(word)
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    def merge_vocab(self, pair, word_freqs):
        new_vocab = {}
        replacement = "".join(pair)
        for word, freq in word_freqs.items():
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == pair[0] and word[i + 1] == pair[1]:
                    new_word.append(replacement)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_vocab["".join(new_word)] = freq
        return new_vocab

    def tokenize_word(self, word):
        pieces = list(word)
        for a, b in self.merges:
            new_pieces = []
            i = 0
            while i < len(pieces):
                if i < len(pieces) - 1 and pieces[i] == a and pieces[i + 1] == b:
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

        for _ in range(num_merges):
            pairs = self.get_stats(word_freqs)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)
            self.merges.append(best_pair)
            word_freqs = self.merge_vocab(best_pair, word_freqs)

        tokens = [self.unk_token, self.bos_token, self.eos_token]
        seen = set(tokens)
        idx = 0

        for t in tokens:
            self.vocab[t] = idx
            self.vocab_r[idx] = t
            idx += 1

        for word in word_freqs:
            for t in self.tokenize_word(word):
                if t not in seen:
                    self.vocab[t] = idx
                    self.vocab_r[idx] = t
                    seen.add(t)
                    idx += 1

    def encode(self, text, add_special_tokens=False):
        words = text.split()
        tokens = []
        if add_special_tokens:
            tokens.append(self.vocab[self.bos_token])

        for word in words:
            pieces = self.tokenize_word(word)
            for p in pieces:
                tokens.append(self.vocab.get(p, self.vocab[self.unk_token]))

        if add_special_tokens:
            tokens.append(self.vocab[self.eos_token])

        return tokens

    def decode(self, token_ids):
        pieces = []
        for tid in token_ids:
            token = self.vocab_r.get(tid, self.unk_token)
            if token in {self.bos_token, self.eos_token, self.unk_token}:
                continue
            pieces.append(token)
        return " ".join(pieces)
