from random import shuffle
from uuid import uuid4


class Game:
    games = {}

    @classmethod
    def create_room(cls, username, room):
        if not cls.games.get(room, False):
            g = cls(username, room)
            cls.games[room] = g
            return {**g.player_detail[1], "room": room}

    @classmethod
    def room_available(cls, room):
        return True if cls.games.get(room, False) else False

    @classmethod
    def room_full(cls, room):
        return True if cls.games[room].player_detail.get(2, False) else False

    @classmethod
    def join_room(cls, username, room):
        cls.games[room].player_detail[2] = {
            "username": username,
            "token": str(uuid4()),
            "symbol": cls.games[room].symbols[1],
            "score": 0
        }
        return {**cls.games[room].player_detail[2], "room": cls.games[room].room}

    @classmethod
    def match_credential(cls, room, token):
        return True if (cls.games[room].player_detail[1]["token"] == token or
                        cls.games[room].player_detail[2]["token"] == token) else False

    @classmethod
    def get_opponent(cls, room, token):
        if cls.games[room].player_detail[1]["token"] == token:
            return {"username": cls.games[room].player_detail[2]["username"],
                    "score": cls.games[room].player_detail[2]["score"],
                    "symbol": cls.games[room].player_detail[2]["symbol"]}
        elif cls.games[room].player_detail[2]["token"] == token:
            return {"username": cls.games[room].player_detail[1]["username"],
                    "score": cls.games[room].player_detail[1]["score"],
                    "symbol": cls.games[room].player_detail[1]["symbol"]}

    @classmethod
    def get_player(cls, room, token):
        if cls.games[room].player_detail[1]["token"] == token:
            return cls.games[room].player_detail[1]
        elif cls.games[room].player_detail[2]["token"] == token:
            return cls.games[room].player_detail[1]

    @classmethod
    def remove(cls, room):
        print(room)
        cls.games.pop(room)

    @classmethod
    def update_game(cls, room, pos, symbol):
        next_player = cls.games[room].update_board(symbol, pos)
        return {"room": room, "pos": pos, "symbol": symbol, "turn": next_player}

    @classmethod
    def over(cls, room):
        return cls.games[room].game_over

    @classmethod
    def game_winner(cls, room):
        return cls.games[room].get_winner()

    @classmethod
    def replay(cls, room):
        cls.games[room].reset()

    def __init__(self, username, room):
        self.turn = "O"
        self.room = room
        self.strike = []
        self.game_over = False
        self.symbols = ["X", "O"]
        self.winner = -1
        self.draw = False
        self.empty_pos = 9
        shuffle(self.symbols)
        self.board = [
            {
                "symbol": "-",
                "pos": pos,
            } for pos in range(1, 10)
        ]
        self.player_detail = {
            1: {
                "username": username,
                "token": str(uuid4()),
                "symbol": self.symbols[0],
                "score": 0
            }
        }

    def get_winner(self):
        return {"draw": self.draw, "winner": self.player_detail.get(self.winner, "")}

    def set_winner(self, symbol, pos):
        if self.symbols[0] == symbol:
            self.winner = 1
        else:
            self.winner = 2
        self.strike = pos
        self.player_detail[self.winner]["score"] += 1
        self.game_over = True

    def update_board(self, symbol, pos):
        self.board[pos - 1]["symbol"] = symbol
        self.turn = "X" if symbol == "O" else "O"
        self.empty_pos -= 1
        for i in range(3):
            st = self.board[i * 3 + 0]["symbol"] == self.board[i * 3 + 1]["symbol"] == self.board[i * 3 + 2]["symbol"]
            if st and self.board[i * 3 + 2]["symbol"] != "-":
                self.set_winner(self.board[i * 3 + 0]["symbol"], [i * 3 + 0, i * 3 + 1, i * 3 + 2])
                break
            st = self.board[i + 0]["symbol"] == self.board[i + 3]["symbol"] == self.board[i + 6]["symbol"]
            if st and self.board[i + 6]["symbol"] != "-":
                self.set_winner(self.board[i + 0]["symbol"], [i + 0, i + 3, i + 6])
                break

        st = self.board[0]["symbol"] == self.board[4]["symbol"] == self.board[8]["symbol"]
        if st and self.board[8]["symbol"] != "-":
            self.set_winner(self.board[0]["symbol"], [0, 4, 8])
        st = self.board[6]["symbol"] == self.board[4]["symbol"] == self.board[2]["symbol"]
        if st and self.board[2]["symbol"] != "-":
            self.set_winner(self.board[2]["symbol"], [2, 4, 6])

        if self.empty_pos == 0:
            self.game_over = True
            if self.winner == -1:
                self.draw = True

        return self.turn

    def reset(self):
        for pos in range(9):
            self.board[pos]["symbol"] = "-"
        self.game_over = False
        self.winner = -1
        self.empty_pos = 9
        self.strike = []
        self.draw = False
        shuffle(self.symbols)
        self.player_detail[1]["symbol"] = self.symbols[0]
        self.player_detail[2]["symbol"] = self.symbols[1]
