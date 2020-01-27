import json
import time
from models import Game
from models import Match
from game_logic import init, play

class GameLogicTestLibrary(object):
    """Test library for testing game logic.
    """

    users = ['Veera', 'Helmi', 'Sanni']

    def __init__(self):
        self.game = None
        self.prev_game_state = ''

    def get_users(self):
        return GameLogicTestLibrary.users

    def init_database(self, numPlayers, numPairs, user):
        assert int(numPlayers) <= len(GameLogicTestLibrary.users), 'max numPlayers exceeded'
        assert user in GameLogicTestLibrary.users, 'must use a predefined user'

        self.game = Game(numPlayers=int(numPlayers), numPairs=int(numPairs), creator=user)
        Match.remove_all()
        for i in range(int(numPlayers)):
            Match.save((i, self.game.gameId, GameLogicTestLibrary.users[i], i+1))

    def print_match(self):
        print('Match.objects.values=', Match.objects.values)
        print('Match, filtered by game_id=', self.game.gameId, ':', Match.objects.filter(game_id=self.game.gameId).values_list())
        print('Match, filtered by game_id=', self.game.gameId, 'and user=', self.game.creator, ':',\
            list(Match.objects.filter(game_id=self.game.gameId, user=self.game.creator).values_list()))

    def check_game_initialization(self):
        init(self.game, int(time.time()))
        print('game.state=', self.game.state)
        game_state = json.loads(self.game.state)

        assert len(game_state['players']) == self.game.numPlayers, '*** #players invalid'
        assert len(game_state['board']) == (self.game.numPairs * 2), '*** board size invalid' 
        assert len(game_state['cards']) == (self.game.numPairs * 2), '*** #cards invalid'
        assert len(game_state['scores']) == self.game.numPlayers, '*** scores size invalid'

    def mock_board(self, board):
        game_state = json.loads(self.game.state)
        game_state['board'] = board.copy()
        for i, card in enumerate(board):
            game_state['cards'][i]['faceValue'] = card[:-1]
        self.game.state = json.dumps(game_state)
        print('game.state=', self.game.state)

    def get_player_in_turn(self):
        turn_as_user_i = json.loads(self.game.state)['turn'] - 1
        return GameLogicTestLibrary.users[turn_as_user_i]

    def turn_card(self, user, cardI):
        print('user', user, 'cardI', cardI)

        message = {'gameId':self.game.gameId, 'userName':user, 'cardI':int(cardI)}
        self.prev_game_state = self.game.state
        play(self.game, message)

        print('game.state=', self.game.state)

    def faceup_cards_should_be(self, cards):
        print(cards)

        faceUp = json.loads(self.game.state)['faceUp']
        assert len(cards) == len(faceUp), 'faceup len invalid'
        for card in cards:
            card_found = False
            for up in faceUp:
                if up['position'] == card['position'] and up['faceValue'] == card['faceValue']:
                    card_found = True
                    break
            assert card_found, 'faceup_cards do not match'

    def check_if_should_clear_faceups(self, faceups):
        if len(faceups) >= 2:
            print("clear faceups")
            return []
        else:
            return faceups

    def score_should_be(self, scores):
        print('scores', scores)
        print('game.state=', self.game.state)

        game_state_scores = json.loads(self.game.state)['scores']
        for i, score in enumerate(scores):
            assert int(score) == game_state_scores[i], 'scores invalid'
