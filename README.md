# ArtistTrend – Artist Popularity Trends Dashboard

ArtistTrend is a Django web application that uses the Spotify Web API to analyse and visualise the popularity of music artists.

## Features

- Search for artists and view their current popularity, followers, and genres
- Store artist data and popularity history in a database
- View an artist detail page with a Chart.js popularity-over-time graph
- Compare two artists side-by-side by popularity and followers
- Simple navigation with Home, Compare, and About pages

## Technologies

- Django (Python)
- SQLite database (via Django ORM)
- Spotify Web API (Client Credentials Flow)
- Chart.js (via CDN)
- HTML, CSS, basic JavaScript

## Setup Instructions

1. Clone or extract the project.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
