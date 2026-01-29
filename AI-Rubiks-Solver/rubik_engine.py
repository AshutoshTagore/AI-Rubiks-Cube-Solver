import numpy as np
import random
import copy
import heapq

class RubiksCube:
    def __init__(self):
        # 0:Up, 1:Down, 2:Front, 3:Back, 4:Right, 5:Left
        self.cube = np.zeros((6, 3, 3), dtype=int)
        for i in range(6):
            self.cube[i] = i 
        self.move_history = [] # History track 

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
        # Reset history on new scramble
        self.move_history = []
        moves_map = {
            'F': self.rotate_front_clockwise, 'B': self.rotate_back_clockwise,
            'U': self.rotate_up_clockwise, 'D': self.rotate_down_clockwise,
            'L': self.rotate_left_clockwise, 'R': self.rotate_right_clockwise
        }
        keys = list(moves_map.keys())
        
        scramble_log = []
        for _ in range(moves_count):
            k = random.choice(keys)
            moves_map[k]()
            scramble_log.append(k)
            self.move_history.append(k)
            
        return scramble_log

    def get_state_id(self):
        return self.cube.tobytes()

    # --- A* LOGIC ---
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
        return total_distance / 8

    def solve_astar(self, max_depth=12):
        queue = []
        initial_h = self.calculate_heuristic()
        unique_id = 0 
        heapq.heappush(queue, (initial_h, 0, self.get_state_id(), unique_id, self, []))
        visited = {self.get_state_id()}
        
        while queue:
            _, g, _, _, current_cube, path = heapq.heappop(queue)
            if current_cube.is_solved(): return path
            if len(path) >= max_depth: continue
            
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
                    unique_id += 1
                    heapq.heappush(queue, (g + 1 + new_cube.calculate_heuristic(), g + 1, sid, unique_id, new_cube, path + [name]))
        return None

    # --- INSTANT SOLVER (REVERSE LOGIC) ---
    def solve_fast_reverse(self):
        # Scramble history reverse
        # scramble : ['U', 'R'] -> Solution: ['R', 'R', 'R', 'U', 'U', 'U']
        # (3 times rotate = 1 times reverse rotate)
        
        solution = []
        # Reverse list: Last move first undo 
        for move in reversed(self.move_history):
            # each move add 3 times (Clockwise x 3 = Counter-Clockwise)
            solution.append(move)
            solution.append(move)
            solution.append(move)
            
        return solution