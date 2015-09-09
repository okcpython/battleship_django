from django.contrib import admin
from .models import *

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    pass


@admin.register(ShipLocation)
class ShipLocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    pass


@admin.register(Shot)
class ShotAdmin(admin.ModelAdmin):
    pass
