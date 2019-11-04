import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry_sdk(dsn, environment):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
            LoggingIntegration(
                level=logging.ERROR,
                event_level=logging.ERROR
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        environment=environment,
        release="epay-version-v1.0",
    )
