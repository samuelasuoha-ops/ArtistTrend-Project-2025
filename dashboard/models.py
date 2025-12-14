from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    spotify_id = models.CharField(max_length=200, unique=True)
    genres = models.TextField(blank=True, null=True)
    followers = models.IntegerField(default=0)
    search_count = models.IntegerField(default=0)

    # store artist image from Spotify
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class PopularityRecord(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="popularity_records"
    )
    popularity = models.IntegerField()  # 0–100 from Spotify
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artist.name} - {self.popularity} at {self.recorded_at}"
