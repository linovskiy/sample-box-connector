# BOX connector

This is a basic sample connector.
It's been reworked from [Fallball Cloud Storage](https://github.com/odin-public/fallball-service).

## Running on localhost with tunnel

* Download and unzip sample-box-connector

* Install package and requirements for local development

```bash
python setup.py develop
```

* Update `config.json` file with your BOX credantials and OAuth data from APS Connect Portal


* Run application

```bash
$ python3 -m connector.app
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
