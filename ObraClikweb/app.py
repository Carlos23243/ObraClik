import os
import pymysql
from pymysql.cursors import DictCursor

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, session, g
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'obraclick_clave_secreta_provisoria')

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Astro2255')
MYSQL_DB = os.environ.get('MYSQL_DB', 'obraclick_db')
MYSQL_PORT = 3306

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

IVA_TASA = 0.15


def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# BASE DE DATOS
# ============================================================

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            autocommit=True,
            cursorclass=DictCursor
        )
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Contador del carrito disponible en todas las plantillas (navbar)
@app.context_processor
def inyectar_carrito():
    carrito = session.get('carrito', [])
    return {'cart_count': sum(item['cantidad'] for item in carrito)}


# ============================================================
# DATOS DE SERVICIOS
# ============================================================

LISTA_SERVICIOS = [
    {"id": 1,  "titulo": "Albañilería y Remodelación",         "imagen": "servicios1.jpg",  "precio": 25},
    {"id": 2,  "titulo": "Instalación Eléctrica",              "imagen": "servicios2.jpg",  "precio": 30},
    {"id": 3,  "titulo": "Reparación de Plomería",             "imagen": "servicios3.jpg",  "precio": 20},
    {"id": 4,  "titulo": "Pintura de Interiores",              "imagen": "servicios4.jpg",  "precio": 35},
    {"id": 5,  "titulo": "Carpintería a Medida",               "imagen": "servicios5.jpg",  "precio": 40},
    {"id": 6,  "titulo": "Limpieza y Desinfección",            "imagen": "servicios6.jpg",  "precio": 15},
    {"id": 7,  "titulo": "Mantenimiento del Hogar",            "imagen": "servicios7.jpg",  "precio": 50},
    {"id": 8,  "titulo": "Instalación de Cerámica",            "imagen": "servicios8.jpg",  "precio": 28},
    {"id": 9,  "titulo": "Instalación de Aire Acondicionado",  "imagen": "servicios9.jpg",  "precio": 45},
    {"id": 10, "titulo": "Reparación de Techos",               "imagen": "servicios10.jpg", "precio": 60},
    {"id": 11, "titulo": "Impermeabilización",                 "imagen": "servicios11.jpg", "precio": 35},
    {"id": 12, "titulo": "Diseño de Jardines",                 "imagen": "servicios12.jpg", "precio": 30},
]


# ============================================================
# RUTAS PÚBLICAS
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


@app.route('/servicios')
def servicios():
    q = request.args.get('q', '').strip().lower()
    lista = LISTA_SERVICIOS
    if q:
        lista = [s for s in LISTA_SERVICIOS if q in s['titulo'].lower()]
    return render_template('servicios.html', servicios=lista)


# ============================================================
# CARRITO
# ============================================================

@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    try:
        servicio_id = int(request.form.get('id'))
    except (TypeError, ValueError):
        flash('Servicio no válido.', 'danger')
        return redirect(url_for('servicios'))

    # Tomamos título y precio del servidor, no del formulario (evita manipular precios)
    servicio = next((s for s in LISTA_SERVICIOS if s['id'] == servicio_id), None)
    if not servicio:
        flash('El servicio no existe.', 'danger')
        return redirect(url_for('servicios'))

    carrito = session.get('carrito', [])

    for item in carrito:
        if item['id'] == servicio_id:
            item['cantidad'] += 1
            break
    else:
        carrito.append({
            'id': servicio['id'],
            'titulo': servicio['titulo'],
            'precio': float(servicio['precio']),
            'cantidad': 1
        })

    session['carrito'] = carrito
    session.modified = True
    flash(f'"{servicio["titulo"]}" se agregó a tu carrito.', 'success')
    return redirect(url_for('ver_carrito'))


@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)
    iva = subtotal * IVA_TASA
    total = subtotal + iva
    return render_template('carrito.html', carrito=carrito,
                           subtotal=subtotal, iva=iva, total=total)


