from time import sleep
from django.core.management.base import BaseCommand
from dashboard.models import Artist, PopularityRecord
from dashboard.services import get_artist_metrics


class Command(BaseCommand):
    help = "Refresh Spotify popularity & followers for all artists and create a daily snapshot."

    def handle(self, *args, **options):
        artists = Artist.objects.all()
        if not artists.exists():
            self.stdout.write(self.style.WARNING("No artists in database yet. Nothing to update."))
            return

        self.stdout.write(self.style.SUCCESS(f"Updating {artists.count()} artists..."))

        for artist in artists:
            try:
                metrics = get_artist_metrics(artist.spotify_id)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to update {artist.name} ({artist.spotify_id}): {e}")
                )
                continue

            # Updates artist fields
            artist.followers = metrics["followers"]
            artist.genres = metrics["genres"]
            artist.save()

            # Creates a new popularity snapshot
            PopularityRecord.objects.create(
                artist=artist,
                popularity=metrics["popularity"],
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated {artist.name}: popularity={metrics['popularity']}, followers={metrics['followers']}"
                )
            )

            sleep(0.2)

        self.stdout.write(self.style.SUCCESS("Done updating artist popularity."))
