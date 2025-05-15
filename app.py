from flask import Flask, request, render_template_string, redirect, url_for
from supabase import create_client, Client
from datetime import datetime

# Conexión a Supabase
url = "https://ldbapinptjixpxhvuium.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkYmFwaW5wdGppeHB4aHZ1aXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyODM5NTgsImV4cCI6MjA2Mjg1OTk1OH0.bihkJfDLl_-nA2q9gFGxAwQiskRO1coiWu6rXAT9Bpw"
supabase: Client = create_client(supabase_url=url, supabase_key=key)

app = Flask(__name__)

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>FedEx - Rastreo de Paquetes</title>
    <style>
        body {
            background: url("{{ url_for('static', filename='img/background.jpg') }}") no-repeat center center fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
            color: #fff;
            text-align: center;
        }
        .container {
            margin-top: 100px;
        }
        input[type=text], input[type=date] {
            padding: 10px;
            width: 300px;
            border: none;
            border-radius: 5px;
        }
        input[type=submit] {
            padding: 10px 20px;
            background-color: #ff6600;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .resultado {
            margin-top: 30px;
            background-color: #fff;
            color: #000;
            padding: 20px;
            display: inline-block;
            border-radius: 10px;
        }
        img {
            max-width: 200px;
            margin-bottom: 10px;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ url_for('static', filename='img/fedex_logo.jpeg') }}" class="logo">
        <h1>Rastreo de Paquetes</h1>
        <form method="POST" action="/track">
            <input type="text" name="tracking" placeholder="Ingresa tu número de rastreo" required>
            <br><br>
            <input type="submit" value="Rastrear">
        </form>

        {% if show_add %}
            <br><br>
            <a href="/agregar" style="color: white; background-color: green; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Agregar Paquete</a>
        {% endif %}

        {% if datos %}
        <div class="resultado">
            <img src="{{ url_for('static', filename='img/' ~ datos.foto) }}" alt="Foto del paquete">
            <p><strong>Número de Rastreo:</strong> {{ datos.numero }}</p>
            <p><strong>Nombre:</strong> {{ datos.nombre }}</p>
            <p><strong>Estado:</strong> {{ datos.estado }}</p>
            <p><strong>Origen:</strong> {{ datos.pais_origen }}</p>
            <p><strong>Destino:</strong> {{ datos.pais_destino }}</p>
            <p><strong>Dirección:</strong> {{ datos.direccion }}</p>
            <p><strong>Responsable:</strong> {{ datos.responsable }}</p>
            <p><strong>Fecha de Envío:</strong> {{ datos.fecha_envio }}</p>
            <p><strong>Última Actualización:</strong> {{ datos.ultima_actualizacion }}</p>
        </div>
        {% elif datos is not none %}
        <div class="resultado">
            <p>Paquete no encontrado.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_template, datos=None, show_add=False)

@app.route('/track', methods=['POST'])
def track():
    numero = request.form['tracking']

    if numero.lower() == 'agregarpaquetes':
        return render_template_string(html_template, datos=None, show_add=True)

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
        return render_template_string(html_template, datos=datos, show_add=False)
    else:
        return render_template_string(html_template, datos=None, show_add=False)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        datos = {
            "numero": request.form['numero'],
            "nombre": request.form['nombre'],
            "estado": request.form['estado'],
            "pais_origen": request.form['pais_origen'],
            "pais_destino": request.form['pais_destino'],
            "direccion": request.form['direccion'],
            "responsable": request.form['responsable'],
            "foto": request.form['foto'],
            "fecha_envio": request.form['fecha_envio'],
            "ultima_actualizacion": datetime.now().isoformat()
        }
        supabase.table("paquetes").insert(datos).execute()
        return redirect(url_for('home'))

    return '''
    <form method="POST">
        <input type="text" name="numero" placeholder="Número de rastreo" required><br><br>
        <input type="text" name="nombre" placeholder="Nombre del destinatario" required><br><br>
        <input type="text" name="estado" placeholder="Estado (Ej: En tránsito)" required><br><br>
        <input type="text" name="pais_origen" placeholder="País de origen" required><br><br>
        <input type="text" name="pais_destino" placeholder="País destino" required><br><br>
        <input type="text" name="direccion" placeholder="Dirección" required><br><br>
        <input type="text" name="responsable" placeholder="Responsable" required><br><br>
        <input type="text" name="foto" placeholder="Nombre de la imagen (Ej: paquete1.jpg)" required><br><br>
        <input type="date" name="fecha_envio" required><br><br>
        <input type="submit" value="Guardar">
    </form>
    '''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)