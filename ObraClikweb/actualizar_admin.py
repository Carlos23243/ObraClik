import pymysql

# Hash real generado por Werkzeug para la contraseña 'admin123'
NUEVO_HASH = 'scrypt:32768:8:1$79xzTfE5TneVYrws$31cce11382c90aab03f1db5397b3e8373464af7ed5fde6e8ceae1c5d76e85ea3d15482048d5f1420026a15336dff8340ce3fbde6d125edeaf2f82f0a9aa7781d'

try:
    conexion = pymysql.connect(
        host='localhost',
        user='root',
        password='Astro2255',
        database='obraclick_db',  # Si tu DB se llama 'obraclick', cambia esta línea
        port=3306
    )

    with conexion.cursor() as cursor:
        sql = "UPDATE usuarios SET password_hash = %s WHERE email = %s OR usuario = %s"
        filas_afectadas = cursor.execute(sql, (NUEVO_HASH, 'admin@obraclick.ec', 'admin'))
        conexion.commit()

        if filas_afectadas > 0:
            print("✅ El hash del Administrador se actualizó correctamente en MySQL.")
        else:
            print("⚠️ No se encontró ningún usuario con email 'admin@obraclick.ec' o usuario 'admin'.")

except Exception as e:
    print("❌ Error al actualizar en la base de datos:", e)

finally:
    if 'conexion' in locals() and conexion.open:
        conexion.close()