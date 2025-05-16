from flask import Flask, request, render_template, redirect, url_for
from supabase import create_client, Client
from datetime import datetime
import random

# Conexión a Supabase
url = "https://ldbapinptjixpxhvuium.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkYmFwaW5wdGppeHB4aHZ1aXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyODM5NTgsImV4cCI6MjA2Mjg1OTk1OH0.bihkJfDLl_-nA2q9gFGxAwQiskRO1coiWu6rXAT9Bpw"
supabase: Client = create_client(supabase_url=url, supabase_key=key)

app = Flask(__name__)

def calcular_peso_100mil():
    # Peso simulado para 100mil dólares en billetes de 100
    return round(random.uniform(1.0, 1.5), 2)

def calcular_distancia(origen, destino):
    # Distancia simulada
    return f"{random.randint(1500, 7000)} km"

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    datos = None
    info_paquete = None
    if request.method == 'POST':
        numero = request.form['numero']
        if numero.strip().lower() == "agregarpaquetes":
            return redirect(url_for('agregar'))
        response = supabase.table("paquetes").select("*").eq("numero", numero).execute()
        data = response.data
        if data:
            paquete = data[0]
            datos = {
                'numero': paquete['numero'],
                'nombre': paquete['nombre'],
                'estado': paquete['estado'],
                'pais_origen': paquete['pais_origen'],
                'pais_destino': paquete['pais_destino'],
                'direccion': paquete['direccion'],
                'responsable': paquete['responsable'],
                'foto': paquete['foto'],
                'fecha_envio': paquete['fecha_envio'],
                'ultima_actualizacion': paquete['ultima_actualizacion']
            }
            info_paquete = {
                "tipo": paquete.get("tipo_paquete", "Dinero"),
                "enviado_por": paquete.get("remitente", "LEONOR DE TODOS LOS SANTOS DE BORBEN Y ORTIZ"),
                "peso": calcular_peso_100mil(),
                "distancia": calcular_distancia(paquete['pais_origen'], paquete['pais_destino'])
            }
        else:
            error = "El código ingresado no es correcto o no existe en la base de datos."
    return render_template('index.html', datos=datos, info_paquete=info_paquete, error=error)

@app.route('/ver_info/<numero>')
def ver_info(numero):
    response = supabase.table("paquetes").select("*").eq("numero", numero).execute()
    data = response.data
    if data:
        paquete = data[0]
        info_paquete = {
            "tipo": paquete.get("tipo_paquete", "Dinero"),
            "enviado_por": paquete.get("remitente", "LEONOR DE TODOS LOS SANTOS DE BORBEN Y ORTIZ"),
            "peso": calcular_peso_100mil(),
            "distancia": calcular_distancia(paquete['pais_origen'], paquete['pais_destino'])
        }
        return render_template('info_paquete.html', info_paquete=info_paquete, datos=paquete)
    else:
        return "Paquete no encontrado", 404

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        numero = request.form['numero']
        nombre = request.form['nombre']
        estado = request.form['estado']
        pais_origen = request.form['pais_origen']
        pais_destino = request.form['pais_destino']
        direccion = request.form['direccion']
        responsable = request.form['responsable']
        foto = request.form['foto']
        tipo_paquete = request.form['tipo_paquete']
        peso = request.form['peso']
        remitente = request.form['remitente']
        fecha_envio = request.form['fecha_envio']
        ultima_actualizacion = datetime.now().isoformat()
        # Insertar el paquete en la base de datos
        supabase.table("paquetes").insert({
            "numero": numero,
            "nombre": nombre,
            "estado": estado,
            "pais_origen": pais_origen,
            "pais_destino": pais_destino,
            "direccion": direccion,
            "responsable": responsable,
            "foto": foto,
            "tipo_paquete": tipo_paquete,
            "peso": peso,
            "remitente": remitente,
            "fecha_envio": fecha_envio,
            "ultima_actualizacion": ultima_actualizacion
        }).execute()
        return redirect(url_for('home'))
    return render_template('agregar.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)