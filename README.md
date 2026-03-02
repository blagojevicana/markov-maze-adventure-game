# markov-maze-adventure-game

### 1. Introduction

The approach detailed here was used in the game SCANLINE, a tilemap-based level 2D game.

This project demonstrates a simple adventure game where you want to collect rewards and avoid traps. For this kind of game, multiple different mazes are needed. They can be designed by hand, but that is time consuming. An alternative is to randomly generate them, which doesn't seem like a good solution since we want mazes to make sense. The better solution is to design a few mazes by hand, and generate the rest using **Markov's chains**. Also, valide each generated maze with **Breadth-first-search** algorithm, so every maze is solvable.

![Media1](figures/Media1.gif)

The result is that we end up with interesting variations of maps — changing the feel of the generated map doesn't require any changes to code, only to that of the input.
The maps strike a good balance between randomly generated and handcrafted. That is they feel both organic and structured but, due to randomness, each is different enough to the other to provide something unique.

### 2. Markov chains

First, we will design a couple of maps to be the "training data" for the Markov chains. Each row is a sequence of 0s and 1s, representing empty spaces and walls. By providing a few examples, the Markov chain can learn local patterns, like how often walls follow other walls or empty spaces.

Mathematically, the Markov chain assumes the probability of the next cell depends only on the current cell (first-order Markov property). We are using the simplest form: P(next_tile | current_tile). We get these probabilities by just counting how often empty cell follows a wall, vertically and horizontally.

We can look at the probabilities for every state:

![Figure_1](figures/Figure_1.png)
![Figure_2](figures/Figure_2.png)

Markov chain will look at these learned probabilities, and based on them generate new maps.

### 3. Breadth-first-search

To make sure a generated maze is solvable, we will use BFS. BFS is an algorithm that will give us the shortest possible path to the target.
BFS explores all reachable empty tiles from the start, and keeps track of which cells we have already checked, and which need to be checked next, in a queue.
If we reach the goal, the maze is solvable. Otherwise, we return False.

<img src="figures/bfs.gif" width="300" alt="bfs"/>

Mathematically, BFS is a graph traversal algorithm. Each cell is a node, each empty neighbor is an edge, and BFS ensures that if a path exists from start to goal, it will find it.

### 4. Draw the maze

Each wall is drawn as a gray rectangle.
Player is a red circle, treasure a green square, trap a black square.
The grid coordinates are adjusted to center the rectangles in each cell.

### 5. Player movement

Player uses arrows on the keyboard to control the game. With that, we calculate the new position.
If it’s a wall, movement is blocked.
If the player reaches a treasure, the room advances (or game resets).
If the player hits a trap, the room restarts.
