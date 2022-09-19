import os

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, join_room, close_room
from flask_cors import CORS
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = "xyz123"
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*",
                    # logger=True, engineio_logger=True, ping_timeout=5, ping_interval=10
                    )


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@socketio.on('player_detail')
def on_player_enter(data):
    if not Game.room_available(data["room"]):
        player = Game.create_room(data["user"], data["room"])
        emit("player_detail", player)
    elif not Game.room_full(data["room"]):
        player = Game.join_room(data["user"], data["room"])
        emit("player_detail", player)
        emit("opponent_detail", {"opponent": player}, broadcast=True, include_self=False, room=data["room"])
        emit("opponent_detail", {"opponent": Game.get_opponent(data["room"], player["token"])})
    else:
        emit('room_full', {"error": "Room Full"})
        return

    join_room(data["room"])


@socketio.on("move")
def on_move(data):
    update = Game.update_game(data["room"], data["pos"], data["symbol"])
    emit("move_update", update, broadcast=True, room=data["room"])
    if Game.over(data["room"]):
        winner = Game.game_winner(data["room"])
        emit("game_over", winner, broadcast=True, room=data["room"])


@socketio.on("play_again")
def play_again(data):
    emit("play_req", Game.get_opponent(data["room"], data["token"]), include_self=False, room=data["room"])


@socketio.on("accept_replay")
def accept(data):
    emit("accepted", Game.get_opponent(data["room"], data["token"]), include_self=False, room=data["room"])
    Game.replay(data["room"])


@socketio.on('continue_old_session')
def on_continue(data):
    if Game.room_available(data["room"]) and Game.match_credential(data["room"], data["token"]):
        join_room(data["room"])
        emit('opponent_detail', {"opponent": Game.get_opponent(data["room"], data["token"]),
                                 "board": {"data": Game.games[data["room"]].board,
                                           "turn": Game.games[data["room"]].turn}})
        if Game.over(data["room"]):
            winner = Game.game_winner(data["room"])
            emit("game_over", winner, broadcast=True, room=data["room"])

    elif not Game.room_available(data["room"]):
        emit('expired', {"error": "Room does not exist!!"})
    else:
        emit('expired', {"error": "Token invalid or expired!!"})


@socketio.on("disconnect_socket")
def on_disconnect(data):
    player = data
    opponent = Game.get_opponent(data["room"], data["token"])
    emit("player_left", {"player": opponent, "opponent": player},
         broadcast=True, room=data["room"], include_self=False)
    Game.remove(data["room"])
    close_room(data["room"])


if __name__ == "__main__":
    socketio.run(app, debug=True)
