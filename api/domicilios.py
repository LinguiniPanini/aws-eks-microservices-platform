from flask import Blueprint, request, jsonify
from db import get_connection

bp = Blueprint('domicilios', __name__)

@bp.post('/clientes/<int:cliente_id>/domicilios')
def crear(cliente_id):
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO domicilios (cliente_id, domicilio, colonia, municipio, estado, tipo) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (cliente_id, body['domicilio'], body['colonia'], body['municipio'], body['estado'], body['tipo'])
            )
            nuevo_id = cur.fetchone()['id']
            conn.commit()
            return jsonify({'id': nuevo_id, 'cliente_id': cliente_id, **body}), 201
    finally:
        conn.close()

@bp.get('/clientes/<int:cliente_id>/domicilios')
def listar(cliente_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM domicilios WHERE cliente_id=%s", (cliente_id,))
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@bp.get('/domicilios/<int:domicilio_id>')
def obtener(domicilio_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM domicilios WHERE id=%s", (domicilio_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Domicilio no encontrado'}), 404
            return jsonify(row)
    finally:
        conn.close()

@bp.put('/domicilios/<int:domicilio_id>')
def actualizar(domicilio_id):
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE domicilios SET domicilio=%s, colonia=%s, municipio=%s, estado=%s, tipo=%s "
                "WHERE id=%s",
                (body['domicilio'], body['colonia'], body['municipio'], body['estado'], body['tipo'], domicilio_id)
            )
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Domicilio no encontrado'}), 404
            return jsonify({'id': domicilio_id, **body})
    finally:
        conn.close()

@bp.delete('/domicilios/<int:domicilio_id>')
def eliminar(domicilio_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM domicilios WHERE id=%s", (domicilio_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Domicilio no encontrado'}), 404
            return jsonify({'message': 'Domicilio eliminado'})
    finally:
        conn.close()
