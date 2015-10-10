from django.db import transaction
from battleship_viewer.models import Player, Game, Ship, ShipLocation


@transaction.atomic
def import_game_from_file(f):
    game = create_game(f)
    create_ships(game, f)
    create_moves(game, f)


#######################################################################
# Create Game
#######################################################################
def create_game(f):
    g = Game()

    g.player1, g.player2 = get_or_create_players(f)
    g.grid_width, g.grid_height = get_grid_size(f)
    g.winner = get_winner(f)
    g.observer_log = f.read()

    g.save()
    return g


def get_or_create_players(f):
    players_data = get_data_by_message_type(f, 'players')

    player1_name = players_data[0]
    player2_name = players_data[1]

    player1, created = Player.objects.get_or_create(name=player1_name)
    player2, created = Player.objects.get_or_create(name=player2_name)

    return player1, player2


def get_grid_size(f):
    grid_size_data = get_data_by_message_type(f, 'grid size')

    grid_size = grid_size_data[0].split()
    grid_width = int(grid_size[0])
    grid_height = int(grid_size[1])

    return grid_width, grid_height


def get_winner(f):
    winner_data = get_data_by_message_type(f, 'end game')

    if 'tie_game' in winner_data:
        return None

    winner_name = winner_data[0].rsplit(" ", 1)[0]
    return Player.objects.get(name=winner_name)


#######################################################################
# Create Ships
#######################################################################
def create_ships(game, f):
    ship_sizes = get_data_by_message_type(f, 'ship sizes')
    for ship_locations in get_multi_data_by_message_type(f, 'ship locations'):
        player = game.get_player_by_name(ship_locations[0])
        for index, ship_location in enumerate(ship_locations[1:]):
            ship_location = ship_location.split()
            x = int(ship_location[0])
            y = int(ship_location[1])
            horizontal = ship_location[2] == "H"
            new_ship = Ship.objects.create(game=game, player=player)

            size = int(ship_sizes[index])
            for size_index in range(size):
                new_ship.add_location(x, y)
                if horizontal:
                    x += 1
                else:
                    y += 1


#######################################################################
# Create Moves
#######################################################################
def create_moves(game, f):
    # Both players move at the same time so are considered one move
    shots_data = get_multi_data_by_message_type(f, 'shots')
    while True:
        try:
            first_shots = shots_data.next()
            second_shots = shots_data.next()
            move = game.get_next_move()

            first_shots_player = game.get_player_by_name(first_shots[0])
            for shot in first_shots[1:]:
                x, y = shot.split()
                move.add_shot(first_shots_player, x, y)

            second_shots_player = game.get_player_by_name(second_shots[0])
            for shot in second_shots[1:]:
                x, y = shot.split()
                move.add_shot(second_shots_player, x, y)
        except StopIteration:
            break


#######################################################################
# Helpers
#######################################################################
def get_multi_data_by_message_type(f, field):
    for line in f:
        if line.startswith('|' + field +'|'):
            yield line.split('|')[2:-2]


def get_data_by_message_type(f, field):
    return get_multi_data_by_message_type(f, field).next()
