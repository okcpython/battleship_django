from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView, ListView, DetailView
from battleship_viewer.forms import ImportObserverLogForm
from battleship_viewer.models import Game, Move
from battleship_viewer.observer_import_utils import import_game_from_file


#######################################################################
class HomeView(TemplateView):
    template_name = "battleship_viewer/home.html"


#######################################################################
class ImportObserverLogView(FormView):
    template_name = 'battleship_viewer/import_observer_log.html'
    form_class = ImportObserverLogForm
    success_url = '/battleship_viewer/game/'

    def form_valid(self, form):
        import_game_from_file(form.cleaned_data['observer_log'])
        return super(ImportObserverLogView, self).form_valid(form)


#######################################################################
class GameView(ListView):
    model = Game


#######################################################################
class GameDetailView(DetailView):
    model = Game


#######################################################################
class MoveView(ListView):
    model = Move

    def get_queryset(self):
        self.game = get_object_or_404(Game, pk=self.args[0])
        return Move.objects.filter(game=self.game)

    def get_context_data(self, **kwargs):
        context = super(MoveView, self).get_context_data(**kwargs)
        context['game'] = self.game
        return context


#######################################################################
class MoveDetailView(DetailView):
    model = Move

    def get_object(self, queryset=None):
        self.order = int(self.kwargs['move'])
        if self.order == 0:
            self.first_run = True
            return Move.objects.get(game=self.kwargs['game'], order=1)
        else:
            self.first_run = False
            return Move.objects.get(game=self.kwargs['game'], order=self.order)

    def get_context_data(self, **kwargs):
        context = super(MoveDetailView, self).get_context_data(**kwargs)
        self.move = self.get_object()
        self.game = self.move.game
        context['game'] = self.get_object().game
        context['grid_width_range'] = range(self.game.grid_width)
        context['grid_height_range'] = range(self.game.grid_height)
        context['player1_ship_locations'] = self.game.get_player1_ship_locations()
        context['player2_ship_locations'] = self.game.get_player2_ship_locations()
        if self.first_run:
            context['player1_shots'] = []
            context['player2_shots'] = []
            context['previous_move'] = None
            context['next_move'] = 1
        else:
            context['player1_shots'] = self.move.get_player1_shots_so_far()
            context['player2_shots'] = self.move.get_player2_shots_so_far()
            context['previous_move'] = self.move.get_previous_move_order()
            context['next_move'] = self.move.get_next_move_order()
        return context
