def search(phrase, letters='aeiou'):
    return set(letters).intersection(set(phrase))