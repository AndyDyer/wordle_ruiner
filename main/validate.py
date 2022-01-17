import copy
import csv

from tqdm import tqdm
from joblib import Parallel, delayed

from ruiner import (
    WORDLE_SYMBOL,
    handle_response,
    seperate_pattern,
    sort_words_by_score,
    get_a_word,
    words,
)


def build_wordle_pattern(guess: str, answer: str):
    response = ""
    for idx in range(0, 5):
        if answer[idx] == guess[idx]:
            response += WORDLE_SYMBOL.G.value
        elif guess[idx] in answer:
            response += WORDLE_SYMBOL.Y.value
        else:
            response += WORDLE_SYMBOL.X.value
    return response




def play_self(word, debug=False):
    guesses = 0
    words_in_play = copy.deepcopy(words)
    current_guessed_letters = []
    current_pattern = r"[A-Z][A-Z][A-Z][A-Z][A-Z]"
    debug and print('WORD ', word)
    try:
        while guesses < 6:
            words_in_play = sort_words_by_score(words_in_play)
            guess = get_a_word(current_pattern, current_guessed_letters, words_in_play, debug=debug)
            if guess:
                debug and print("try: ", guess)

                wordle_response = build_wordle_pattern(guess, word)
                debug and print("WORDLE RESPONDED: ", wordle_response)

                if wordle_response == WORDLE_SYMBOL.G.value * 5:
                    debug and print("you win!")
                    return {"word": word, "status": guesses}
                   

                response = handle_response(
                    guess, wordle_response, seperate_pattern(current_pattern)
                )
                current_pattern = response["pattern"]
                current_guessed_letters = (
                    response["eliminated_letter"] + current_guessed_letters
                )
                debug and print("current guessed letters", current_guessed_letters)
                debug and print("\n\n")
                guesses += 1
            else:
                debug and print(
                    "no words left, some here messed up. it probably wasnt me."
                )
                return {"word": word, "status": "ERROR IN LOGIC"}
                return

        return {"word": word, "status": "NO MORE GUESSES"}
    except Exception as e:
        print (e)
        return {"word": word, "status": "ERROR IN LOGIC"}


validate = Parallel(n_jobs=-1)(delayed(play_self)(word) for word in tqdm(words))


with open("validation.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["word", "status"])
    writer.writeheader()
    writer.writerows(validate)


how_many_fails = len([x for x in validate if x["status"] == "NO MORE GUESSES"])
guesses = [x["status"] for x in validate if isinstance(x["status"], int)]


print ("how many fails: ", how_many_fails)
print ("success %: ", (1- ((how_many_fails / len(validate)))* 100))
print ("average guesses of win: ", sum(guesses) / len(guesses))

