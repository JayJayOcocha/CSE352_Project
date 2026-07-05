from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from cachetools import TTLCache, cached
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cache = TTLCache(maxsize=100, ttl=600)

model_name = "gpt2"  
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

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

def simple_ai_move(board):
    for r, c in get_free_positions(board):
        return r, c
    return None, None

@cached(cache, key=lambda board, player: (tuple(map(tuple, board)), player))
def gpt_play(board, player):
    try:
        prompt = (
            "The current board state is:\n"
            f"{board[0][0]} | {board[0][1]} | {board[0][2]}\n"
            f"{board[1][0]} | {board[1][1]} | {board[1][2]}\n"
            f"{board[2][0]} | {board[2][1]} | {board[2][2]}\n"
            f"Next player: {player}\n"
            "Provide the next move in the format 'row,col'. Only respond with the move."
        )

        inputs = tokenizer.encode(prompt, return_tensors='pt')
        outputs = model.generate(inputs, max_length=inputs.shape[1] + 20, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)

        move = tokenizer.decode(outputs[0], skip_special_tokens=True).strip().split()[-1]
        if ',' in move:
            row, col = map(int, move.split(','))
            if (row, col) in get_free_positions(board):
                return row, col
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

    return None, None

def gpt_play_no_cache(board, player):
    try:
        prompt = (
            "The current board state is:\n"
            f"{board[0][0]} | {board[0][1]} | {board[0][2]}\n"
            f"{board[1][0]} | {board[1][1]} | {board[1][2]}\n"
            f"{board[2][0]} | {board[2][1]} | {board[2][2]}\n"
            f"Next player: {player}\n"
            "Provide the next move in the format 'row,col'. Only respond with the move."
        )

        inputs = tokenizer.encode(prompt, return_tensors='pt')
        outputs = model.generate(inputs, max_length=inputs.shape[1] + 20, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)

        move = tokenizer.decode(outputs[0], skip_special_tokens=True).strip().split()[-1]
        if ',' in move:
            row, col = map(int, move.split(','))
            if (row, col) in get_free_positions(board):
                return row, col
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

    return None, None

@app.route('/', methods=['GET'])
def index():
    session['board'] = [[" " for _ in range(3)] for _ in range(3)]
    session['current_player'] = 'X'
    session['winner'] = None
    return render_template('index.html', board=session['board'], winner=session['winner'])

@app.route('/play', methods=['POST'])
def play():
    move = request.form.get('move')
    if move:
        row, col = map(int, move.split(','))
        board = session['board']
        current_player = session['current_player']
        
        if (row, col) in get_free_positions(board):
            board[row][col] = current_player
            if check_winner(board, current_player):
                session['winner'] = f"Player {current_player} wins!"
                return jsonify(winner=session['winner'], board=board)
            session['current_player'] = 'O' if current_player == 'X' else 'X'
            
            if session['current_player'] != 'X':  # GPT plays here if not human's turn
                start_time = time.time()
                row, col = gpt_play(board, 'O')
                end_time = time.time()
                cached_time = end_time - start_time

                start_time = time.time()
                row_no_cache, col_no_cache = gpt_play_no_cache(board, 'O')
                end_time = time.time()
                no_cache_time = end_time - start_time

                if row is None or col is None:
                    row, col = simple_ai_move(board)
                if row is not None and col is not None:
                    board[row][col] = 'O'
                    if check_winner(board, 'O'):
                        session['winner'] = "Player O wins!"
                        return jsonify(winner=session['winner'], board=board, cached_time=cached_time, no_cache_time=no_cache_time)
                    session['current_player'] = 'X'
                else:
                    print("No response from the model. Please try again.")
                
            session['board'] = board
            return jsonify(board=board, cached_time=cached_time, no_cache_time=no_cache_time)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
