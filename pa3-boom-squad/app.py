from flask import Flask, render_template, jsonify, request, redirect, url_for
import random

app = Flask(__name__)
@app.route('/cheat', methods=['GET'])
def cheat():
    global game
    bomb_positions = []
    board = game['board']
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col]['mine']:
                bomb_positions.append({'row': row, 'col': col})
    return jsonify({'bombs': bomb_positions})

game = {
    'board': [],
    'game_over': False,
    'difficulty': 'easy'
}

def get_difficulty_settings(difficulty):
    """
    (Task 1): Implement this function to return the game board settings as a tuple:
          (rows, cols, mines) based on the given difficulty level.
          Use these settings:
            - Easy:   8 rows, 8 columns, 10 mines.
            - Medium: 16 rows, 16 columns, 40 mines.
            - Hard:   16 rows, 30 columns, 99 mines.
          This function defines the board dimensions and the number of mines.
    """
    difficulty = difficulty.lower()
    if difficulty == "easy":
        return 8, 8, 10
    elif difficulty == "medium":
        return 16, 16, 40
    elif difficulty == "hard":
        return 16, 30, 99
    else:
        return 8, 8, 10

def calculate_adjacent_mines(board, row, col):
    """
    (Task 2): Implement this function to calculate the number of adjacent mines for
          the cell at (row, col) on the board.
          It should check all 8 neighboring cells (including diagonals) and count how many
          contain a mine.
    """
    count = 0
    totals_row = len(board)
    totals_col = len(board[0])
    for a in range(row - 1, row + 2):
        for b in range(col - 1, col + 2):
            if a >= 0 and a < totals_row and b >= 0 and b < totals_col:
                if not(a == row and b == col):
                    if board[a][b]["mine"]:
                        count += 1
    return count


def generate_board(difficulty):
    """
    (Task 3): Implement this function to generate the game board as a 2D list of dictionaries.
          Each cell is represented as a dictionary containing:
            - 'mine': boolean, True if the cell contains a mine.
            - 'count': integer, number of adjacent mines (to be calculated).
            - 'revealed': boolean, True if the cell has been uncovered.
            - 'flagged': boolean, True if the cell is flagged.
          Steps:
            1. Get board dimensions and mine count using get_difficulty_settings.
            2. Create an empty board with default values.
            3. Randomly place the specified number of mines.
            4. Calculate and assign the adjacent mine count for each cell.
    """
    rows, cols, num_mines = get_difficulty_settings(difficulty)

    board = []
    for r in range(rows):
        row = []
        for c in range(cols):
            cell = {
                'mine': False,
                'count': 0,
                'revealed': False,
                'flagged': False
            }
            row.append(cell)
        board.append(row)

    all_positions = []
    for r in range(rows):
        for c in range(cols):
            all_positions.append((r, c))

    mine_positions = random.sample(all_positions, num_mines)

    for r, c in mine_positions:
        board[r][c]['mine'] = True

    for r in range(rows):
        for c in range(cols):
            if not board[r][c]['mine']:
                board[r][c]['count'] = calculate_adjacent_mines(board, r, c)

    return board

def reveal_cell(board, row, col):
    """
    (Task 4): Implement this recursive function to reveal the cell at (row, col) and its neighbors.
          When a cell is revealed:
            - Mark it as revealed.
            - If it is a mine, stop further processing.
            - If it has a non-zero adjacent mine count, do not reveal neighbors.
            - If it has zero adjacent mines, recursively reveal all neighboring cells.
          This replicates the "flood fill" behavior of Minesweeper.
    """
    rows = len(board)
    cols = len(board[0])

    if row < 0 or row >= rows or col < 0 or col >= cols:
        return board

    if board[row][col]['revealed'] or board[row][col]['flagged']:
        return board

    board[row][col]['revealed'] = True

    if board[row][col]['mine']:
        return board

    if board[row][col]['count'] == 0:
        for r in range(row - 1, row + 2):
            for c in range(col -1, col + 2):
                if r == row and c == col:
                    continue
                reveal_cell(board, r, c)

    return board

def check_win(board):
    """
    (Task 5): Implement this function to check if the player has won the game.
          The player wins when all non-mine cells are revealed.
          Return True if the game is won, otherwise return False.
    """
    for row in board:
        for cells in row:
            if cells["mine"] == False:
                if cells["revealed"] == False:
                    return False
    return True


