import json
import os
from datetime import datetime

import boto3
import requests
from flask import Blueprint, request, jsonify, Response

import secret_store
from db import get_connection

bp = Blueprint('notas', __name__)

sqs = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

PDF_GENERATOR_URL = os.environ['PDF_GENERATOR_URL']

def _queue_url():
    return secret_store.get('examen2/sqs')['queue_url']

@bp.post('/notas')
def crear():
    body = request.get_json()
    detalle = body['detalle']
    folio = 'NV-' + datetime.now().strftime('%Y%m%d%H%M%S')
    total = sum(item['cantidad'] * item['precio_unitario'] for item in detalle)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notas_venta (folio, cliente_id, dir_facturacion_id, dir_envio_id, total) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (folio, body['cliente_id'], body['dir_facturacion_id'], body['dir_envio_id'], total)
            )
            nota_id = cur.fetchone()['id']

            for item in detalle:
                importe = item['cantidad'] * item['precio_unitario']
                cur.execute(
                    "INSERT INTO notas_venta_detalle (nota_id, producto_id, cantidad, precio_unitario, importe) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (nota_id, item['producto_id'], item['cantidad'], item['precio_unitario'], importe)
                )
            conn.commit()
    finally:
        conn.close()

    sqs.send_message(QueueUrl=_queue_url(), MessageBody=json.dumps({'nota_id': nota_id}))
    return jsonify({'id': nota_id, 'folio': folio, 'total': float(total)}), 201

@bp.get('/notas/<int:nota_id>')
def leer(nota_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nv.*, c.razon_social, c.nombre_comercial, c.rfc, c.email, c.telefono
                FROM notas_venta nv JOIN clientes c ON nv.cliente_id = c.id
                WHERE nv.id = %s
            """, (nota_id,))
            nota = cur.fetchone()
            if not nota:
                return jsonify({'error': 'Nota no encontrada'}), 404

            cur.execute("""
                SELECT nvd.*, p.nombre AS producto_nombre
                FROM notas_venta_detalle nvd JOIN productos p ON nvd.producto_id = p.id
                WHERE nvd.nota_id = %s
            """, (nota_id,))
            nota['detalle'] = cur.fetchall()

            cur.execute("SELECT * FROM domicilios WHERE id=%s", (nota['dir_facturacion_id'],))
            nota['dir_facturacion'] = cur.fetchone()
            cur.execute("SELECT * FROM domicilios WHERE id=%s", (nota['dir_envio_id'],))
            nota['dir_envio'] = cur.fetchone()
            return jsonify(nota)
    finally:
        conn.close()

@bp.get('/notas/<int:nota_id>/pdf')
def descargar(nota_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nv.folio, c.rfc FROM notas_venta nv
                JOIN clientes c ON nv.cliente_id = c.id WHERE nv.id = %s
            """, (nota_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'Nota no encontrada'}), 404
    finally:
        conn.close()

    resp = requests.get(f"{PDF_GENERATOR_URL}/download/{row['rfc']}/{row['folio']}", timeout=30)
    if resp.status_code != 200:
        return jsonify({'error': 'No se pudo obtener PDF'}), 502
    return Response(
        resp.content,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{row["folio"]}.pdf"'}
    )

@bp.post('/notas/<int:nota_id>/enviar')
def reenviar(nota_id):
    sqs.send_message(QueueUrl=_queue_url(), MessageBody=json.dumps({'nota_id': nota_id, 'reenvio': True}))
    return jsonify({'message': 'Encolado para reenvio', 'nota_id': nota_id}), 202
