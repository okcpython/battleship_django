from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView, ListView, DetailView
from battleship_viewer.forms import ImportObserverLogForm
from battleship_viewer.models import Game, Move, ShipLocation, CellState, Shot
from battleship_viewer.observer_import_utils import import_game_from_file
import battleship_viewer.profiler
import time

########################################################################
class HomeView(TemplateView):
    template_name = "battleship_viewer/home.html"


########################################################################
class ImportObserverLogView(FormView):
    template_name = 'battleship_viewer/import_observer_log.html'
    form_class = ImportObserverLogForm
    success_url = '/battleship_viewer/game/'

    def form_valid(self, form):
        import_game_from_file(form.cleaned_data['observer_log'])
        return super(ImportObserverLogView, self).form_valid(form)


########################################################################
class GameView(ListView):
    model = Game


########################################################################
class GameDetailView(DetailView):
    model = Game


########################################################################
class MoveView(ListView):
    model = Move

    def get_queryset(self):
        self.game = get_object_or_404(Game, pk=self.args[0])
        return Move.objects.filter(game=self.game)

    def get_context_data(self, **kwargs):
        context = super(MoveView, self).get_context_data(**kwargs)
        context['game'] = self.game
        return context


########################################################################
class MoveDetailView(DetailView):
    model = Move

    ####################################################################
    def get_object(self, queryset=None):
        self.order = int(self.kwargs['move'])
        if self.order == 0:
            self.first_run = True
            return Move.objects.get(game=self.kwargs['game'], order=1)
        else:
            self.first_run = False
            return Move.objects.get(game=self.kwargs['game'], order=self.order)

    ####################################################################
    # @battleship_viewer.profiler.profile("move-detail")
    def get_context_data(self, **kwargs):
        context = super(MoveDetailView, self).get_context_data(**kwargs)
        move = self.get_object()
        game = move.game
        context['game'] = game
        context["player1_name"] = game.player1.name
        context["player2_name"] = game.player2.name
        if self.first_run:
            context["move_label"] = unicode(game)
            context['previous_move'] = None
            context['next_move'] = 1
            context["player1_grid"] = self.get_starting_grid(game, game.player1)
            context["player2_grid"] = self.get_starting_grid(game, game.player2)
            context["player1_shots"] = ""
            context["player2_shots"] = ""
        else:
            context["move_label"] = unicode(move)
            context['previous_move'] = move.get_previous_move_order()
            context['next_move'] = move.get_next_move_order()
            context["player1_grid"] = self.get_player_grid(move, game.player1)
            context["player2_grid"] = self.get_player_grid(move, game.player2)
            context["player1_shots"] = move.player1_text
            context["player2_shots"] = move.player2_text
        return context

    ####################################################################
    def get_starting_grid(self, game, player):
        grid = []
        ship_locations = {(sl.x, sl.y): sl for sl in ShipLocation.objects.player_locations(game, player)}
        for y in range(game.grid_height):
            row = []
            for x in range(game.grid_width):
                if (x, y) in ship_locations:
                    cell_state = ship_locations[(x, y)].get_position()
                else:
                    cell_state = CellState.EMPTY
                cell = {"x": x,
                        "y": y,
                        "cell_state": cell_state,
                        }
                row.append(cell)
            grid.append(row)
        return grid

    ####################################################################
    def get_player_grid(self, move, player):
        ship_locations = {(sl.x, sl.y): sl for sl in ShipLocation.objects.filter(ship__player=player, ship__game=move.game)}
        opponent = move.game.get_other_player(player)
        shots_this_move = Shot.objects.filter(move=move, player=opponent).values_list('x', 'y')
        shots_so_far = Shot.objects.filter(move__game=move.game, move__order__lte=move.order, player=opponent).values_list('x', 'y')

        grid = []
        for y in range(move.game.grid_height):
            row = []
            for x in range(move.game.grid_width):
                cell_state = self.get_cell_state(ship_locations, shots_this_move, shots_so_far, x, y)

                cell = {"x": x,
                        "y": y,
                        "cell_state": cell_state,
                        }
                row.append(cell)
            grid.append(row)
        return grid

    ####################################################################
    def get_cell_state(self, ship_locations, shots_this_move, shots_so_far, x, y):
        ship_location = ship_locations.get((x, y))

        if (x, y) in shots_this_move:
            if ship_location:
                return CellState.JUST_HIT
            else:
                return CellState.JUST_MISSED
        elif (x, y) in shots_so_far:
            if ship_location:
                return CellState.HIT
            else:
                return CellState.MISS
        else:
            if ship_location:
                return ship_location.get_position()
            else:
                return CellState.EMPTY
