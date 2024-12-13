<p align="center">
  <img src="assets/soundmood.png" alt="logo" height="180" />
</p>

<h1 align="center">SoundMood CC Service</h1>

<div align="center">

</div>

SoundMood is an application that allows you to predict the mood by uploading image of face, SoundMood predict the mood of the image, and return the most fitting playlist based on the uploaded image.

The service available:

- Authorization
  <pre>POST /auth/token</pre>

- Predictions
  <pre>POST /me/predict</pre>

- Playlist
  <pre>GET /me/playlist</pre>
  <pre>GET /me/playlist/{playlist_id}</pre>
  <pre>PUT /me/playlist/{playlist_id}</pre>

- User
  <pre>GET /me</pre>

# Tools
- [Google Cloud](https://cloud.google.com/)
- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Spotipy](https://github.com/spotipy-dev/spotipy)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)
- [Postman](https://www.postman.com/)

# Quick Look

## Architecture

<p align="center">
  <img src="assets/architecture.png" alt="architecture diagram" />
</p>

# Authentications

This service is using Spotify access token for getting an JWT token, your email need to be registered to Spotify Developer dashboard to get JWT token for using this service. Be aware that the JWT token is valid for only 1 day so you need to renew the access token by requesting GET /auth/token.

# Installation
1. Setup Memorystore for Redis Cluster, Cloud SQL, and Cloud Storage in your project.
2. Create database `soundmood` in your Cloud SQL.
3. Also, setup Pub/Sub with a topic name with the subscriptions below:
   * `plz-predict` with pull subscription, to handle output from ML service to BE service. 
   * `get-predict` with push subscription, to handle request from BE service.

4. Configure the following environment variables:

```bash
  DATABASE_URL: {database_url to soundmood db}
  JWT_SECRET: {your jwt secret}
  SHA_SECRET: {your sha key}
  REDIS_HOST: {your redis ip}
  REDIS_PORT: {your redis port}
  BUCKET_NAME: {your gcp bucket}
  PROJECT_ID: {your gcp project id}
  TOPIC_NAME: {your pub/sub topic name}
  ALGORITHM: HS256
  HOST: 0.0.0.0
```

5. Clone this repository and build container image for `be` and `ml` branch.

6. Deploy the Cloud Run using above image with the environment variables mentioned above.

# Testing

This service uses Postman to do API testing.

- You can download the Postman documentation [here](https://documenter.getpostman.com/view/40378264/2sAYHxnP79).

## Contributors

### CC Member 
CC member is responsible for the development of the API service and deployment of the model. In sort, in this project CC is responsible for Backend, infrastructure, and DevOps.
#### Individuals

<p>Vanes Angelo</p>

<p>Restu Dermawan Muhammad</p>

### ML Member
#### Individuals

<p>Tarisa Nur Safitri</p>

<p>Sanjukin Ndube Pinem</p>

<p>Antonius Wisang Bayu Nugraha</p>

### MD Member
#### Individuals

<p>Reisya Pratama</p>

<p>I Wayan Satya Widhya Putra Pratama</p>
