from collections import defaultdict
import re

class SimpleBPE:
    def __init__(self):
        self.vocab = {}
        self.vocab_r = {}
        self.merges = []
        self.unk_token = "<unk>"
        self.bos_token = "<bos>"
        self.eos_token = "<eos>"
        
    def train(self, text: str, num_merges: int = 50):
        """Train a simple BPE tokenizer"""
        if not text.strip():
            text = "hello world ai agent code money learn"
        
        # Start with characters
        words = re.findall(r'\w+|[^\w\s]', text.lower())
        word_freqs = defaultdict(int)
        for word in words:
            word_freqs[' '.join(list(word))] += 1  # character level initial
        
        print(f"Training BPE with {num_merges} merges on {len(words)} words...")
        
        for i in range(num_merges):
            pairs = self.get_stats(word_freqs)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)
            self.merges.append(best_pair)
            word_freqs = self.merge_vocab(best_pair, word_freqs)
            
            if i % 10 == 0:
                print(f"Merge {i+1}/{num_merges} completed")
        
        # Build vocabulary
        self.vocab = {}
        self.vocab_r = {}
        idx = 0
        
        special_tokens = [self.unk_token, self.bos_token, self.eos_token]
        for t in special_tokens:
            self.vocab[t] = idx
            self.vocab_r[idx] = t
            idx += 1
        
        # Add learned tokens
        for merged_word in word_freqs.keys():
            for token in merged_word.split():
                if token not in self.vocab:
                    self.vocab[token] = idx
                    self.vocab_r[idx] = token
                    idx += 1
        
        print(f"✅ BPE Training finished. Vocab size: {len(self.vocab)}")
    
    def get_stats(self, word_freqs):
        pairs = defaultdict(int)
        for word, freq in word_freqs.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    def merge_vocab(self, pair, word_freqs):
        new_vocab = {}
        replacement = ' '.join(pair)
        for word, freq in word_freqs.items():
            new_word = word.replace(' '.join(pair), replacement)
            new_vocab[new_word] = freq
        return new_vocab

    def encode(self, text: str, add_special_tokens: bool = True):
        """Convert text to token ids"""
        if not text:
            return []
        
        text = text.lower()
        words = re.findall(r'\w+|[^\w\s]', text)
        tokens = []
        
        if add_special_tokens:
            tokens.append(self.vocab[self.bos_token])
        
        for word in words:
            # Start with characters
            pieces = list(word)
            # Apply merges
            for a, b in self.merges:
                i = 0
                while i < len(pieces) - 1:
                    if pieces[i] == a and pieces[i + 1] == b:
                        pieces[i] = a + b
                        del pieces[i + 1]
                    else:
                        i += 1
            # Convert to ids
            for p in pieces:
                tokens.append(self.vocab.get(p, self.vocab[self.unk_token]))
        
        if add_special_tokens:
            tokens.append(self.vocab[self.eos_token])
        
        return tokens

    def decode(self, token_ids):
        """Convert token ids back to text"""
        pieces = []
        for tid in token_ids:
            token = self.vocab_r.get(tid, self.unk_token)
            if token in {self.bos_token, self.eos_token, self.unk_token}:
                continue
            pieces.append(token)
        return "".join(pieces).replace(" ", " ")  # Clean spacing


# Quick test when running directly
if __name__ == "__main__":
    bpe = SimpleBPE()
    bpe.train("hello ai agent fix code make money learn fast", num_merges=30)
    print("Test encode:", bpe.encode("hello ai agent"))
    print("Test decode:", bpe.decode(bpe.encode("hello how are you")))
