
import os
import json
import pytest

from fixtures import flask_client


def test_misc_routes(flask_client):
    misc_routes = [
        "/",
        "/api/list",
    ]
    for r in misc_routes:
        resp = flask_client.get(r)
        assert resp.status_code == 200