def reveal_all_mines(board):
    """
    (Task 6): Implement this helper function to reveal all mines on the board.
          This function is called when a mine is clicked (resulting in game over),
          and it should mark every cell that contains a mine as revealed.
    """
    for row in board:
        for cell in row:
            if cell["mine"]:
                cell["revealed"] = True
    return board

def toggle_flag(board, row, col):
    """
    (Task 7): Implement this function to toggle the flag on the cell at (row, col).
          If the cell is not revealed, change its flagged status (True/False).
    """
    select_cell = board[row][col]
    if not select_cell["revealed"]:
        select_cell["flagged"] = not select_cell["flagged"]
    return board

def update_high_score(score):
    """
    (Task 8): Implement this function to update the high score stored in a file.
          It should compare the current high score with the new score and, if the new score is higher,
          overwrite the file with the new high score.
    """
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
    except (FileNotFoundError, ValueError):
        high_score = 0

    if score > high_score:
        with open("high_score.txt", "w") as file:
            file.write(str(score))

def get_high_score():
    """
    (Task 9): Implement this function to read the high score from a file.
          If the file doesn't exist or is empty, it should return 0.
    """
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
            return high_score
    except (FileNotFoundError, ValueError):
        return 0

def calculate_score(board):
    """
    (Task 10): Implement this function to calculate the score.
          The score should be defined as the number of revealed non-mine cells.
    """
    score = 0
    for row in board:
        for a in row:
            if a["revealed"] and not a["mine"]:
                score += 1
    return score

# FLASK ROUTES
@app.route('/')
def index():
    # Render the main game page.
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    # Start a new game using the selected difficulty.
    difficulty = request.form.get('difficulty', 'easy')
    game['difficulty'] = difficulty
    game['board'] = generate_board(difficulty)
    game['game_over'] = False
    return jsonify({'status': 'new game started', 'board': game['board']})

@app.route('/reveal', methods=['POST'])
def reveal():
    global game
    if game['game_over']:
        return jsonify({'status': 'game over', 'board': game['board']})
    data = request.get_json()
    row = int(data.get('row'))
    col = int(data.get('col'))
    board = game['board']
    cell = board[row][col]
    if cell['revealed'] or cell['flagged']:
        return jsonify({'status': 'already revealed', 'board': board})
    if cell['mine']:
        board = reveal_all_mines(board)
        game['game_over'] = True
        # Return game over status to trigger redirection on the client.
        return jsonify({'status': 'game over', 'board': board})
    board = reveal_cell(board, row, col)
    if check_win(board):
        game['game_over'] = True
        return jsonify({'status': 'win', 'board': board})
    return jsonify({'status': 'continue', 'board': board})

@app.route('/toggle_flag', methods=['POST'])
def toggle_flag_route():
    global game
    if game['game_over']:
        return jsonify({'status': 'game over', 'board': game['board']})
    data = request.get_json()
    row = int(data.get('row'))
    col = int(data.get('col'))
    board = game['board']
    board = toggle_flag(board, row, col)
    return jsonify({'status': 'continue', 'board': board})

@app.route('/game_over_page')
def game_over_page():
    # Retrieve the elapsed time from the query string and convert it to an integer.
    time_elapsed = int(request.args.get('time', '0'))
    # Calculate the base score as the number of revealed non-mine cells.
    base_score = calculate_score(game['board'])
    # New final score is the product of base score and time taken.
    final_score = base_score * (9999 - time_elapsed)
    # Retrieve and update the high score if necessary.
    update_high_score(final_score)
    high_score = get_high_score()  # Re-read updated high score.
    return render_template('game_over.html', score=final_score, high_score=high_score, time_elapsed=time_elapsed)

@app.route('/won_screen')
def won_screen():
    # Retrieve the elapsed time from the query string and convert it to an integer.
    time_elapsed = int(request.args.get('time', '0'))
    # Calculate the base score as the number of revealed non-mine cells.
    base_score = calculate_score(game['board'])
    # New final score is the product of base score and time taken.
    final_score = base_score * (9999-time_elapsed)
    # Retrieve and update the high score if necessary.
    update_high_score(final_score)
    high_score = get_high_score()  # Re-read updated high score.
    return render_template('won.html', score=final_score, high_score=high_score, time_elapsed=time_elapsed)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
