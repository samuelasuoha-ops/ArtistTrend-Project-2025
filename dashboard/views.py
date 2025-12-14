import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Max, Q
from django.utils.timezone import now
from .services import search_artist, get_artist_top_tracks
from .models import Artist, PopularityRecord


def get_trending_artists():
    
    # Returns up to 3 'trending' artists based on:
    # - latest popularity (50%)
    # - growth over last 7 days (30%)
    # - how many times they've been searched in this app (20%)
    
    one_week_ago = now() - timedelta(days=7)

    # Annotates artists with recent averages and latest popularity
    artists = Artist.objects.annotate(
        avg_popularity_7d=Avg(
            "popularity_records__popularity",
            filter=Q(popularity_records__recorded_at__gte=one_week_ago),
        ),
        latest_popularity=Max("popularity_records__popularity"),
    )

    trending_list = []

    for artist in artists:
        if artist.avg_popularity_7d is None or artist.latest_popularity is None:
            continue

        # Combines the trending score
        latest = artist.latest_popularity
        avg_7d = artist.avg_popularity_7d
        growth = latest - avg_7d  # positive = rising

        score = (
            latest * 0.5 +
            growth * 0.3 +
            artist.search_count * 0.2
        )

        trending_list.append({"artist": artist, "score": score})

    trending_list.sort(key=lambda x: x["score"], reverse=True)

    return [item["artist"] for item in trending_list[:3]]

def home(request):
    context = {}
    query = request.GET.get("artist")

    if query:
        try:
            # Gets results from Spotify
            results = search_artist(query)
            context["artists"] = results
            context["search_query"] = query

            # Saves or updates artists and stores popularity snapshots
            for artist_data in results:
                artist_obj, created = Artist.objects.update_or_create(
                    spotify_id=artist_data["spotify_id"],
                    defaults={
                        "name": artist_data["name"],
                        "genres": artist_data["genres"],
                        "followers": artist_data["followers"],
                         "image_url": artist_data["image"],
                    },
                )

                # Counts searches for trending
                artist_obj.search_count += 1
                artist_obj.save()

                # Creates popularity records
                PopularityRecord.objects.create(
                    artist=artist_obj,
                    popularity=artist_data["popularity"],
                )

        except Exception as error:
            context["error"] = str(error)

    # To always compute trending artists from DB
    context["trending_artists"] = get_trending_artists()

    return render(request, "dashboard/home.html", context)


def artist_detail(request, spotify_id):
    
    # Shows one artist and a chart of their popularity over time.
    
    artist = get_object_or_404(Artist, spotify_id=spotify_id)
    records = artist.popularity_records.order_by("recorded_at")

    labels = [r.recorded_at.strftime("%Y-%m-%d %H:%M") for r in records]
    data = [r.popularity for r in records]

    # Data for last 7 days sparkline
    seven_days_ago = now() - timedelta(days=7)
    recent_records = [r for r in records if r.recorded_at >= seven_days_ago]
    spark_labels = [r.recorded_at.strftime("%d %b") for r in recent_records]
    spark_data = [r.popularity for r in recent_records]

    # The top tracks from Spotify
    top_tracks = []
    try:
        top_tracks = get_artist_top_tracks(spotify_id)
    except Exception:
        top_tracks = []

    context = {
        "artist": artist,
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "spark_labels": json.dumps(spark_labels),
        "spark_data": json.dumps(spark_data),
        "top_tracks": top_tracks,
    }
    return render(request, "dashboard/artist_detail.html", context)
 

def compare_artists(request):
    
    # Compare two artists: show image, latest popularity (if any), followers and genres, plus a simple bar chart.
    
    artist1_query = request.GET.get("artist1")
    artist2_query = request.GET.get("artist2")

    artist1 = None
    artist2 = None
    error = None

    # Defaults for bar chart data
    bar_labels = []
    bar_data1 = []
    bar_data2 = []

    try:
        # Artist 1
        if artist1_query:
            results1 = search_artist(artist1_query)
            if results1:
                a1 = results1[0]
                artist1, _ = Artist.objects.get_or_create(
                    spotify_id=a1["spotify_id"],
                    defaults={
                        "name": a1["name"],
                        "genres": a1["genres"],
                        "followers": a1["followers"],
                        "image_url": a1["image"],
                    },
                )

        # Artist 2
        if artist2_query:
            results2 = search_artist(artist2_query)
            if results2:
                a2 = results2[0]
                artist2, _ = Artist.objects.get_or_create(
                    spotify_id=a2["spotify_id"],
                    defaults={
                        "name": a2["name"],
                        "genres": a2["genres"],
                        "followers": a2["followers"],
                        "image_url": a2["image"],
                    },
                )

        # Builds bar-chart data ONLY if we have both artists
        if artist1 and artist2:
            # Gets the latest popularity record for each, if any
            last1 = artist1.popularity_records.order_by("-recorded_at").first()
            last2 = artist2.popularity_records.order_by("-recorded_at").first()

            pop1 = last1.popularity if last1 else 0
            pop2 = last2.popularity if last2 else 0

            followers1 = artist1.followers or 0
            followers2 = artist2.followers or 0

            # Scales the followers to millions so values are comparable on the chart
            followers1_m = followers1 / 1_000_000 if followers1 else 0
            followers2_m = followers2 / 1_000_000 if followers2 else 0

            bar_labels = ["Popularity", "Followers (M)"]
            bar_data1 = [pop1, followers1_m]
            bar_data2 = [pop2, followers2_m]

    except Exception as e:
        error = str(e)

    context = {
        "artist1_query": artist1_query,
        "artist2_query": artist2_query,
        "artist1": artist1,
        "artist2": artist2,
        "error": error,
        #  the bar chart data. This is always defined and may be empty arrays.
        "bar_labels": json.dumps(bar_labels),
        "bar_data1": json.dumps(bar_data1),
        "bar_data2": json.dumps(bar_data2),
    }
    return render(request, "dashboard/compare.html", context)

def about(request):
    
    # A simple About page describing the project.
    return render(request, "dashboard/about.html")
