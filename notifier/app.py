import os
from datetime import datetime

import boto3
from flask import Flask, request, jsonify

import secret_store

app = Flask(__name__)
sns = boto3.client('sns', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

API_PUBLIC_URL = os.environ['API_PUBLIC_URL']

def _topic_arn():
    return secret_store.get('examen2/sns')['topic_arn']

def _bucket():
    return secret_store.get('examen2/s3')['bucket']

@app.post('/notify')
def notificar():
    body = request.get_json()
    folio = body['folio']
    nota_id = body['nota_id']
    nombre = body['nombre_comercial']
    email = body['email']
    rfc = body['rfc']

    download_url = f"{API_PUBLIC_URL}/notas/{nota_id}/pdf"
    asunto = f"Nota de Venta {folio}"
    mensaje = (
        f"Estimado {nombre},\n\n"
        f"Se ha generado su nota de venta con folio {folio}.\n"
        f"Puede descargarla en: {download_url}\n"
    )

    sns.publish(
        TopicArn=_topic_arn(),
        Subject=asunto,
        Message=mensaje,
        MessageAttributes={'email': {'DataType': 'String', 'StringValue': email}},
    )

    key = f"{rfc}/{folio}.pdf"
    bucket = _bucket()
    obj = s3.head_object(Bucket=bucket, Key=key)
    veces = int(obj['Metadata'].get('veces-enviado', '0')) + 1
    s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=key,
        Metadata={
            'hora-envio': datetime.utcnow().isoformat(),
            'nota-descargada': obj['Metadata'].get('nota-descargada', 'false'),
            'veces-enviado': str(veces),
        },
        MetadataDirective='REPLACE',
    )

    return jsonify({'message': 'Notificacion enviada', 'veces_enviado': veces})

@app.get('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
