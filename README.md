# cloud-computing
<p align="center">
  <img src="assets/soundmood.png" alt="logo" height="180" />
</p>

<h1 align="center">SoundMood</h1>

<div align="center">

</div>

SoundMood is an application that allows you to predict the mood by uploading image of face, SoundMood predict the mood of the image, and return the most fitting playlist based on the uploaded image.

> Base url of this service is: http://localhost:8081/

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

# Quick Look

## Architecture

<p align="center">
  <img src="assets/architecture.png" alt="architecture diagram" />
</p>

# Authentications

This service is using token for authentication, your email need to be registered to get access token for using this service, the acess token is valid for only 60 minutes, you need renew the access token by requesting with /get/auth

# Environment

In order to run this project, you need to configure the following environment variables:

```bash
  DATABASE_URL: {database_url}
  JWT_SECRET: {your jwt secret}
  SHA_SECRET: {your sha key}
  REDIS_HOST: {your redis ip}
  REDIS_PORT: {your redis port}
  BUCKET_NAME: {your gcp bucket}
  PROJECT_ID: {your gcp projec id}
  TOPIC_NAME: {your pub/sub topic name}
  ALGORITHM: HS256
  HOST: 0.0.0.0
```

Then you can use the following image to create your own database:

# Testing

This Web service uses Postman to test.

- You can download the Postman documentation [here](https://documenter.getpostman.com/view/40378264/2sAYHxnP79).

If you want to contribute to this project, please contact me.

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
