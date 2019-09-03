# Image-resizer

This project provides a REST API that can be used to resize images.

## Usage

Note: On Windows, this application runs with docker-compose version 1.23.2.

1. To start the service, just type `docker-compose up` in the root directory.
2. Go to Postman, select POST, and enter <http://127.0.0.1:5000/images/api/v1/send-resizing-request> as the URL.
3. Enter the JSON payload on the `Body` tab. The `key` in the payload is "urls" and the `value` is a list of URLs pointing to the images to be resized. Here is an example of what the JSON payload should look like:

    ```json
    {
        "urls": [
            "https://avatars0.githubusercontent.com/200",
            "https://avatars0.githubusercontent.com/2010"
        ]
    }
    ```

4. 


## Architecture

This application uses `docker-compose` and can be started using `docker-compose up`. It uses along running architecture such that the bulk of the image resizing operations are done in the background.

Mutiple images can be submitted for resizing in a single request.

These are the services started by `docker-compose`:

- web: This is the main microservice that the client interacts with. The available end-points are:

  - POST /images/api/v1/send-images: Not meant to be used by the client. This is used by the kafka consumer microservice to send back processed images to the client facing microservice.
  - POST /images/api/v1/send-resizing-request: Sends the given JSON payload, containing links to multiple images, for resizing.
  - GET /images/api/v1/get-request/<string:request_id>: Gets the resized images for the specified request.
  - GET /images/api/v1/get-image/<string:image_id>: Gets the specified image after resizing.

- consumer: This microservice runs kafka consumer in the background. It polls messages from kafka, resizes the images and sends them back to the `web` microservice over HTTP

- kafka: This acts as the kafka broker, which is basically a middleman between the kafka producer and consumer. For this service, port 9092 is exposed for use by the internal docker network.

- zookeeper: This is used by the kafka service. It is required to track status of various kafka nodes. 


## Improvements/ Scope of Future Work

### Minor improvements which could add more functionality and enhance user experience

- Provide functionality to provide images as either URLs or from the filesystem.
 <!-- search "send image to rest api" -->