def test_client_login():
    from package.client import Client
    client = Client()
    client.login()
    assert client.auth_token is not None
    assert client.feed_token is not None
    assert client.smartApi is not None

