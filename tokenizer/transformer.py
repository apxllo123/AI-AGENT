"""A tiny educational BPE-style tokenizer.

This tokenizer is intentionally simple so the project stays understandable.
Unlike the previous version, it preserves spaces/newlines by training directly on
characters from the full corpus instead of splitting text into words.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence, Tuple


class SimpleBPE:
    """Minimal byte-pair/character tokenizer for small from-scratch models."""

    def __init__(self):
        self.vocab = {}
        self.vocab_r = {}
        self.merges: List[Tuple[str, str]] = []
        self.unk_token = "<unk>"
        self.bos_token = "<bos>"
        self.eos_token = "<eos>"

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def _apply_merges(self, pieces: List[str]) -> List[str]:
        for a, b in self.merges:
            merged = a + b
            out = []
            i = 0
            while i < len(pieces):
                if i < len(pieces) - 1 and pieces[i] == a and pieces[i + 1] == b:
                    out.append(merged)
                    i += 2
                else:
                    out.append(pieces[i])
                    i += 1
            pieces = out
        return pieces

    @staticmethod
    def _pair_counts(pieces: Sequence[str]) -> Counter:
        return Counter(zip(pieces, pieces[1:]))

    def train(self, text: str, num_merges: int = 200):
        """Train tokenizer merges on raw text while preserving whitespace."""
        if not text:
            text = "User: hello\nAssistant: hello\n"

        pieces = list(text)
        self.merges = []

        for i in range(max(0, int(num_merges))):
            pairs = self._pair_counts(pieces)
            if not pairs:
                break
            best_pair, count = pairs.most_common(1)[0]
            if count < 2:
                break
            self.merges.append(best_pair)
            pieces = self._apply_single_merge(pieces, best_pair)
            if (i + 1) % 50 == 0:
                print(f"Tokenizer merge {i + 1}/{num_merges} complete")

        special = [self.unk_token, self.bos_token, self.eos_token]
        tokens = special + sorted(set(self._apply_merges(list(text))))
        self.vocab = {tok: idx for idx, tok in enumerate(tokens)}
        self.vocab_r = {idx: tok for tok, idx in self.vocab.items()}
        print(f"Tokenizer vocab size: {len(self.vocab)}")

    @staticmethod
    def _apply_single_merge(pieces: List[str], pair: Tuple[str, str]) -> List[str]:
        a, b = pair
        merged = a + b
        out = []
        i = 0
        while i < len(pieces):
            if i < len(pieces) - 1 and pieces[i] == a and pieces[i + 1] == b:
                out.append(merged)
                i += 2
            else:
                out.append(pieces[i])
                i += 1
        return out

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        pieces = self._apply_merges(list(text or ""))
        ids = []
        if add_special_tokens:
            ids.append(self.vocab[self.bos_token])
        unk = self.vocab.get(self.unk_token, 0)
        ids.extend(self.vocab.get(piece, unk) for piece in pieces)
        if add_special_tokens:
            ids.append(self.vocab[self.eos_token])
        return ids

    def decode(self, token_ids: Iterable[int]) -> str:
        out = []
        special = {self.unk_token, self.bos_token, self.eos_token}
        for tid in token_ids:
            token = self.vocab_r.get(int(tid), self.unk_token)
            if token not in special:
                out.append(token)
        return "".join(out)


if __name__ == "__main__":
    bpe = SimpleBPE()
    sample = "User: hello\nAssistant: hello there!\n"
    bpe.train(sample, num_merges=20)
    ids = bpe.encode(sample, add_special_tokens=True)
    print(ids)
    print(bpe.decode(ids))
