import argparse
import pathlib
import trafaret as T

from trafaret_config import commandline

BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'dev.yml'

TRAFARET = T.Dict({
    T.Key('kafka'):
        T.Dict({
            'host': T.String(),
            'port': T.Int(),
            'topics': T.List(T.String())
        }),
    T.Key('consumers'):
        T.List(
            T.Dict({
                'host': T.String(),
                'port': T.Int(),
                'protocol': T.String(),
                'url': T.String(),
                'token': T.String(allow_blank=True),
            }),
        ),
    T.Key('mysql'):
        T.Dict({
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
        }),
    T.Key('email'):
        T.Dict({
            'host': T.String(),
            'port': T.Int(),
            'auth_required': T.Bool(),
            'username': T.String(allow_blank=True),
            'password': T.String(allow_blank=True),
            'email_to_notify': T.String(),
        }),
    T.Key('token'): T.String(),
    T.Key('host'): T.IP,
    T.Key('port'): T.Int(),
    T.Key('debug'): T.Bool(),
    T.Key('period_to_resend'): T.Int(),
    T.Key('resend_limit'): T.Int(),
    T.Key('sentry_dsn'): T.String(allow_blank=True),
})

def get_config(argv=None):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ap,
        default_config=DEFAULT_CONFIG_PATH
    )

    options, unknown = ap.parse_known_args(argv)

    if argv:
        options.config = "{}/config/{}.yml".format(BASE_DIR, options.config)

    config = commandline.config_from_options(options, TRAFARET)

    return config

def generate_consumers_url(app):
    headers = {
        'Content-Type': 'application/json'
    }
    consumers = []
    for consumer in app['config']['consumers']:
        headers['Authorization'] = consumer['token']
        consumer_url = "{}://{}:{}{}".format(
            consumer['protocol'],
            consumer['host'],
            consumer['port'],
            consumer['url']
        )
        consumers.append(
            {
                'headers': headers,
                'url': consumer_url
            }
        )

    app['consumers'] = consumers