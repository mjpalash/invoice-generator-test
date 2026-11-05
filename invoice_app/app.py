"""Dependency-free local WSGI UI and JSON API for Slice 1."""
import json
import os
from pathlib import Path
from wsgiref.simple_server import make_server
from .clients import ClientStore, ClientValidationError

HTML_PATH = Path(__file__).with_name('index.html')

def create_app(db_path):
    store = ClientStore(db_path)

    def app(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        status = '200 OK'
        content_type = 'application/json; charset=utf-8'
        if path == '/' and method == 'GET':
            content_type = 'text/html; charset=utf-8'
            body = HTML_PATH.read_bytes()
        elif path == '/api/clients' and method == 'GET':
            body = json.dumps(store.list_clients()).encode('utf-8')
        elif path == '/api/clients' and method == 'POST':
            try:
                length = int(environ.get('CONTENT_LENGTH') or 0)
                if length > 65536:
                    raise ClientValidationError('Client details are too large')
                data = json.loads(environ['wsgi.input'].read(length))
                created = store.create(data)
                status = '201 Created'
                body = json.dumps(created).encode('utf-8')
            except (ClientValidationError, json.JSONDecodeError, TypeError, ValueError) as error:
                status = '422 Unprocessable Entity'
                body = json.dumps({'error': str(error)}).encode('utf-8')
        else:
            status = '404 Not Found'
            body = json.dumps({'error': 'Not found'}).encode('utf-8')
        start_response(status, [('Content-Type', content_type), ('Content-Length', str(len(body))), ('Cache-Control', 'no-store')])
        return [body]

    return app

def main():
    db = Path(os.environ.get('INVOICE_DB', str(Path.home() / '.invoice-manager' / 'invoice.sqlite3')))
    host, port = '127.0.0.1', int(os.environ.get('INVOICE_PORT', '8765'))
    with make_server(host, port, create_app(db)) as server:
        print(f'Invoice Manager Slice 1: http://{host}:{port}  (database: {db})', flush=True)
        server.serve_forever()

if __name__ == '__main__':
    main()
