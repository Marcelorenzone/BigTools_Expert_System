import os
import json
from flask import Flask, request, jsonify
from functools import wraps
from werkzeug.security import safe_str_cmp # Para comparar contraseñas de forma segura
from base64 import b64decode

# Asegúrate de que las rutas son relativas al directorio principal del proyecto
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE_CONOCIMIENTO = os.path.join(ROOT_DIR, '..', 'base_conocimiento.json')
RUTA_USUARIOS = os.path.join(ROOT_DIR, 'usuarios.json')

# Importar las clases de la carpeta core
import sys
sys.path.append(os.path.join(ROOT_DIR, '..', 'core'))
from motor_diagnostico import MotorDiagnostico
from base_conocimientos import BaseConocimientos

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
app = Flask(__name__)

def cargar_motor_y_bk():
    """Carga y recarga el Motor de Diagnóstico con la última BK."""
    global DIAG_ENGINE
    try:
        bk = BaseConocimientos().from_json(RUTA_BASE_CONOCIMIENTO)
        DIAG_ENGINE = MotorDiagnostico(bk)
        print("✅ Motor de diagnóstico cargado y listo.")
    except Exception as e:
        print(f"🚨 Error al inicializar el motor: {e}")
        DIAG_ENGINE = None

# Inicializar motor al inicio del servidor
DIAG_ENGINE = None
cargar_motor_y_bk()

# Carga la base de usuarios
def cargar_usuarios():
    with open(RUTA_USUARIOS, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- DECORADOR DE AUTENTICACIÓN ---
def requiere_rol(roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get('Authorization')
            if not auth or not auth.startswith('Basic '):
                return jsonify({'error': 'Faltan credenciales (Autorización Basic requerida).'}), 401

            try:
                # Decodificar el par username:password
                auth_data = b64decode(auth.split(' ')[1]).decode('utf-8')
                username, password = auth_data.split(':', 1)
            except:
                return jsonify({'error': 'Formato de autenticación incorrecto.'}), 401
            
            users = cargar_usuarios()
            user_data = users.get(username)

            if user_data and safe_str_cmp(password, user_data['password']) and user_data['rol'] in roles:
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Acceso denegado o credenciales inválidas.'}), 403
        return decorated
    return wrapper

# --- ENDPOINTS PÚBLICOS (Técnicos) ---

@app.route('/api/diagnostico', methods=['POST'])
@requiere_rol(['administrador', 'tecnico_libre'])
def diagnostico_handler():
    if DIAG_ENGINE is None:
        return jsonify({"error": "El motor de inferencia no está disponible."}), 503
        
    data = request.json
    estado = data.get('estado')
    
    if estado is None:
        # A. INICIO DE LA SESIÓN 
        id_maquina = data.get('id_maquina')
        descripcion_inicial = data.get('descripcion')
        if not id_maquina or not descripcion_inicial:
            return jsonify({"error": "Faltan parámetros de inicio (máquina/descripción)."}), 400

        resultado = DIAG_ENGINE.iniciar_diagnostico(id_maquina, descripcion_inicial)
    else:
        # B. CONTINUACIÓN DE LA SESIÓN 
        respuesta_usuario = data.get('respuesta')
        if respuesta_usuario is None:
            return jsonify({"error": "Falta la respuesta del usuario ('si'/'no')."}), 400
        
        resultado = DIAG_ENGINE.procesar_respuesta(estado, respuesta_usuario)
    
    return jsonify(resultado)

# --- ENDPOINT DE ADMINISTRACIÓN (Actualización de Base de Conocimiento) ---

@app.route('/api/admin/actualizar_bk', methods=['POST'])
@requiere_rol(['administrador']) # SOLO ADMINISTRADORES
def actualizar_base_conocimiento():
    """Permite al administrador subir y guardar la nueva base de conocimiento."""
    try:
        data_json = request.json
        
        # Guardar el JSON directamente en el archivo
        with open(RUTA_BASE_CONOCIMIENTO, 'w', encoding='utf-8') as f:
            json.dump(data_json, f, indent=2)

        # Recargar el motor de inferencia para usar la nueva base de conocimiento
        cargar_motor_y_bk()

        return jsonify({"mensaje": "✅ Base de conocimiento actualizada y motor recargado con éxito."})
    
    except Exception as e:
        return jsonify({"error": f"Error al guardar o recargar la Base de Conocimiento: {e}"}), 500

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Usar puerto 5000 por defecto
    app.run(debug=True, port=5000)
