# Fallball connector

This is a basic sample connector for the [Fallball Cloud Storage](https://github.com/odin-public/fallball-service).

[![Build Status](https://travis-ci.org/odin-public/fallball-connector.svg?branch=master)](https://travis-ci.org/odin-public/fallball-connector)
[![Coverage Status](https://coveralls.io/repos/github/odin-public/fallball-connector/badge.svg?branch=master)](https://coveralls.io/github/odin-public/fallball-connector?branch=master)

## Running on localhost with tunnel

* Download and unzip fallball-connector

* Install package and requirements for local development

```bash
python setup.py develop
```

* Update `config.json` file with your credantials

```json
{
    "fallball_service_url": "PUT_HERE_FALLBALL_SERVICE_URI",
    "fallball_service_authorization_token": "PUT_HERE_FALLBALL_SERVICE_AUTHORIZATION_TOKEN",
    "oauth_key": "PUT_HERE_OAUTH_KEY",
    "oauth_signature": "PUT_HERE_OAUTH_SIGNATURE"
}
```

* Run application

```bash
$ python connector/app.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

* Create HTTP tunnel with [ngrok](https://ngrok.io)

```bash
ngrok http 5000
```

* Use public connector URL <https://YOUR_UNIQ_ID.ngrok.io/v1/>

If you run connector without SSL behind SSL-enabled reverse proxy, make sure that proxy populates the `X-Forwarded-Proto` header.

## Running in Docker

```bash
docker-compose up
```

Application is started in debug mode in docker container on port 5000.

## Development

* Run unit tests

```bash
python setup.py nosetests
```
