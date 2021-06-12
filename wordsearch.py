from math import ceil
import random
import sys
import time
from pyfiglet import Figlet
from plumbum import cli
import questionary
from nltk.corpus import words

def delete_last_line():
    """Delete the last line"""
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')


LETTERS = "QWERTYUIOPASDFGHJKLZXCVBNM"
DIFFICULTIES = {'Easy': '5 12', 'Medium': '7 16', 'Hard': '10 20'}
DIRECTIONS = {
    0: '-1 0',
    1: '-1 1',
    2: '0 1',
    3: '1 1',
    4: '1 0',
    5: '1 -1',
    6: '0 -1',
    7: '-1 -1',
}
INSTR = """
This is a standard word search with 3 difficulties:
    -Easy: 5 words, 12x12
    -Medium: 7 words, 16x16
    -Hard: 10 words, 20x20
The words are imported from NLTK.

If you find a word, enter the coordinates of the first letter, separated by a space.
Although the margins only show the units digit, enter the full coordinate.
The row goes first, and then the column.
The numbering starts at 1 1, which represents the top left corner.
You can always select 'exit program' to exit the program.
Enjoy!
"""

def print_block(text):
    """Print the title"""
    print(Figlet(font='doom', justify='center').renderText(text))

def select_difficulty():
    """Have user choose a difficulty"""
    return questionary.select(
        "Choose a difficulty:",
        choices=[
            'Easy',
            'Medium',
            'Hard',
        ]).ask()

def found_words(to_find):
    """Display words left to find"""
    return questionary.select(
        'Check off when found:',
        choices=to_find
    ).ask()

def check_found_word(word):
    """Check if the user really found a word"""
    return questionary.text(f"Enter coordinates of the first letter of {word}:").ask()

def create_letter_list_2d(board_size: int, random_words):
    """Create the 2d list of letters to "paste" onto board"""
    def find_space(word, start_row, start_col, direction):
        del_row = int(DIRECTIONS[direction].split()[0])
        del_col = int(DIRECTIONS[direction].split()[1])
        has_space = True

        curr_row = start_row
        curr_col = start_col
        for i in word:
            if letter_list[curr_row][curr_col] != ' ' and letter_list[curr_row][curr_col] != i:
                has_space = False
                break
            curr_row += del_row
            curr_col += del_col

        if has_space:
            # Add to dictionary only if there is space
            start_pos[word] = f'{start_row + 1} {start_col + 1}'

            curr_row = start_row
            curr_col = start_col
            for let in word:
                # Add to 2d list only if there is space
                letter_list[curr_row][curr_col] = let

                curr_row += del_row
                curr_col += del_col
        return has_space

    letter_list = [[' ' for i in range(board_size)] for j in range(board_size)]
    start_pos = {}
    for word in random_words:
        success = False
        while not success:
            direction = random.randrange(8)
            start_coords = ""
            start_row = ""
            start_col = ""

            # N
            if direction == 0:
                start_row = random.randrange(len(word) - 1, board_size)
                start_col = random.randrange(board_size)
            # NE
            elif direction == 1:
                start_row = random.randrange(len(word) - 1, board_size)
                start_col = random.randrange(board_size - len(word) + 1)
            # E
            elif direction == 2:
                start_row = random.randrange(board_size)
                start_col = random.randrange(board_size - len(word) + 1)
            # SE
            elif direction == 3:
                start_row = random.randrange(board_size - len(word) + 1)
                start_col = random.randrange(board_size - len(word) + 1)
            # S
            elif direction == 4:
                start_row = random.randrange(board_size - len(word) + 1)
                start_col = random.randrange(board_size)
            # SW
            elif direction == 5:
                start_row = random.randrange(board_size - len(word) + 1)
                start_col = random.randrange(len(word) - 1, board_size)
            # W
            elif direction == 6:
                start_row = random.randrange(board_size)
                start_col = random.randrange(len(word) - 1, board_size)
            # NW
            else:
                start_row = random.randrange(len(word) - 1, board_size)
                start_col = random.randrange(len(word) - 1, board_size)

            start_coords = f'{start_row} {start_col}'
            success = find_space(word, int(start_coords.split()[0]),
                int(start_coords.split()[1]), direction)

    for i in range(board_size):
        for j in range(board_size):
            if letter_list[i][j] == ' ':
                letter_list[i][j] = random.choice(LETTERS)
    return [letter_list, start_pos]

def print_board(input_list):
    """Paste the 2d list of letters onto a square board"""
    v_spacing_list = [f'{(i + 1) % 10} ' for i,_ in enumerate(input_list)]
    print(f"\n{''.join(v_spacing_list).rjust(2 * len(v_spacing_list) + 20)}\n")
    for i,_ in enumerate(input_list):
        h_spacing = f'{(i + 1) % 10}  '
        print(h_spacing.rjust(20), end='')
        for j,_ in enumerate(input_list[i]):
            print(f'{input_list[i][j]} ', end='')
        print(f'  {h_spacing} ')
    print(f"\n{''.join(v_spacing_list).rjust(2 * len(v_spacing_list) + 20)}\n")

def generate_words(num_words: int, board_size: int):
    """Generate random words of valid length"""
    my_words = []
    while len(my_words) < num_words:
        random_word = random.choice(words.words()).upper()
        if len(random_word) in range(ceil(board_size / 4), board_size + 1):
            my_words.append(random_word)
    return my_words

class Game(cli.Application):
    VERSION = "1.0"
    instructions = cli.Flag(['i', 'instructions'], help="Read the instructions")

    def main(self):
        print_block("Word Search")

        if self.instructions:
            print(INSTR)
            time.sleep(10)

        diff = DIFFICULTIES[select_difficulty()].split()
        random_list = generate_words(int(diff[0]), int(diff[1]))
        random_letter_list = create_letter_list_2d(int(diff[1]), random_list)
        my_list = random_letter_list[0]
        my_pos = random_letter_list[1]

        print_board(my_list)
        random_list.append('exit program')

        print('Remaining words:')
        while len(random_list) > 1:
            has_found = found_words(random_list)
            if has_found == 'exit program':
                sys.exit()
            if check_found_word(has_found) == my_pos[has_found]:
                print("Nice!")
                random_list.remove(has_found)
            else:
                print("Try again.")
            time.sleep(0.5)
            for _ in range(3):
                delete_last_line()
        print("\nCongrats! You win!")

if __name__ == "__main__":
    Game()

def test_create_letter_list_2d():
    """Test the `create_letter_list_2d` method"""
    my_words = generate_words(5, 12)
    assert len(my_words) == 5
    assert len(create_letter_list_2d(12, my_words)[1]) == 5

def test_generate_words():
    """Test the `generate_words` method"""
    my_words = generate_words(3, 8)
    for word in my_words:
        assert len(word) in range(2, 9)
    assert len(my_words) == 3
