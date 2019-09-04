# Image-resizer

This project provides a REST API that can be used to resize images.

## Usage

Note: On Windows, this application runs with docker-compose version 1.23.2.

1. To start the service, just type `docker-compose up` in the root directory.
2. Go to Postman (or make a curl request), select POST, and enter <http://127.0.0.1:5000/images/api/v1/send-resizing-request> as the URL.
3. Enter the JSON payload on the `Body` tab. The `key` in the payload is "urls" and the `value` is a list of URLs pointing to the images to be resized. Here is an example of what the JSON payload should look like:

    ```json
    {
        "urls": [
            "https://avatars0.githubusercontent.com/200",
            "https://avatars0.githubusercontent.com/2010"
        ]
    }
    ```

Currently, input can only be provided as such links pointing to the images.
4. Once you make this request, you will recieve an output as follows:

```json
{
"request": "http://127.0.0.1:5000/images/api/v1/get-request/fcc7404b-b6cd-4d75-85a6-b1494128400f"
}
```

This means that the request was successful and it has been added to the Kafka queue for processing.
5. Make a GET request to the URL returned in the previous step: <http://127.0.0.1:5000/images/api/v1/get-request/fcc7404b-b6cd-4d75-85a6-b1494128400f>
6. You will get a JSON response containing the links to the resized images as follows:

```json
{
  "resized_images": [
    "http://127.0.0.1:5000/images/api/v1/get-image/c23078ba-0b72-4ee0-9c76-be4ed055fe96",
    "http://127.0.0.1:5000/images/api/v1/get-image/0b6afda9-9ede-4755-b955-13e09b6bbd54"
  ]
}
```

7. Make a GET request to any of the links returned in the previous step to get the resized image.

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

- zookeeper: This is used by the kafka service. It is required to track status of various kafka nodes and coordinate between them.

## Improvements/ Scope of Future Work

### Minor improvements which could add more functionality and enhance user experience

- Provide functionality to provide images as either URLs or from the filesystem.
- Currently, everything is being stored in memory. A DB instance should be used to store the images and the requests.

### Testing

- Currently, only basic unit tests have been written. More tests to cover corner cases and increase code coverage could be written.
- Testing could also be done by creating a script to run the application and then make API calls to it and verify the results.
