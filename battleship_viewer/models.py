from django.db import models
from django.db.models import Max, Count


#######################################################################
class Player(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.name)


#######################################################################
class Game(models.Model):
    player1 = models.ForeignKey(Player, related_name="player1")
    player2 = models.ForeignKey(Player, related_name="player2")
    grid_width = models.IntegerField()
    grid_height = models.IntegerField()
    winner = models.ForeignKey(Player, null=True, related_name="winner")
    observer_log = models.TextField()

    def get_player_by_name(self, name):
        if self.player1.name == name:
            return self.player1
        elif self.player2.name == name:
            return self.player2
        else:
            raise NameError

    def get_next_move(self):
        highest_move = self.move_set.aggregate(Max('order'))['order__max']
        if not highest_move:
            highest_move = 0
        return Move.objects.create(game=self, order=highest_move+1)

    def num_ships_per_player(self):
        return self.ship_set.count() / 2

    def num_shots(self):
        return self.move_set.aggregate(Count('shot'))['shot__count']

    def get_player1_ship_locations(self):
        return ShipLocation.objects.filter(ship__game=self, ship__player=self.player1).values_list('x', 'y')

    def get_player2_ship_locations(self):
        return ShipLocation.objects.filter(ship__game=self, ship__player=self.player2).values_list('x', 'y')

    def __unicode__(self):
        return u'Game %s: %s vs %s' % (self.id, self.player1, self.player2)


#######################################################################
class Ship(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)

    def add_location(self, x, y):
        ShipLocation.objects.create(ship=self, x=x, y=y)

    def __unicode__(self):
        return u'Game %s Player %s Ship' % (self.game.id, self.player)


#######################################################################
class ShipLocation(models.Model):
    ship = models.ForeignKey(Ship)
    x = models.IntegerField()
    y = models.IntegerField()

    def __unicode__(self):
        return u'%s: %s, %s' % (self.ship, self.x, self.y)


#######################################################################
class Move(models.Model):
    game = models.ForeignKey(Game)
    order = models.IntegerField(db_index=True)

    def add_shot(self, player, x, y):
        Shot.objects.create(move=self, player=player, x=x, y=y)

    def get_previous_move_order(self):
        try:
            return Move.objects.get(game=self.game, order=self.order-1).order
        except Move.DoesNotExist:
            return 0

    def get_next_move_order(self):
        try:
            return Move.objects.get(game=self.game, order=self.order+1).order
        except Move.DoesNotExist:
            return None

    def get_player1_shots_so_far(self):
        return Shot.objects.filter(move__game=self.game,
                                   move__order__lte=self.order,
                                   player=self.game.player1).values_list('x', 'y')

    def get_player2_shots_so_far(self):
        return Shot.objects.filter(move__game=self.game,
                                   move__order__lte=self.order,
                                   player=self.game.player2).values_list('x', 'y')

    def __unicode__(self):
        return u'Game %s Move %s' % (self.game, self.order)

    class Meta:
        ordering = ['order']


#######################################################################
class Shot(models.Model):
    move = models.ForeignKey(Move)
    player = models.ForeignKey(Player)
    x = models.IntegerField()
    y = models.IntegerField()

    def __unicode__(self):
        return u'%s Player %s Shot %s, %s' % (self.move, self.player, self.x, self.y)