@app.route('/vaciar_carrito')
def vaciar_carrito():
    session.pop('carrito', None)
    flash('Carrito vaciado.', 'info')
    return redirect(url_for('ver_carrito'))


@app.route('/procesar_compra', methods=['POST'])
def procesar_compra():
    carrito = session.get('carrito', [])
    if not carrito:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('servicios'))

    tipo_doc = request.form.get('tipo_doc', '').strip()
    identificacion = request.form.get('identificacion', '').strip()
    nombre_razon = request.form.get('nombre_razon', '').strip()
    email = request.form.get('email', '').strip()
    telefono = request.form.get('telefono', '').strip()

    if not (tipo_doc and identificacion and nombre_razon and email and telefono):
        flash('Completa todos los datos de facturación.', 'danger')
        return redirect(url_for('ver_carrito'))

    subtotal = sum(i['precio'] * i['cantidad'] for i in carrito)
    iva = subtotal * IVA_TASA
    total = subtotal + iva

    # --- Guardar pedido en BD (descomenta y ajusta a tu tabla `pedidos`) ---
    # try:
    #     db = get_db()
    #     with db.cursor() as cursor:
    #         cursor.execute(
    #             """INSERT INTO pedidos
    #                (usuario_id, tipo_doc, identificacion, nombre_razon,
    #                 email, telefono, subtotal, iva, total)
    #                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    #             (session.get('user_id'), tipo_doc, identificacion, nombre_razon,
    #              email, telefono, subtotal, iva, total))
    # except pymysql.MySQLError as error:
    #     print("ERROR GUARDANDO PEDIDO:", error)
    #     flash('No se pudo registrar el pedido.', 'danger')
    #     return redirect(url_for('ver_carrito'))

    session.pop('carrito', None)

    return render_template('confirmacion.html', cliente=nombre_razon, email=email,
                           items=carrito, subtotal=subtotal, iva=iva, total=total)


