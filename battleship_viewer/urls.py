from django.conf.urls import url
from battleship_viewer.views import HomeView, ImportObserverLogView, GameView, GameDetailView, MoveView, MoveDetailView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^import_observer_log/$', ImportObserverLogView.as_view(), name='import_observer_log'),
    url(r'^game/$', GameView.as_view(), name='list_games'),
    url(r'^game/(?P<pk>\d+)/$', GameDetailView.as_view(), name='game-detail'),
    url(r'^game/(\d+)/move/$', MoveView.as_view(), name='list_moves'),
    url(r'^game/(?P<game>\d+)/(?P<move>\d+)/$', MoveDetailView.as_view(), name='move-detail'),
]
