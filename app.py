from flask import Flask, request, render_template
from supabase import create_client, Client
from datetime import datetime
import random
import json
from math import radians, sin, cos, sqrt, atan2

url = "https://ldbapinptjixpxhvuium.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkYmFwaW5wdGppeHB4aHZ1aXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyODM5NTgsImV4cCI6MjA2Mjg1OTk1OH0.bihkJfDLl_-nA2q9gFGxAwQiskRO1coiWu6rXAT9Bpw"
supabase: Client = create_client(supabase_url=url, supabase_key=key)

app = Flask(__name__)

COORDS_PAISES = {
    "españa": (40.4168, -3.7038),
    "alemania": (52.52, 13.405),
    "argentina": (-34.6037, -58.3816),
    "australia": (-35.2809, 149.13),
    "brasil": (-15.7939, -47.8828),
    "canadá": (45.4215, -75.6997),
    "canada": (45.4215, -75.6997),
    "chile": (-33.4489, -70.6693),
    "china": (39.9042, 116.4074),
    "colombia": (4.7110, -74.0721),
    "corea del sur": (37.5665, 126.9780),
    "costa rica": (9.9281, -84.0907),
    "cuba": (23.1136, -82.3666),
    "dinamarca": (55.6761, 12.5683),
    "ecuador": (-0.1807, -78.4678),
    "egipto": (30.0444, 31.2357),
    "el salvador": (13.6929, -89.2182),
    "emiratos árabes unidos": (25.2048, 55.2708),
    "emiratos arabes unidos": (25.2048, 55.2708),
    "estados unidos": (37.0902, -95.7129),
    "francia": (48.8566, 2.3522),
    "guatemala": (14.6349, -90.5069),
    "honduras": (14.0723, -87.1921),
    "india": (28.6139, 77.2090),
    "italia": (41.9028, 12.4964),
    "japón": (35.6895, 139.6917),
    "japon": (35.6895, 139.6917),
    "méxico": (19.4326, -99.1332),
    "mexico": (19.4326, -99.1332),
    "nicaragua": (12.1364, -86.2514),
    "noruega": (59.9139, 10.7522),
    "panamá": (8.9824, -79.5199),
    "panama": (8.9824, -79.5199),
    "paraguay": (-25.2637, -57.5759),
    "perú": (-12.0464, -77.0428),
    "peru": (-12.0464, -77.0428),
    "polonia": (52.2297, 21.0122),
    "portugal": (38.7223, -9.1393),
    "reino unido": (51.5074, -0.1278),
    "república dominicana": (18.4861, -69.9312),
    "republica dominicana": (18.4861, -69.9312),
    "rusia": (55.7558, 37.6173),
    "sudáfrica": (-25.7479, 28.2293),
    "sudafrica": (-25.7479, 28.2293),
    "suecia": (59.3293, 18.0686),
    "suiza": (46.948, 7.4474),
    "turquía": (39.9334, 32.8597),
    "turquia": (39.9334, 32.8597),
    "uruguay": (-34.9011, -56.1645),
    "venezuela": (10.4806, -66.9036)
}

def calcular_peso_100mil():
    return round(random.uniform(1.0, 1.5), 2)

def calcular_distancia(origen, destino):
    origen = (origen or '').strip().lower()
    destino = (destino or '').strip().lower()
    if origen in COORDS_PAISES and destino in COORDS_PAISES:
        lat1, lon1 = COORDS_PAISES[origen]
        lat2, lon2 = COORDS_PAISES[destino]
        # Fórmula Haversine
        R = 6371  # Radio de la Tierra en km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distancia = R * c
        return f"{distancia:.0f} km"
    else:
        return "-"

def ubicacion_aleatoria(pais):
    pais = pais.strip().lower()
    base_lat, base_lon = COORDS_PAISES.get(pais, (20.0, -40.0))
    return {
        "lat": base_lat + random.uniform(-1.0, 1.0),
        "lon": base_lon + random.uniform(-1.0, 1.0)
    }