# ============================================================
# LOGIN
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    usuario_input = request.form.get('usuario', '').strip()
    password_input = request.form.get('password', '')

    def responder_error(mensaje, codigo):
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), codigo
        flash(mensaje, 'danger')
        return render_template('login.html')

    if not usuario_input or not password_input:
        return responder_error('Por favor, ingresa tu usuario/correo y contraseña.', 400)

    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, apellido, email, usuario, identificacion, password_hash, rol
                FROM usuarios
                WHERE usuario = %s OR email = %s OR identificacion = %s
                LIMIT 1
            """, (usuario_input, usuario_input, usuario_input))
            usuario = cursor.fetchone()

        if not usuario:
            return responder_error('Usuario o contraseña incorrectos.', 401)

        password_hash = usuario.get('password_hash')
        if not password_hash:
            return responder_error('La cuenta no tiene una contraseña configurada correctamente.', 500)

        try:
            password_correcta = check_password_hash(password_hash, password_input)
        except Exception as error:
            print("ERROR HASH:", error)
            password_correcta = False

        if not password_correcta:
            return responder_error('Usuario o contraseña incorrectos.', 401)

        # Conservar el carrito al iniciar sesión
        carrito_previo = session.get('carrito', [])
        session.clear()
        if carrito_previo:
            session['carrito'] = carrito_previo

        session['user_id'] = usuario['id']
        session['usuario_nombre'] = usuario.get('nombre') or ''
        session['usuario_email'] = usuario.get('email') or ''
        session['usuario_rol'] = usuario.get('rol') or 'cliente'

        if es_ajax:
            return jsonify({
                "success": True,
                "message": "¡Inicio de sesión exitoso!",
                "redirect_url": url_for('perfil')
            }), 200

        flash('¡Bienvenido de nuevo!', 'success')
        return redirect(url_for('perfil'))

    except pymysql.MySQLError as error:
        print("ERROR MYSQL LOGIN:", error)
        return responder_error('No se pudo conectar con la base de datos.', 500)
    except Exception as error:
        print("ERROR LOGIN:", error)
        return responder_error('Ocurrió un error interno en el servidor.', 500)


# ============================================================
# REGISTRO
# ============================================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')

    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    tipo_doc = request.form.get('tipo_doc', '').strip()
    identificacion = request.form.get('identificacion', '').strip()
    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    email = request.form.get('email', '').strip()
    telefono = request.form.get('telefono', '').strip()
    usuario = request.form.get('usuario', '').strip()
    password_raw = request.form.get('password', '')

    def responder_error(mensaje, codigo):
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), codigo
        flash(mensaje, 'danger')
        return render_template('registro.html')

    if not (tipo_doc and identificacion and nombre and email and usuario and password_raw):
        return responder_error('Por favor, completa todos los campos obligatorios.', 400)

    filename = None
    file_antecedentes = request.files.get('antecedentes')
    if file_antecedentes and file_antecedentes.filename and archivo_permitido(file_antecedentes.filename):
        filename = secure_filename(file_antecedentes.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_antecedentes.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    password_hash = generate_password_hash(password_raw)

    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuarios
                (tipo_doc, identificacion, nombre, apellido, email, telefono,
                 usuario, password_hash, antecedentes_path, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'cliente')
            """, (tipo_doc, identificacion, nombre, apellido, email,
                  telefono, usuario, password_hash, filename))

        mensaje = 'Registro completado exitosamente. Procede al inicio de sesión.'
        if es_ajax:
            return jsonify({"success": True, "message": mensaje,
                            "redirect_url": url_for('login')}), 200
        flash(mensaje, 'success')
        return redirect(url_for('login'))

    except pymysql.MySQLError as error:
        print("ERROR MYSQL REGISTRO:", error)
        if error.args[0] == 1062:
            return responder_error('El correo, identificación o nombre de usuario ya se encuentra registrado.', 400)
        return responder_error('No se pudo guardar el usuario en la base de datos.', 500)

    except Exception as error:
        print("ERROR REGISTRO:", error)
        return responder_error('Ocurrió un error al registrar el usuario.', 500)


# ============================================================
# PERFIL Y OTROS
# ============================================================

@app.route('/crecimiento')
def crecimiento():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta sección.', 'warning')
        return redirect(url_for('login'))

    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s LIMIT 1", (session['user_id'],))
            usuario_data = cursor.fetchone()
    except Exception as error:
        print("ERROR CRECIMIENTO:", error)
        usuario_data = None

    if not usuario_data:
        session.clear()
        flash('El usuario no existe.', 'warning')
        return redirect(url_for('login'))

    return render_template('crecimiento.html', usuario=usuario_data)


@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al perfil.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    pedidos_data = []
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s LIMIT 1", (user_id,))
            usuario_data = cursor.fetchone()
            try:
                cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s", (user_id,))
                pedidos_data = cursor.fetchall()
            except Exception:
                pedidos_data = []
    except Exception as error:
        print("ERROR PERFIL:", error)
        usuario_data = None

    if not usuario_data:
        session.clear()
        flash('El usuario ya no existe.', 'warning')
        return redirect(url_for('login'))

    return render_template('perfil.html', usuario=usuario_data, pedidos=pedidos_data)


@app.route('/pedidos')
def pedidos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus pedidos.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s LIMIT 1", (user_id,))
            usuario_data = cursor.fetchone()
            cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s", (user_id,))
            lista_pedidos = cursor.fetchall()
    except Exception as error:
        print("ERROR PEDIDOS:", error)
        lista_pedidos = []
        usuario_data = None

    return render_template('pedidos.html', usuario=usuario_data, pedidos=lista_pedidos)


@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    if 'user_id' not in session:
        flash('Inicia sesión para enviar mensajes.', 'warning')
        return redirect(url_for('login'))

    flash('Mensaje enviado correctamente.', 'success')
    return redirect(request.referrer or url_for('perfil'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)