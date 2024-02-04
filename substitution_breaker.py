import numpy as np
from pathlib import Path

from PIL import Image
import pickle

def decrypt_language(language_path: Path):
    screenshots_path = language_path / 'screenshots'
    alphabet_path = language_path / 'alphabet'

    alphabet_mapping = {}

    attempt_path = language_path / 'decode_attempt.txt'
    if attempt_path.exists():
        with open(attempt_path) as f:
            decode_attempt = f.read()
    else:
        attempt_path.touch()
        decode_attempt = ""
    decode_attempt = decode_attempt.strip()

    with open(language_path / 'keys.pickle', 'rb') as f:
        textboxes = pickle.load(f)


    for hintline, keyline in zip(decode_attempt.split('\n'), textboxes):
        # print(hintline, keyline)
        for hint, key in zip(hintline, keyline):
            if hint != "_":
                assert alphabet_mapping.get(key, hint) == hint, f"incompatible! {key} -> {alphabet_mapping.get(key)} = {repr(hint)}"
                alphabet_mapping[key] = hint
                # print(f'{key} -> {hint}')

    translations = '\n'.join(''.join(alphabet_mapping.get(c, '_') for c in box) for box in textboxes)
    print(translations)

    remaining = set('qwertyuiopasdfghjklzxcvbnm') - set(alphabet_mapping.values())
    print()
    print('remaining: ', ' '.join(sorted(remaining)))

def main():
    language_path = Path("./language_purple")
    decrypt_language(language_path)

if __name__ == '__main__':
    main()
