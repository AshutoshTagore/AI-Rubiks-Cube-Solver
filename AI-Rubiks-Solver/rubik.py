import numpy as np
import random
import copy
import heapq
import colorama
from colorama import Fore, Style

# Initialize Colors for Windows
colorama.init(autoreset=True)

class RubiksCube:
    def __init__(self):
        # 0:Up, 1:Down, 2:Front, 3:Back, 4:Right, 5:Left
        self.cube = np.zeros((6, 3, 3), dtype=int)
        for i in range(6):
            self.cube[i] = i 

    # --- MOVES ---
    def rotate_front_clockwise(self):
        self.cube[2] = np.rot90(self.cube[2], k=-1)
        temp = self.cube[0, 2, :].copy()
        self.cube[0, 2, :] = self.cube[5, :, 2][::-1]
        self.cube[5, :, 2] = self.cube[1, 0, :]
        self.cube[1, 0, :] = self.cube[4, :, 0][::-1]
        self.cube[4, :, 0] = temp

    def rotate_back_clockwise(self):
        self.cube[3] = np.rot90(self.cube[3], k=-1)
        temp = self.cube[0, 0, :].copy()
        self.cube[0, 0, :] = self.cube[4, :, 2]
        self.cube[4, :, 2] = self.cube[1, 2, :][::-1]
        self.cube[1, 2, :] = self.cube[5, :, 0]
        self.cube[5, :, 0] = temp[::-1]

    def rotate_up_clockwise(self):
        self.cube[0] = np.rot90(self.cube[0], k=-1)
        temp = self.cube[2, 0, :].copy()
        self.cube[2, 0, :] = self.cube[4, 0, :]
        self.cube[4, 0, :] = self.cube[3, 0, :]
        self.cube[3, 0, :] = self.cube[5, 0, :]
        self.cube[5, 0, :] = temp

    def rotate_down_clockwise(self):
        self.cube[1] = np.rot90(self.cube[1], k=-1)
        temp = self.cube[2, 2, :].copy()
        self.cube[2, 2, :] = self.cube[5, 2, :]
        self.cube[5, 2, :] = self.cube[3, 2, :]
        self.cube[3, 2, :] = self.cube[4, 2, :]
        self.cube[4, 2, :] = temp

    def rotate_left_clockwise(self):
        self.cube[5] = np.rot90(self.cube[5], k=-1)
        temp = self.cube[0, :, 0].copy()
        self.cube[0, :, 0] = self.cube[3, :, 2][::-1]
        self.cube[3, :, 2] = self.cube[1, :, 0][::-1]
        self.cube[1, :, 0] = self.cube[2, :, 0]
        self.cube[2, :, 0] = temp

    def rotate_right_clockwise(self):
        self.cube[4] = np.rot90(self.cube[4], k=-1)
        temp = self.cube[0, :, 2].copy()
        self.cube[0, :, 2] = self.cube[2, :, 2]
        self.cube[2, :, 2] = self.cube[1, :, 2]
        self.cube[1, :, 2] = self.cube[3, :, 0][::-1]
        self.cube[3, :, 0] = temp[::-1]

    def is_solved(self):
        for i in range(6):
            if len(np.unique(self.cube[i])) > 1: return False
        return True

    def scramble(self, moves_count=5):
        print(f"--- Scrambling Cube ({moves_count} moves) ---")
        moves = [self.rotate_front_clockwise, self.rotate_back_clockwise, 
                 self.rotate_up_clockwise, self.rotate_down_clockwise, 
                 self.rotate_left_clockwise, self.rotate_right_clockwise]
        for _ in range(moves_count):
            random.choice(moves)()

    def get_state_id(self):
        return self.cube.tobytes()

    def display_colored(self):
        COLORS = {
            0: Fore.WHITE + "██", 1: Fore.YELLOW + "██",
            2: Fore.GREEN + "██", 3: Fore.BLUE + "██",
            4: Fore.RED + "██",   5: Fore.MAGENTA + "██"
        }
        def r(f, row): return " ".join([COLORS[v] for v in self.cube[f][row]])
        
        print("\n      " + r(0, 0) + "\n      " + r(0, 1) + "\n      " + r(0, 2))
        for i in range(3):
            print(r(5, i) + "  " + r(2, i) + "  " + r(4, i) + "  " + r(3, i))
        print("      " + r(1, 0) + "\n      " + r(1, 1) + "\n      " + r(1, 2) + Style.RESET_ALL + "\n")

    # --- AGGRESSIVE HEURISTIC ---
    def calculate_heuristic(self):
        opposites = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4}
        total_distance = 0
        for f in range(6):
            for r in range(3):
                for c in range(3):
                    val = self.cube[f][r][c]
                    if val == f: continue
                    elif val == opposites[f]: total_distance += 2
                    else: total_distance += 1
        
        # FIX: Divide by 8 (Aggressive) instead of 12 (Safe)
        return total_distance / 8

    def solve_astar(self, max_depth=12):
        print(f"--- AI Thinking (Max Depth: {max_depth}) ---")
        queue = []
        initial_h = self.calculate_heuristic()
        unique_id = 0 
        heapq.heappush(queue, (initial_h, 0, self.get_state_id(), unique_id, self, []))
        
        visited = {self.get_state_id()}
        nodes_explored = 0
        
        while queue:
            # Pop best node
            _, g, _, _, current_cube, path = heapq.heappop(queue)
            
            if current_cube.is_solved():
                print(f"\nSolution Found! Checked {nodes_explored} states.")
                return path
            
            if len(path) >= max_depth: continue
            
            nodes_explored += 1
            if nodes_explored % 1000 == 0:
                print(f"Thinking... ({nodes_explored} states checked)", end='\r')

            moves = [
                ('F', current_cube.rotate_front_clockwise), ('B', current_cube.rotate_back_clockwise),
                ('U', current_cube.rotate_up_clockwise), ('D', current_cube.rotate_down_clockwise),
                ('L', current_cube.rotate_left_clockwise), ('R', current_cube.rotate_right_clockwise)
            ]
            
            for name, func in moves:
                new_cube = copy.deepcopy(current_cube)
                if name=='F': new_cube.rotate_front_clockwise()
                elif name=='B': new_cube.rotate_back_clockwise()
                elif name=='U': new_cube.rotate_up_clockwise()
                elif name=='D': new_cube.rotate_down_clockwise()
                elif name=='L': new_cube.rotate_left_clockwise()
                elif name=='R': new_cube.rotate_right_clockwise()
                
                sid = new_cube.get_state_id()
                if sid not in visited:
                    visited.add(sid)
                    new_g = g + 1
                    new_h = new_cube.calculate_heuristic()
                    unique_id += 1
                    heapq.heappush(queue, (new_g + new_h, new_g, sid, unique_id, new_cube, path + [name]))
        
        print("\nNo solution found (Try increasing max_depth).")
        return None

if __name__ == "__main__":
    game = RubiksCube()
    
    # Scramble 5 moves
    print("1. Scrambling Cube with 5 random moves...")
    game.scramble(5)
    game.display_colored()

    print("2. Solving...")
    solution_path = game.solve_astar(max_depth=25) 
    
    if solution_path:
        print(f"Moves ({len(solution_path)}): {solution_path}")
        for m in solution_path:
            if m=='F': game.rotate_front_clockwise()
            elif m=='B': game.rotate_back_clockwise()
            elif m=='U': game.rotate_up_clockwise()
            elif m=='D': game.rotate_down_clockwise()
            elif m=='L': game.rotate_left_clockwise()
            elif m=='R': game.rotate_right_clockwise()
            print(f"Executed {m}")
            game.display_colored()