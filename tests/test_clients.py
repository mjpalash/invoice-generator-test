import io
import json
from wsgiref.util import setup_testing_defaults

import pytest

from invoice_app.app import create_app
from invoice_app.clients import ClientStore, ClientValidationError


@pytest.fixture
def store(tmp_path):
    return ClientStore(tmp_path / 'clients.sqlite3')


def valid_client(**overrides):
    data = {
        'name': 'Inspiria Knowledge Campus',
        'billing_address': 'Siliguri, West Bengal',
        'place_of_supply': 'Siliguri',
        'state': 'West Bengal',
        'gst_registered': False,
        'email': 'accounts@example.org',
    }
    data.update(overrides)
    return data


def call(app, method, path, data=None):
    raw = json.dumps(data).encode() if data is not None else b''
    environ = {}
    setup_testing_defaults(environ)
    environ.update(REQUEST_METHOD=method, PATH_INFO=path, CONTENT_LENGTH=str(len(raw)),
                   CONTENT_TYPE='application/json', **{'wsgi.input': io.BytesIO(raw)})
    result = {}
    def start_response(status, headers):
        result['status'] = int(status.split()[0])
        result['headers'] = dict(headers)
    body = b''.join(app(environ, start_response))
    result['body'] = json.loads(body) if result['headers'].get('Content-Type', '').startswith('application/json') else body.decode()
    return result


def test_save_and_list_valid_client(store):
    created = store.create(valid_client())
    assert created['id'] > 0
    assert created['name'] == 'Inspiria Knowledge Campus'
    assert store.list_clients() == [created]


def test_required_name_is_rejected_without_writing(store):
    with pytest.raises(ClientValidationError, match='Client name is required'):
        store.create(valid_client(name='  '))
    assert store.list_clients() == []


@pytest.mark.parametrize('field', ['billing_address', 'place_of_supply', 'state'])
def test_other_required_fields(store, field):
    with pytest.raises(ClientValidationError):
        store.create(valid_client(**{field: ''}))
    assert store.list_clients() == []


def test_registered_client_requires_valid_gstin(store):
    with pytest.raises(ClientValidationError, match='GSTIN'):
        store.create(valid_client(gst_registered=True, gstin=''))
    with pytest.raises(ClientValidationError, match='GSTIN'):
        store.create(valid_client(gst_registered=True, gstin='invalid'))
    created = store.create(valid_client(gst_registered=True, gstin='19ABCDE1234F1Z5'))
    assert created['gstin'] == '19ABCDE1234F1Z5'


def test_unregistered_client_does_not_require_or_store_gstin(store):
    created = store.create(valid_client(gst_registered=False, gstin='19ABCDE1234F1Z5'))
    assert created['gstin'] is None


def test_clients_survive_store_reopen(tmp_path):
    db = tmp_path / 'restart.sqlite3'
    original = ClientStore(db).create(valid_client())
    assert ClientStore(db).list_clients() == [original]


def test_api_create_and_list(tmp_path):
    app = create_app(tmp_path / 'api.sqlite3')
    response = call(app, 'POST', '/api/clients', valid_client())
    assert response['status'] == 201
    assert call(app, 'GET', '/api/clients')['body'][0]['id'] == response['body']['id']


def test_api_validation_error(tmp_path):
    app = create_app(tmp_path / 'api.sqlite3')
    response = call(app, 'POST', '/api/clients', valid_client(name=''))
    assert response['status'] == 422
    assert 'name' in response['body']['error'].lower()
    assert call(app, 'GET', '/api/clients')['body'] == []


def test_ui_serves_gst_conditional_form(tmp_path):
    app = create_app(tmp_path / 'ui.sqlite3')
    response = call(app, 'GET', '/')
    assert response['status'] == 200
    assert 'Client name' in response['body']
    assert 'gstRegistered' in response['body']
    assert 'gstinGroup' in response['body']
