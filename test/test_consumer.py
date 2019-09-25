from kafka_consumer import consumer


def test_process_urls():
    url_root = 'localhost:8080'
    urls = ['https://avatars0.githubusercontent.com/2',
            'https://avatars0.githubusercontent.com/20']
    output_dictionary = consumer.process_urls(urls, url_root)
    assert len(output_dictionary['result']['resized_images']) == len(urls)
    assert len(consumer.image_map) == len(urls)


def test_compress_and_get_output_file_name():
    output = consumer.compress_and_get_output_file_name(
        'https://avatars0.githubusercontent.com/2')
    assert output
    assert consumer.image_map
