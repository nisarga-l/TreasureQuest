
import random

class QLearningAgent:

    def __init__(self, maze):
        self.maze = maze
        self.q_table = {}
        self.alpha = 0.2
        self.gamma = 0.9
        self.epsilon = 0.2

        self.actions = [
            (0, -1),  # Up
            (0, 1),   # Down
            (-1, 0),  # Left
            (1, 0)    # Right
        ]

        self.start = (1, 1)
        self.relic = None
        self.goal = None

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == "R":
                    self.relic = (x, y)
                elif cell == "G":
                    self.goal = (x, y)

    def get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * 4
        return self.q_table[state]

    def choose_action(self, state, explore=True):
        values = self.get_q(state)

        if explore and random.random() < self.epsilon:
            return random.randrange(4)

        best = max(values)
        choices = [
            i for i, value in enumerate(values)
            if value == best
        ]
        return random.choice(choices)

    def transition(self, state, action):
        x, y, has_relic = state
        dx, dy = self.actions[action]
        nx, ny = x + dx, y + dy

        if not (0 <= ny < len(self.maze)
                and 0 <= nx < len(self.maze[0])):
            return state, -10, False

        if self.maze[ny][nx] == "#":
            return state, -10, False

        position = (nx, ny)

        if position == self.relic and not has_relic:
            has_relic = True
            reward = 50
        elif self.maze[ny][nx] == "T":
            return (self.start[0], self.start[1], has_relic), -25, False
        elif position == self.goal and has_relic:
            return (nx, ny, has_relic), 100, True
        else:
            reward = -1

        return (nx, ny, has_relic), reward, False

    def train(self, episodes=3000):
        for episode in range(episodes):
            state = (1, 1, False)

            for step in range(300):
                action = self.choose_action(state)
                next_state, reward, done = self.transition(
                    state, action
                )

                current_q = self.get_q(state)[action]
                next_best = (
                    0 if done else max(self.get_q(next_state))
                )

                updated_q = current_q + self.alpha * (
                    reward + self.gamma * next_best - current_q
                )

                self.get_q(state)[action] = updated_q
                state = next_state

                if done:
                    break

        return len(self.q_table)

    def next_move(self, position, has_relic):
        state = (
            position[0],
            position[1],
            has_relic
        )

        action = self.choose_action(state, explore=False)
        return self.actions[action]
