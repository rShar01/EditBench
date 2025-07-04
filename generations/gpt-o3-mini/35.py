import random

# ... (other unchanged code above)

# Highlighted section start
def look_up_words(n):
    try:
        with open("/usr/share/dict/words", "r") as f:
            words = f.read().splitlines()
    except FileNotFoundError:
        print("Dictionary file not found.")
        return []

    # Filter words with exactly n alphabetic characters
    valid_words = [word for word in words if len(word) == n and word.isalpha()]

    # If there are more than 10 words, randomly pick 10, otherwise return all found
    if len(valid_words) > 10:
        return random.sample(valid_words, 10)
    else:
        return valid_words

def main():
    try:
        n = int(input("Enter the number of characters for the words: "))
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    words_found = look_up_words(n)
    if words_found:
        print("Words found:")
        for word in words_found:
            print(word)
    else:
        print(f"No words found with {n} characters.")

if __name__ == "__main__":
    main()
# Highlighted section end

# ... (other unchanged code below)
