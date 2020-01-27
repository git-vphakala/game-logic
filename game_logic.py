"""
findpairs/game_logic.py
init()
play()
"""
import json
from random import shuffle
import time
from models import MATCH_COL_NUMPLAYER
from models import Match

def init(game, start_time):
    """
    game: models.Game
    """
    pair_list = []
    card_ids = ["a", "b"]
    scores = [0] * game.numPlayers
    players = []
    board = []
    cards = []

    for pair in range(1, game.numPairs+1):
        pair_list.append(str(pair))

    for pair_name in pair_list:
        for card_id in card_ids:
            board.append(pair_name + card_id)
            cards.append({"facedown": True, "removed": False, "faceValue": pair_name})

    board_cards = list(zip(board, cards))
    shuffle(board_cards)
    board, cards = zip(*board_cards)
    for i, card in enumerate(cards):
        card["position"] = i

    match_list = list(Match.objects.filter(game_id=game.gameId).values_list())
    match_list.sort(key=sort_by_num_player)
    for match in match_list:
        # print("game_logic.init: type(match)=" + str(type(match)) + ", match=" + str(match))
        players.append(match[2]) # 2 == user

    game.state = json.dumps({
        "gameId": str(game.gameId),
        "board": board,
        "cards": cards,
        "turn": 1,
        "faceUp":[],
        "removed":0,
        "scores":scores,
        "gameover": False,
        "players": players,
        "start-time": start_time, # int(time.time()),
        "game-max-len": 200, # fixme: game_len,
        "max-len-timer": 0, # fixme: TimerMgr, max_len_timer
        "faceup-delay": False,
        "in-device": False
    })

def sort_by_num_player(match):
    """
    Sort helper for match_list.sort to get the players-list as sorted according the numPlayer-field
    """
    return match[MATCH_COL_NUMPLAYER] # 3 == numPlayer

def play(game, message):
    """
    game: models.Game
    message: {gameId:<str>, userName:<str>, cardI:<int>}
    """
    try:
        game_state = json.loads(game.state)
    except json.JSONDecodeError:
        print("game_logic.play: JSONDecodeError, gameId=" + game.gameId +
              ", game.state=" + game.state)
        return

    try:
        player_inturn = list(Match.objects.filter(game_id=game.gameId,
                                                         user=message["userName"]).values_list())
    except Match.DoesNotExist:
        print("game_logic.play: Match.DoesNotExist, gameId=" + game.gameId +
              ", userName=" + message["userName"])
        return

    if player_inturn[0][3] != game_state["turn"]: # List contains one Match. Match[3] == numPlayer
        return

    card_i = message["cardI"]
    if card_i < 0 or card_i >= len(game_state["cards"]):
        print("game_logic.play: invalid cardI=" + card_i + ", gameId=" + game.gameId +
              ", userName=" + message["userName"])

    card = game_state["cards"][card_i]

    if len(game_state["faceUp"]) == 2 and card["facedown"]:
        game_state["faceUp"].clear()

    if len(game_state["faceUp"]) < 2 and card["facedown"]:
        game_state["cards"][card_i]["facedown"] = card["facedown"] = False
        game_state["faceUp"].append(card)
        print("game_logic.play: turned, cardI=" + str(card_i))

    if len(game_state["faceUp"]) > 1:
        print("two cards are face-up")
        if game_state["faceUp"][0]["faceValue"] == game_state["faceUp"][1]["faceValue"]:
            print("pair found")
            for i, card in enumerate(game_state["faceUp"]):
                removed_card_i = game_state["faceUp"][i]["position"]
                game_state["cards"][removed_card_i]["removed"] = True
                game_state["faceUp"][i]["removed"] = True

            # game_state["faceUp"].clear()
            game_state["removed"] += 1
            scores_i = player_inturn[0][3] - 1 # Match[3] == numPlayer (1..Game.numPlayers)
            game_state["scores"][scores_i] += 1
            if game_state["removed"] == game.numPairs:
                game_state["gameover"] = True
            else:
                game_state["turn"] = change_turn(game_state["turn"], game_state["players"])
        else:
            print("Not a pair. Return cards back to the face-down state.")
            for i, card in enumerate(game_state["faceUp"]):
                returned_card_i = game_state["faceUp"][i]["position"]
                game_state["cards"][returned_card_i]["facedown"] = True
            # game_state["faceUp"].clear()
            game_state["turn"] = change_turn(game_state["turn"], game_state["players"])

    try:
        game.state = json.dumps(game_state)
    except TypeError:
        print("game_logic.play: game_state TypeError, gameId=" + game.gameId +
              ", userName=" + message["userName"])

def change_turn(turn, players):
    """
    Set turn for the next player in the list.
    """
    turn -= 1 # game_state.turn = 1..numPlayers, here turn = 0..numPlayers-1
    new_turn = turn

    # for (i = 0; i < this.players.length; i++) {
    #   newTurn = ((turn + 1 + i) % this.players.length);
    #   if (this.removedPlayers[this.players[newTurn]]) continue; // skip a removed player
    #   else break;
    new_turn = ((turn + 1) % len(players))
    return new_turn + 1
