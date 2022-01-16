import re
from enum import Enum
from typing import List, Tuple

import typer

app = typer.Typer()
words = []


class WORDLE_SYMBOL(Enum):
    Y = "Y"
    G = "G"
    X = "X"


with open("./true_wordle.txt") as f:
    for line in f:
        words.append(line.strip().upper())


def handle_response(guess: str, positions: str, split_pattern: list):

    # positions can be anythin from WORDLE_SYMBOL
    # guess: shirt
    # positions: "_ G G Y _"
    # pattern: [[A-Z],[A-Z], [A-Z], [A-Z], [A-Z]]

    answer = {"eliminated_letter": [], "pattern": ""}
    wild_card = "[A-Z]"
    for idx in range(0, 5):
        current_letter = guess[idx]
        current_pattern = split_pattern[idx]
        symbol = positions[idx]
        if symbol == WORDLE_SYMBOL.X.value:
            answer["pattern"] += wild_card
            answer["eliminated_letter"].append(current_letter)
        if symbol == WORDLE_SYMBOL.Y.value:
            if current_pattern == wild_card:
                answer["pattern"] += f"[^{current_letter}]"
            else:
                # must be already a [^xyz]
                clean = clean_not_letters_pattern(current_pattern)
                new_not_letters = "".join(list(set(current_letter + clean)))
                answer["pattern"] += f"[^{new_not_letters}]"
        if symbol == WORDLE_SYMBOL.G.value:
            answer["pattern"] += f"[{current_letter}]"
    return answer


def get_a_word(pattern, eliminated_letters, words, debug = False):
    guess_pattern = re.compile(pattern)
    debug and print(f"guess {pattern} and eliminate {eliminated_letters} '\n")

    filtered_list = words
    debug and print("number of words: ", len(filtered_list), "\n")
    if eliminated_letters:
        debug and print("some eliminated using letters ", eliminated_letters, "\n")
        # 100% this could be a regex but i couldnt figure it out nor did i care to
        filtered_list = list(
            filter(
                lambda word: not any(letter in word for letter in eliminated_letters),
                filtered_list,
            )
        )
        debug and print("words left after eliminating letters", len(filtered_list))

    filtered_list = list(filter(guess_pattern.match, filtered_list))
    debug and print("words left after pattern match", len(filtered_list))
 

    try:
        if (debug and len(filtered_list) < 10):
            print(filtered_list)
        return filtered_list[0].upper()
    except Exception as e:
        # print(e)
        return None


def score_a_word(word: str, scores: dict):
    score = 0
    for letter in list(set(word)):
        score += scores[letter]
    return score


def sort_a_dict(dictionary: dict):
    return sorted(dictionary, key=dictionary.get, reverse=True)


def normalize_scores(sorted_letters: List[Tuple]):
    max = sorted_letters[0][1]
    min = sorted_letters[-1][1]
    scores = {}
    for i in range(len(sorted_letters)):
        scores[sorted_letters[i][0]] = (sorted_letters[i][1] - min) / (max - min)

    return scores


def count_letters_in_words(words: List[str]):
    letters = {}
    for word in words:
        for letter in word:
            if letter not in letters:
                letters[letter] = 1
            else:
                letters[letter] += 1
    return letters


def seperate_pattern(str_pattern: str):
    return re.findall("[^]]+]", str_pattern)


def clean_not_letters_pattern(str_pattern):
    s = str_pattern.replace("[", "")
    s = s.replace("]", "")
    s = s.replace("^", "")
    return s


# SET UP
letters = count_letters_in_words(words)

sorted_letters = sorted(letters.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)


scores = normalize_scores(sorted_letters)

scored_words = {}
for word in words:
    scored_words[word] = score_a_word(word, scores)


scored_words = sort_a_dict(scored_words)



def handle_wordle_response(response: str, guess: str, guessed_letters: list, pattern: str):
    if response == WORDLE_SYMBOL.G.value * 5:
        print("you win!")
        return
    else:
        response = handle_response(guess, response, seperate_pattern(pattern))
        guessed_letters = response["eliminated_letter"] + guessed_letters
        pattern = response["pattern"]
        return guessed_letters, pattern





def main():
    guesses = 0
    current_guessed_letters = []
    current_pattern = r"[A-Z][A-Z][A-Z][A-Z][A-Z]"
    while guesses < 10:
        guess = get_a_word(current_pattern, current_guessed_letters, scored_words)
        if isinstance(guess, str):
            print("try: ", guess)

            wordle_response = typer.prompt(f"response from wordle?")
            wordle_response = wordle_response.upper()

            if wordle_response == WORDLE_SYMBOL.G.value * 5:
                print("you win!")
                break

            response = handle_response(
                guess, wordle_response, seperate_pattern(current_pattern)
            )
            current_pattern = response["pattern"]
            current_guessed_letters = (
                response["eliminated_letter"] + current_guessed_letters
            )
            print("current guessed letters", current_guessed_letters)
            print("\n\n")
            guesses += 1
        else:
            print("no words left, some here messed up. it probably wasnt me.")
            break


if __name__ == "__main__":
    typer.run(main)
