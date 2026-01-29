from flask import Flask, jsonify, render_template
from rubik_engine import RubiksCube

app = Flask(__name__)
game = RubiksCube()

# --- WEB UI ROUTE ---
@app.route('/')
def home():
    return render_template('index.html') 

# --- API ROUTES ---
@app.route('/scramble')
def scramble_cube():
    global game
    game = RubiksCube()
    moves = game.scramble(5) 
    return jsonify({
        "message": "Scrambled",
        "moves_made": moves,
        "state": game.cube.tolist()
    })

@app.route('/solve-custom')
def solve_custom():
    # A* Logic
    solution = game.solve_astar(max_depth=12)
    if solution:
        return jsonify({"method": "Custom A* AI", "solution": solution})
    else:
        return jsonify({"method": "Custom A*", "error": "AI gave up (Too deep)"})

@app.route('/solve-fast')
def solve_fast():
    # Instant Reverse Logic
    solution = game.solve_fast_reverse()
    return jsonify({
        "method": "Reverse Logic",
        "solution": solution
    })

if __name__ == '__main__':
    app.run(debug=True)