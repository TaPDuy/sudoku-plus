import os
import json


from sudoku.timer import Time


class Highscore:
    __PATH = "highscore.json"
    highscores = {}

    @staticmethod
    def load():
        if os.path.exists(Highscore.__PATH):
            with open(Highscore.__PATH, "r") as file:
                Highscore.highscores = json.load(file)

    @staticmethod
    def save():
        if not os.path.exists(Highscore.__PATH):
            open(Highscore.__PATH, 'a').close()

        with open(Highscore.__PATH, "w") as file:
            json.dump(Highscore.highscores, file)

    @staticmethod
    def update(level_id: str, time: Time):
        if Highscore.highscores.get(level_id):
            if time < Highscore.highscores[level_id]:
                Highscore.highscores[level_id] = time.ticks
        else:
            Highscore.highscores[level_id] = time.ticks

    @staticmethod
    def get(level_id: str) -> Time:
        ticks = Highscore.highscores.get(level_id)
        return Time.to_time(ticks) if ticks else Time()
