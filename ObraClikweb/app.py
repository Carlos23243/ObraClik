import os
import pymysql
from pymysql.cursors import DictCursor

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
    g
)

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# CONFIGURACIÓN DE FLASK
# ============================================================

app = Flask(__name__)
app.secret_key = 'obraclick_clave_secreta_provisoria'


# ============================================================
# CONFIGURACIÓN DE MYSQL
# ============================================================

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Astro2255'
MYSQL_DB = 'obraclick_db'  # <-- Verifica que este nombre coincida con tu base de datos
MYSQL_PORT = 3306


# ============================================================
# CONFIGURACIÓN DE ARCHIVOS
# ============================================================

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def archivo_permitido(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# CONEXIÓN A MYSQL
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
    lista_servicios = [
        {"titulo": "Albañilería y Remodelación", "imagen": "servicios1.jpg", "precio": 25},
        {"titulo": "Instalación Eléctrica", "imagen": "servicios2.jpg", "precio": 30},
        {"titulo": "Reparación de Plomería", "imagen": "servicios3.jpg", "precio": 20},
        {"titulo": "Pintura de Interiores", "imagen": "servicios4.jpg", "precio": 35},
        {"titulo": "Carpintería a Medida", "imagen": "servicios5.jpg", "precio": 40},
        {"titulo": "Limpieza y Desinfección", "imagen": "servicios6.jpg", "precio": 15},
        {"titulo": "Mantenimiento del Hogar", "imagen": "servicios7.jpg", "precio": 50},
        {"titulo": "Instalación de Cerámica", "imagen": "servicios8.jpg", "precio": 28},
        {"titulo": "Instalación de Aire Acondicionado", "imagen": "servicios9.jpg", "precio": 45},
        {"titulo": "Reparación de Techos", "imagen": "servicios10.jpg", "precio": 60},
        {"titulo": "Impermeabilización", "imagen": "servicios11.jpg", "precio": 35},
        {"titulo": "Diseño de Jardines", "imagen": "servicios12.jpg", "precio": 30}
    ]
    return render_template('servicios.html', servicios=lista_servicios)


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

    if not usuario_input or not password_input:
        mensaje = 'Por favor, ingresa tu usuario/correo y contraseña.'
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 400
        flash(mensaje, 'danger')
        return render_template('login.html')

    try:
        db = get_db()
        with db.cursor() as cursor:
            sql = """
                SELECT id, nombre, apellido, email, usuario, identificacion, password_hash, rol
                FROM usuarios
                WHERE usuario = %s OR email = %s OR identificacion = %s
                LIMIT 1
            """
            cursor.execute(sql, (usuario_input, usuario_input, usuario_input))
            usuario = cursor.fetchone()

        if not usuario:
            mensaje = 'Usuario o contraseña incorrectos.'
            if es_ajax:
                return jsonify({"success": False, "message": mensaje}), 401
            flash(mensaje, 'danger')
            return render_template('login.html')

        password_hash = usuario.get('password_hash')
        if not password_hash:
            mensaje = 'La cuenta no tiene una contraseña configurada correctamente.'
            if es_ajax:
                return jsonify({"success": False, "message": mensaje}), 500
            flash(mensaje, 'danger')
            return render_template('login.html')

        try:
            password_correcta = check_password_hash(password_hash, password_input)
        except Exception as error:
            print("ERROR HASH:", error)
            password_correcta = False

        if not password_correcta:
            mensaje = 'Usuario o contraseña incorrectos.'
            if es_ajax:
                return jsonify({"success": False, "message": mensaje}), 401
            flash(mensaje, 'danger')
            return render_template('login.html')

        session.clear()
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
        mensaje = 'No se pudo conectar con la base de datos.'
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 500
        flash(mensaje, 'danger')
        return render_template('login.html')

    except Exception as error:
        print("ERROR LOGIN:", error)
        mensaje = 'Ocurrió un error interno en el servidor.'
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 500
        flash(mensaje, 'danger')
        return render_template('login.html')


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

    if not (tipo_doc and identificacion and nombre and email and usuario and password_raw):
        mensaje = 'Por favor, completa todos los campos obligatorios.'
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 400
        flash(mensaje, 'danger')
        return render_template('registro.html')

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
            sql = """
                INSERT INTO usuarios
                (tipo_doc, identificacion, nombre, apellido, email, telefono, usuario, password_hash, antecedentes_path, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'cliente')
            """
            cursor.execute(sql, (tipo_doc, identificacion, nombre, apellido, email, telefono, usuario, password_hash, filename))

        mensaje = 'Registro completado exitosamente. Procede al inicio de sesión.'
        if es_ajax:
            return jsonify({"success": True, "message": mensaje, "redirect_url": url_for('login')}), 200

        flash(mensaje, 'success')
        return redirect(url_for('login'))

    except pymysql.MySQLError as error:
        print("ERROR MYSQL REGISTRO:", error)
        # Captura de error de duplicidad (Ej: email o identificación ya registrados)
        if error.args[0] == 1062:
            mensaje = 'El correo, identificación o nombre de usuario ya se encuentra registrado.'
        else:
            mensaje = 'No se pudo guardar el usuario en la base de datos.'

        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 400 if error.args[0] == 1062 else 500
        flash(mensaje, 'danger')
        return render_template('registro.html')

    except Exception as error:
        print("ERROR REGISTRO:", error)
        mensaje = 'Ocurrió un error al registrar el usuario.'
        if es_ajax:
            return jsonify({"success": False, "message": mensaje}), 500
        flash(mensaje, 'danger')
        return render_template('registro.html')


# ============================================================
# PERFIL Y OTROS
# ============================================================


@app.route('/crecimiento')
def crecimiento():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta sección.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s LIMIT 1", (user_id,))
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
        pedidos_data = []

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