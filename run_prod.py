from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    serve(
        app, 
        host='0.0.0.0', 
        port=5000,
        trusted_proxy='127.0.0.1',
        trusted_proxy_headers=['x-forwarded-for', 'x-forwarded-proto', 'x-forwarded-host', 'x-forwarded-port']
    )
