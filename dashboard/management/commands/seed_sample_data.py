from django.core.management.base import BaseCommand
from dashboard.services import search_artist
from dashboard.models import Artist, PopularityRecord


POPULAR_ARTISTS = [
    "Drake",
    "Taylor Swift",
    "The Weeknd",
    "Ariana Grande",
    "Ed Sheeran",
    "Burna Boy",
    "Wizkid",
]


class Command(BaseCommand):
    help = "Seed the database with sample popular artists from Spotify"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding sample artists..."))

        for name in POPULAR_ARTISTS:
            results = search_artist(name)
            if not results:
                self.stdout.write(self.style.WARNING(f"No results for {name}"))
                continue

            data = results[0]  # first match

            artist_obj, created = Artist.objects.update_or_create(
                spotify_id=data["spotify_id"],
                defaults={
                    "name": data["name"],
                    "genres": data["genres"],
                    "followers": data["followers"],
                    "image_url": data["image"],
                },
            )

            # Mark as searched a few times to boost trending score
            artist_obj.search_count += 3
            artist_obj.save()

            PopularityRecord.objects.create(
                artist=artist_obj,
                popularity=data["popularity"],
            )

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {artist_obj.name}"))

        self.stdout.write(self.style.SUCCESS("Done seeding sample data."))
