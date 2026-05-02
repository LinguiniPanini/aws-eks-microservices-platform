from flask import Blueprint, request, jsonify
from db import get_connection

bp = Blueprint('clientes', __name__)

@bp.post('/clientes')
def crear():
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO clientes (razon_social, nombre_comercial, rfc, email, telefono) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (body['razon_social'], body['nombre_comercial'], body['rfc'], body['email'], body['telefono'])
            )
            nuevo_id = cur.fetchone()['id']
            conn.commit()
            return jsonify({'id': nuevo_id, **body}), 201
    finally:
        conn.close()

@bp.get('/clientes')
def listar():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clientes")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@bp.get('/clientes/<int:cliente_id>')
def obtener(cliente_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clientes WHERE id=%s", (cliente_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            return jsonify(row)
    finally:
        conn.close()

@bp.put('/clientes/<int:cliente_id>')
def actualizar(cliente_id):
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE clientes SET razon_social=%s, nombre_comercial=%s, rfc=%s, email=%s, telefono=%s "
                "WHERE id=%s",
                (body['razon_social'], body['nombre_comercial'], body['rfc'], body['email'], body['telefono'], cliente_id)
            )
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            return jsonify({'id': cliente_id, **body})
    finally:
        conn.close()

@bp.delete('/clientes/<int:cliente_id>')
def eliminar(cliente_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            return jsonify({'message': 'Cliente eliminado'})
    finally:
        conn.close()
