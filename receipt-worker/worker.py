import json
import os
import time
from decimal import Decimal

import boto3
import requests

import secret_store
from db import get_connection


def _jsonable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"no serializable: {type(obj)}")

REGION = os.environ.get('AWS_REGION', 'us-east-1')
PDF_GENERATOR_URL = os.environ['PDF_GENERATOR_URL']
NOTIFIER_URL = os.environ['NOTIFIER_URL']

sqs = boto3.client('sqs', region_name=REGION)

def cargar_nota(nota_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nv.id, nv.folio, nv.total,
                       c.razon_social, c.nombre_comercial, c.rfc, c.email, c.telefono
                FROM notas_venta nv JOIN clientes c ON nv.cliente_id = c.id
                WHERE nv.id = %s
            """, (nota_id,))
            nota = cur.fetchone()
            if not nota:
                return None

            cur.execute("""
                SELECT nvd.cantidad, nvd.precio_unitario, nvd.importe, p.nombre AS producto_nombre
                FROM notas_venta_detalle nvd JOIN productos p ON nvd.producto_id = p.id
                WHERE nvd.nota_id = %s
            """, (nota_id,))
            nota['detalle'] = cur.fetchall()
            return nota
    finally:
        conn.close()

def procesar(nota_id, reenvio):
    nota = cargar_nota(nota_id)
    if not nota:
        print(f"Nota {nota_id} no encontrada, descartando")
        return

    if not reenvio:
        r = requests.post(
            f"{PDF_GENERATOR_URL}/generate",
            data=json.dumps(nota, default=_jsonable),
            headers={'Content-Type': 'application/json'},
            timeout=60,
        )
        r.raise_for_status()

    payload = {
        'nota_id': nota['id'],
        'folio': nota['folio'],
        'rfc': nota['rfc'],
        'email': nota['email'],
        'nombre_comercial': nota['nombre_comercial'],
    }
    r = requests.post(f"{NOTIFIER_URL}/notify", json=payload, timeout=30)
    r.raise_for_status()

def main():
    queue_url = secret_store.get('examen2/sqs')['queue_url']
    print(f"Escuchando cola {queue_url}")
    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
        )
        for msg in resp.get('Messages', []):
            try:
                body = json.loads(msg['Body'])
                procesar(body['nota_id'], body.get('reenvio', False))
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
                time.sleep(2)

if __name__ == '__main__':
    main()
