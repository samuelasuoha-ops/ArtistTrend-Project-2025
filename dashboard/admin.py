from django.contrib import admin
from .models import Artist, PopularityRecord


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "spotify_id", "followers", "genres")
    search_fields = ("name", "spotify_id", "genres")


@admin.register(PopularityRecord)
class PopularityRecordAdmin(admin.ModelAdmin):
    list_display = ("artist", "popularity", "recorded_at")
    list_filter = ("artist", "recorded_at")