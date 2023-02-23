from copy import deepcopy
import heapq
# definition of the problem
class NPuzzleState:

    def __init__(self, board, move_history=[]):
        # board(list[list[int]]) - the state of the board
        # move_history(list[list[list[int]]]) - the history of the moves up until this state
        self.board = deepcopy(board)
        (self.blank_row, self.blank_col) = self.find_blank()

        # create an empty array and append move_history
        self.move_history = [] + move_history + [self.board]

    def children(self):
        # returns the possible moves
        functions = [self.up, self.down, self.left, self.right]

        children = []
        for func in functions:
            child = func()
            if child:
                children.append(child)

        return children

    def find_blank(self):
        # finds the blank row and col
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == 0:
                    return (row, col)

    def move(func):
        # decorator function to add to history everytime a move is made
        # functions with @move will apply this decorator
        def wrapper(self):
            state = NPuzzleState(self.board, self.move_history)
            value = func(state)
            if value:
                return state
            else:
                return None

        return wrapper

    @move
    def up(self):
        # moves the blank upwards
        if self.blank_row == 0:
            return False
        else:
            self.board[self.blank_row][self.blank_col] = self.board[self.blank_row - 1][self.blank_col]
            self.board[self.blank_row - 1][self.blank_col] = 0
            self.blank_row -= 1
            return True

    @move
    def down(self):
        # moves the blank downwards
        if self.blank_row == len(self.board) - 1:
            return False
        else:
            self.board[self.blank_row][self.blank_col] = self.board[self.blank_row + 1][self.blank_col]
            self.board[self.blank_row + 1][self.blank_col] = 0
            self.blank_row += 1
            return True

    @move
    def left(self):
        # moves the blank left
        if self.blank_col == 0:
            return False
        else:
            self.board[self.blank_row][self.blank_col] = self.board[self.blank_row][self.blank_col - 1]
            self.board[self.blank_row][self.blank_col - 1] = 0
            self.blank_col -= 1
            return True

    @move
    def right(self):
        # moves the blank right
        if self.blank_col == len(self.board[0]) - 1:
            return False
        else:
            self.board[self.blank_row][self.blank_col] = self.board[self.blank_row][self.blank_col + 1]
            self.board[self.blank_row][self.blank_col + 1] = 0
            self.blank_col += 1
            return True

    def is_complete(self):
        # checks if the board is complete
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] != row * len(self.board[0]) + col + 1 and self.board[row][col] != 0:
                    return False
        return True

    def __hash__(self):
        # to be able to use the state in a set
        return hash(str([item for sublist in self.board for item in sublist]))

    def __eq__(self, other):
        # compares the two matrices
        return [item for sublist in self.board for item in sublist] == [item for sublist in other.board for item in sublist]

def print_sequence(sequence):
    print("Steps:", len(sequence) - 1)
    # prints the sequence of states
    for state in sequence:
        for row in state:
            print(row)
        print()


def problems():
    return (
        NPuzzleState([[1, 2, 3], [5, 0, 6], [4, 7, 8]]),
        NPuzzleState([[1, 3, 6], [5, 2, 0], [4, 7, 8]]),
        NPuzzleState([[1, 6, 2], [5, 7, 3], [0, 4, 8]]),
        NPuzzleState([[5, 1, 3, 4], [2, 0, 7, 8], [
                     10, 6, 11, 12], [9, 13, 14, 15]]),
    )


def bfs(problem):
    # problem(NPuzzleState) - the initial state
    queue = [problem]
    visited = set()  # to not visit the same state twice
    while queue:
        solution = queue.pop(0)

        if solution in visited:
            continue

        visited.add(solution)

        if solution.is_complete():
            return solution.move_history

        next_list = solution.children()
        queue = queue + list(filter(lambda x: x not in visited, next_list))

    return None


# prints the sequence for the first problem using bfs
#print_sequence(bfs(problems()[2]))

# we'll be using a heap to store the states


def greedy_search(problem, heuristic):
    # problem (NPuzzleState) - the initial state
    # heuristic (function) - the heuristic function that takes a board (matrix), and returns an integer
    setattr(NPuzzleState, "__lt__", lambda self, other: heuristic(self) < heuristic(other))
    states = [problem]
    visited = set()  # to not visit the same state twice
    visited.add(problem)
    while states:
        solution = heapq.heappop(states)
        visited.add(solution)
        if solution.is_complete():
            return solution.move_history

        for state in solution.children():
            if state not in visited:
                heapq.heappush(states, state)

    return None


def _preferential_position(number, side):
    # calculates the preferred position of a piece given its number
    # number (int) - the number of the piece
    # side (int) - the size of the side of the board (only for square boards)
    if number == 0:
        # if it is the last piece, it is 0
        row = col = side - 1
    else:
        # otherwise it is sequential, starting at 1
        row = number // side
        col = number % side - 1
    return (row, col)


def h1(state):
    # heuristic function 1
    # returns the number of incorrect placed pieces in the matrix
    board = state.board
    side = len(board)  # the size of the side of the board (only for square boards)

    total = 0

    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] != row * side + col + 1 and board[row][col] != 0:
                total += 1

    return total


def h2(state):
    # heuristic function 2
    # returns the sum of manhattan distances from incorrect placed pieces to their correct places
    board = state.board
    side = len(board)  # the size of the side of the board (only for square boards)

    total = 0

    total = 0

    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] != row * side + col + 1 and board[row][col] != 0:
                pref_row, pref_col = _preferential_position(board[row][col], side)
                total += abs(row - pref_row) + abs(col - pref_col)

    return total


#print('h1')
#print_sequence(greedy_search(problems()[2], h1))

#print('h2')
#print_sequence(greedy_search(problems()[2], h2))

def a_star_search(problem, heuristic):
    # problem (NPuzzleState) - the initial state
    # heuristic (function) - the heuristic function that takes a board (matrix), and returns an integer

    # this is very similar to greedy, the difference is that it takes into account the cost of the path so far
    # the cost of the path so far is the length of the move history

    return greedy_search(problem, lambda state: heuristic(state) + len(state.move_history))


print('h1')
print_sequence(a_star_search(problems()[2], h1))

print('h2')
print_sequence(a_star_search(problems()[2], h2))