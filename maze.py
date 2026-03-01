import matplotlib.pyplot as plt
import random
from collections import defaultdict, deque

# ---------------- Game parameters ----------------
grid_size = 10
num_rooms = 5
player_pos = [0, 0]
treasure_pos = [[9, 9], [8, 1], [4, 8], [9,0], [0,9]]
trap_pos = [[4, 5], [2, 2], [7, 4], [5,5], [1,8]]

# ---------------- Example maps ----------------
example_maps = [
    [
        [0,0,1,1,0,0,0,1,0,0],
        [0,1,1,0,0,1,0,1,0,0],
        [0,0,0,0,1,1,0,0,0,1],
        [0,1,0,0,0,0,1,0,1,0],
        [0,0,1,1,0,0,0,1,0,0],
        [0,1,0,0,1,1,0,0,0,1],
        [0,0,0,1,0,0,1,0,0,0],
        [1,0,0,0,1,0,0,1,0,0],
        [0,0,1,0,0,0,1,0,1,0],
        [0,1,0,0,1,0,0,0,0,1],
    ],
    [
        [0,1,0,0,1,0,0,1,1,0],
        [0,0,0,1,1,0,0,0,1,0],
        [1,0,0,0,0,1,0,0,0,0],
        [0,0,1,0,1,0,1,0,0,0],
        [0,1,0,0,0,1,0,0,1,0],
        [0,0,1,1,0,0,1,0,0,0],
        [1,0,0,0,1,0,0,1,0,0],
        [0,1,0,0,0,0,1,0,0,1],
        [0,0,1,0,0,1,0,0,0,0],
        [1,0,0,1,0,0,0,1,0,0],
    ]
]

# ---------------- Markov chain functions ----------------
def build_markov_chain(sequences):
    chain = defaultdict(lambda: defaultdict(int))
    for seq in sequences:
        for i in range(len(seq)-1):
            prev = seq[i]
            nxt = seq[i+1]
            chain[prev][nxt] += 1
    # Normalize probabilities
    for prev, next_dict in chain.items():
        total = sum(next_dict.values())
        for nxt in next_dict:
            next_dict[nxt] /= total
    return chain

def generate_sequence(chain, length):
    seq = [0]
    for _ in range(length-1):
        prev = seq[-1]
        nxt_probs = chain[prev]
        choices, probs = zip(*nxt_probs.items())
        seq.append(random.choices(choices, probs)[0])
    return seq

def extract_rows_and_cols(maps):
    rows, cols = [], []
    for m in maps:
        rows.extend(m)
        # extract columns
        for c in range(len(m[0])):
            cols.append([m[r][c] for r in range(len(m))])
    return rows, cols

# ---------------- BFS solvability ----------------
def is_solvable(walls, start, goal):
    visited = [[False]*grid_size for _ in range(grid_size)]
    q = deque([start])
    visited[start[1]][start[0]] = True
    while q:
        x, y = q.popleft()
        if [x, y] == goal:
            return True
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<grid_size and 0<=ny<grid_size:
                if not visited[ny][nx] and walls[ny][nx]==0:
                    visited[ny][nx]=True
                    q.append([nx, ny])
    return False

# ---------------- Generate room ----------------
def generate_room(rows_chain, cols_chain, player_pos, treasure, trap):
    while True:
        # Generate by row
        room_rows = [generate_sequence(rows_chain, grid_size) for _ in range(grid_size)]
        # Generate by column
        room_cols = [generate_sequence(cols_chain, grid_size) for _ in range(grid_size)]
        # Merge (OR) row and column patterns
        room = [[max(room_rows[y][x], room_cols[x][y]) for x in range(grid_size)] for y in range(grid_size)]
        # Ensure important positions are empty
        sx, sy = player_pos
        tx, ty = treasure
        trapx, trapy = trap
        room[sy][sx] = 0
        room[ty][tx] = 0
        room[trapy][trapx] = 0
        # Check solvability
        if is_solvable(room, player_pos, treasure):
            return room

# ---------------- Build chains ----------------
rows_seq, cols_seq = extract_rows_and_cols(example_maps)
rows_chain = build_markov_chain(rows_seq)
cols_chain = build_markov_chain(cols_seq)

# ---------------- Generate all rooms ----------------
num_rooms = 5
walls_rooms = []
for r in range(num_rooms):
    walls_rooms.append(generate_room(rows_chain, cols_chain, player_pos, treasure_pos[r], trap_pos[r]))

