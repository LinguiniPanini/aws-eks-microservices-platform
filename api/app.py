from flask import Flask

import clientes
import domicilios
import productos
import notas

app = Flask(__name__)
app.register_blueprint(clientes.bp)
app.register_blueprint(domicilios.bp)
app.register_blueprint(productos.bp)
app.register_blueprint(notas.bp)

@app.get('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