NIVELES_ESTADO = {
    "etiqueta creada": 1,
    "en tránsito": 2,
    "en transito": 2,
    "tenemos tu paquete": 2,
    "en espera de pago de impuesto": 3,
    "retenido": 4,
    "en revisión aduanal": 4,
    "en revision aduanal": 4,
    "entregado": 5
}

@app.route('/ver_info/<numero>')
def ver_info(numero):
    response = supabase.table("paquetes").select("*").eq("numero", numero).execute()
    data = response.data
    if data:
        paquete = data[0]
        info_paquete = {
            "tipo": paquete.get("tipo_paquete", "Dinero"),
            "enviado_por": paquete.get("remitente", "LEONOR DE TODOS LOS SANTOS DE BORBEN Y ORTIZ"),
            "peso": paquete.get("peso") or calcular_peso_100mil(),
            "distancia": calcular_distancia(paquete.get('pais_origen',''), paquete.get('pais_destino',''))
        }
        ubicacion = None
        # Determinar ubicación según estado
        estado_actual = paquete['estado'].strip().lower()
        if estado_actual == 'entregado' and paquete.get('pais_destino'):
            ubicacion = json.dumps(ubicacion_aleatoria(paquete['pais_destino']))
        elif paquete.get('pais_origen'):
            ubicacion = json.dumps(ubicacion_aleatoria(paquete['pais_origen']))
        else:
            ubicacion = json.dumps({})
        historial = None
        nivel_estado = NIVELES_ESTADO.get(estado_actual, 1)
        return render_template(
            'info_paquete.html',
            datos=paquete,
            info_paquete=info_paquete,
            historial=historial,
            ubicacion=ubicacion,
            nivel_estado=nivel_estado
        )
    else:
        return "Paquete no encontrado", 404

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    datos = None
    info_paquete = None
    ubicacion = None
    mostrar_formulario_agregar = False
    exito_agregado = False

    if request.method == 'POST':
        if 'numero' in request.form:
            numero = request.form['numero']
            if numero.strip().lower() == "agregarpaquetes":
                mostrar_formulario_agregar = True
            else:
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
                        'ultima_actualizacion': paquete['ultima_actualizacion'],
                        'mensaje_personalizado': paquete.get('mensaje_personalizado', '')
                    }
                    info_paquete = {
                        "tipo": paquete.get("tipo_paquete", "Dinero"),
                        "enviado_por": paquete.get("remitente", "LEONOR DE TODOS LOS SANTOS DE BORBEN Y ORTIZ"),
                        "peso": calcular_peso_100mil(),
                        "distancia": calcular_distancia(paquete['pais_origen'], paquete['pais_destino'])
                    }
                    ubicacion = json.dumps(ubicacion_aleatoria(paquete['pais_origen']))
                else:
                    error = "El código ingresado no es correcto o no existe en la base de datos."
        elif 'numero_nuevo' in request.form:
            numero = request.form['numero_nuevo']
            nombre = request.form['nombre_nuevo']
            estado = request.form['estado_nuevo']
            pais_origen = request.form['pais_origen_nuevo']
            pais_destino = request.form['pais_destino_nuevo']
            direccion = request.form['direccion_nuevo']
            responsable = request.form['responsable_nuevo']
            foto = request.form['foto_nuevo']
            tipo_paquete = request.form['tipo_paquete_nuevo']
            peso = request.form['peso_nuevo']
            remitente = request.form['remitente_nuevo']
            fecha_envio = request.form['fecha_envio_nuevo']
            mensaje_personalizado = request.form.get('mensaje_personalizado_nuevo', '')
            ultima_actualizacion = datetime.now().isoformat()
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
                "mensaje_personalizado": mensaje_personalizado,
                "ultima_actualizacion": ultima_actualizacion
            }).execute()
            exito_agregado = True
            mostrar_formulario_agregar = False

    return render_template('index.html',
        datos=datos,
        info_paquete=info_paquete,
        error=error,
        ubicacion=ubicacion,
        mostrar_formulario_agregar=mostrar_formulario_agregar,
        exito_agregado=exito_agregado
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)