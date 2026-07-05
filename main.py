import openai
from config import API_KEY

def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 5)

def check_winner(board, player):
    conditions = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[2][0], board[1][1], board[0][2]]
    ]
    return any(all(cell == player for cell in condition) for condition in conditions)

def get_free_positions(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]

def gpt3_play(board, player):
    prompt = "The board is:\n{}\nIt's player {}'s turn. What's the best move?".format(
        "\n".join([" | ".join(row) for row in board]), player)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50,
        api_key=API_KEY
    )
    move = response.choices[0].text.strip().split()
    return int(move[0]), int(move[1])

def main():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "XQ"

    while True:
        print_board(board)
        if current_player == "X":
            row, col = map(int, input("Enter row and column numbers to place your mark (0-2): ").split())
        else:
            row, col = gpt3_play(board, current_player)
        
        if (row, col) in get_free_positions(board):
            board[row][col] = current_player
            if check_winner(board, current_player):
                print_board(board)
                print(f"Player {current_player} wins!")
                break
            current_player = "O" if current_player == "X" else "X"
        else:
            print("Invalid move, try again.")

        if not get_free_positions(board):
            print("It's a tie!")
            break

if __name__ == "__main__":
    main()
