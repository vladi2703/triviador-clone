import os


class PlayerDatabase:

    def __init__(self, filename):
        self.filename = filename
        self.players: dict[int, int] = {}

        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                for line in f:
                    name, score = line.strip().split()  # TODO: fix format error
                    self.players[name] = int(score)

    def add_player(self, name) -> bool:
        """Add a player to the database. Return True if the player was added, False else."""
        if len(self.players) > 3 or self.players.get(name) is not None:
            print(f"Player {name} already exists or player limit reached")
            return False
        self.players[name] = 0
        self.save()
        return True

    def update_score(self, name, score):
        self.players[name] = score
        self.save()

    def add_points(self, name, points):
        self.players[name] += points
        self.save()

    def save(self):
        with open(self.filename, 'w') as f:
            for name, score in self.players.items():
                f.write(f"{name} {score}\n")

    def get_top_scores(self, n=10):
        return sorted(self.players.items(), key=lambda x: x[1], reverse=True)[:n]
