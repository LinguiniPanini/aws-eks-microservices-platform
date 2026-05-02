import os
from datetime import datetime

import boto3
from flask import Flask, request, jsonify, Response
from fpdf import FPDF

import secret_store

app = Flask(__name__)
s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

def _bucket():
    return secret_store.get('examen2/s3')['bucket']

def _build_pdf(nota):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Nota de Venta', ln=True, align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Datos del Cliente', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"Razon Social: {nota['razon_social']}", ln=True)
    pdf.cell(0, 6, f"Nombre Comercial: {nota['nombre_comercial']}", ln=True)
    pdf.cell(0, 6, f"RFC: {nota['rfc']}", ln=True)
    pdf.cell(0, 6, f"Email: {nota['email']}", ln=True)
    pdf.cell(0, 6, f"Telefono: {nota['telefono']}", ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, f"Folio: {nota['folio']}", ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(20, 8, 'Cant.', 1)
    pdf.cell(70, 8, 'Producto', 1)
    pdf.cell(40, 8, 'P. Unitario', 1)
    pdf.cell(40, 8, 'Importe', 1)
    pdf.ln()

    pdf.set_font('Helvetica', '', 10)
    for item in nota['detalle']:
        pdf.cell(20, 8, str(item['cantidad']), 1)
        pdf.cell(70, 8, item['producto_nombre'], 1)
        pdf.cell(40, 8, f"${float(item['precio_unitario']):.2f}", 1)
        pdf.cell(40, 8, f"${float(item['importe']):.2f}", 1)
        pdf.ln()

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(130, 10, '', 0)
    pdf.cell(40, 10, f"Total: ${float(nota['total']):.2f}", 0)
    return bytes(pdf.output())

@app.post('/generate')
def generar():
    nota = request.get_json()
    pdf_bytes = _build_pdf(nota)
    key = f"{nota['rfc']}/{nota['folio']}.pdf"

    s3.put_object(
        Bucket=_bucket(),
        Key=key,
        Body=pdf_bytes,
        ContentType='application/pdf',
        Metadata={
            'hora-envio': datetime.utcnow().isoformat(),
            'nota-descargada': 'false',
            'veces-enviado': '1',
        },
    )
    return jsonify({'key': key, 'bucket': _bucket()})

@app.get('/download/<rfc>/<folio>')
def descargar(rfc, folio):
    key = f"{rfc}/{folio}.pdf"
    bucket = _bucket()
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()

    s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=key,
        Metadata={
            'hora-envio': obj['Metadata'].get('hora-envio', ''),
            'nota-descargada': 'true',
            'veces-enviado': obj['Metadata'].get('veces-enviado', '1'),
        },
        MetadataDirective='REPLACE',
    )
    return Response(body, mimetype='application/pdf')

@app.get('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