# ---------------- Plotting ----------------
fig, ax = plt.subplots(figsize=(5,5))

def draw_scene(current_room):
    ax.clear()
    ax.set_xlim(-0.5, grid_size-0.5)
    ax.set_ylim(-0.5, grid_size-0.5)
    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_aspect('equal')
    ax.grid(True)
    room = walls_rooms[current_room]
    for y in range(grid_size):
        for x in range(grid_size):
            if room[y][x]==1:
                ax.add_patch(plt.Rectangle((x-0.5, y-0.5),1,1,color='gray'))
    ax.plot(player_pos[0], player_pos[1],'ro', markersize=20)
    ax.plot(treasure_pos[current_room][0], treasure_pos[current_room][1],'gs', markersize=20)
    ax.plot(trap_pos[current_room][0], trap_pos[current_room][1],'ks', markersize=20)
    ax.set_title(f'Room {current_room+1} - Arrow keys to move')
    fig.canvas.draw()

# ---------------- Movement ----------------
current_room = 0
def move_player(dx, dy):
    global player_pos, current_room
    new_x = max(0,min(grid_size-1, player_pos[0]+dx))
    new_y = max(0,min(grid_size-1, player_pos[1]+dy))
    if walls_rooms[current_room][new_y][new_x]==1:
        return
    player_pos[0]=new_x
    player_pos[1]=new_y
    # Treasure
    if player_pos==treasure_pos[current_room]:
        if current_room<num_rooms-1:
            print(f"Treasure found! Moving to Room {current_room+2}")
            current_room+=1
            player_pos[:] = [0,0]
        else:
            print("Final treasure found! You win!")
            current_room=0
            player_pos[:] = [0,0]
    # Trap
    elif player_pos==trap_pos[current_room]:
        print("Trap hit! Restarting room.")
        player_pos[:] = [0,0]
    draw_scene(current_room)

# ---------------- Key press ----------------
def on_key(event):
    if event.key=='up': move_player(0,1)
    elif event.key=='down': move_player(0,-1)
    elif event.key=='left': move_player(-1,0)
    elif event.key=='right': move_player(1,0)
    elif event.key=='escape': plt.close(fig)

fig.canvas.mpl_connect('key_press_event', on_key)
draw_scene(current_room)
plt.show()
#%%
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def plot_transition_matrix(chain, title):
    # Convert chain dict to 2x2 numpy array (rows: prev, columns: next)
    matrix = np.zeros((2,2))
    for prev in [0,1]:
        for nxt in [0,1]:
            if nxt in chain[prev]:
                matrix[prev][nxt] = chain[prev][nxt]
            else:
                matrix[prev][nxt] = 0.0
    sns.heatmap(matrix, annot=True, cmap='Blues', fmt=".2f", xticklabels=['0','1'], yticklabels=['0','1'])
    plt.xlabel('Next tile')
    plt.ylabel('Previous tile')
    plt.title(title)
    plt.show()

# Plot row transition matrix
plot_transition_matrix(rows_chain, "Row Markov Chain Transition Probabilities")
plt.figure()
# Plot column transition matrix
plot_transition_matrix(cols_chain, "Column Markov Chain Transition Probabilities")
#%%
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def room_probability_overlay(room, rows_chain, cols_chain):
    """
    Create a heatmap showing probability that each tile is a wall according to
    row and column Markov chains.
    """
    prob_matrix = np.zeros((grid_size, grid_size))
    
    # Row probabilities
    for y in range(grid_size):
        for x in range(1, grid_size):
            prev = room[y][x-1]
            prob_matrix[y][x] = rows_chain[prev].get(1, 0)  # probability next tile = wall
    
    # Column probabilities (merge with max)
    for x in range(grid_size):
        for y in range(1, grid_size):
            prev = room[y-1][x]
            prob_matrix[y][x] = max(prob_matrix[y][x], cols_chain[prev].get(1, 0))
    
    # First row/column default
    prob_matrix[0,:] = 0
    prob_matrix[:,0] = 0
    
    # Plot heatmap
    plt.figure(figsize=(6,6))
    sns.heatmap(prob_matrix, annot=room, fmt='d', cmap='Reds', cbar=True)
    plt.title("Generated Room with Wall Probabilities Overlayed")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()

# Example usage:
# Take the first generated room
room_probability_overlay(walls_rooms[0], rows_chain, cols_chain)