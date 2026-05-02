from flask import Blueprint, request, jsonify
from db import get_connection

bp = Blueprint('productos', __name__)

@bp.post('/productos')
def crear():
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO productos (nombre, unidad_medida, precio_base) VALUES (%s,%s,%s) RETURNING id",
                (body['nombre'], body['unidad_medida'], body['precio_base'])
            )
            nuevo_id = cur.fetchone()['id']
            conn.commit()
            return jsonify({'id': nuevo_id, **body}), 201
    finally:
        conn.close()

@bp.get('/productos')
def listar():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM productos")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@bp.get('/productos/<int:producto_id>')
def obtener(producto_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM productos WHERE id=%s", (producto_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Producto no encontrado'}), 404
            return jsonify(row)
    finally:
        conn.close()

@bp.put('/productos/<int:producto_id>')
def actualizar(producto_id):
    body = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE productos SET nombre=%s, unidad_medida=%s, precio_base=%s WHERE id=%s",
                (body['nombre'], body['unidad_medida'], body['precio_base'], producto_id)
            )
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Producto no encontrado'}), 404
            return jsonify({'id': producto_id, **body})
    finally:
        conn.close()

@bp.delete('/productos/<int:producto_id>')
def eliminar(producto_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM productos WHERE id=%s", (producto_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'error': 'Producto no encontrado'}), 404
            return jsonify({'message': 'Producto eliminado'})
    finally:
        conn.close()
