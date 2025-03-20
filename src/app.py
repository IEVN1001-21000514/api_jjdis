from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config

app = Flask(__name__)
CORS(app)
app.config.from_object(config['development'])
con = MySQL(app)

# 📌 Obtener los sliders disponibles
@app.route("/obtenerSliders", methods=['GET'])
def obtener_sliders():
    try:
        cursor = con.connection.cursor()
        cursor.execute("SELECT id_sliders, nombreSlider FROM sliders")
        sliders = cursor.fetchall()
# Agregar un mensaje de registro para verificar los sliders obtenidos
        print("Sliders obtenidos:", sliders)

        return jsonify([{'id': s[0], 'value': s[1]} for s in sliders])
    except Exception as ex:
        return jsonify({'mensaje': f'Error al obtener sliders: {str(ex)}', 'exito': False})

# 📌 Guardar un registro en la tabla registroPedido
@app.route("/guardarRegistroPedido", methods=['POST'])
def guardar_registro_pedido():
    try:
        data = request.get_json()
        cursor = con.connection.cursor()
        sql = """INSERT INTO registroPedido (id_slider, secuencia, cantidad, estado) 
                 VALUES (%s, %s, %s, 'pendiente')"""  # Estado por defecto "pendiente"
        cursor.execute(sql, (data['id_slider'], data['secuencia'], data['cantidad']))
        con.connection.commit()
        return jsonify({'mensaje': 'Registro guardado correctamente', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f'Error al guardar el registro: {str(ex)}', 'exito': False})

# 📌 Obtener los registros de pedido
@app.route("/obtenerRegistroPedidos", methods=['GET'])
def obtener_registro_pedidos():
    try:
        cursor = con.connection.cursor()
        cursor.execute("SELECT id_registroPedido, id_slider, secuencia, cantidad FROM registroPedido WHERE estado = 'pendiente'")
        registros = cursor.fetchall()
        return jsonify([
            {'id_registroPedido': r[0], 'id_slider': r[1], 'secuencia': r[2], 'cantidad': r[3]}
            for r in registros
        ])
    except Exception as ex:
        return jsonify({'mensaje': f'Error al obtener los registros: {str(ex)}', 'exito': False})

# 📌 Eliminar un registro de la tabla registroPedido
@app.route("/eliminarRegistroPedido/<int:id_registroPedido>", methods=['DELETE'])
def eliminar_registro_pedido(id_registroPedido):
    try:
        cursor = con.connection.cursor()
        cursor.execute("DELETE FROM registroPedido WHERE id_registroPedido = %s", (id_registroPedido,))
        con.connection.commit()
        return jsonify({'mensaje': 'Registro eliminado correctamente', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f'Error al eliminar el registro: {str(ex)}', 'exito': False})

# 📌 Finalizar pedido y guardar en la tabla pedido
@app.route("/crearPedido", methods=['POST'])
def crear_pedido():
    try:
        cursor = con.connection.cursor()

        # Obtener el último numero_pedido y aumentar en 1
        cursor.execute("SELECT IFNULL(MAX(numero_pedido), 0) + 1 FROM pedido")
        nuevo_numero_pedido = cursor.fetchone()[0]

        # Obtener todos los registros de registroPedido que no han sido asignados
        cursor.execute("SELECT id_registroPedido FROM registroPedido WHERE estado IS NULL OR estado != 'asignado'")
        registros = cursor.fetchall()

        if not registros:
            return jsonify({'mensaje': 'No hay registros disponibles para generar un pedido', 'exito': False})

        # Insertar cada registro con el mismo numero_pedido y actualizar su estado a "asignado"
        sql_insert = """INSERT INTO pedido (numero_pedido, id_registroPedido, fecha_registro) 
                        VALUES (%s, %s, NOW())"""
        sql_update = """UPDATE registroPedido SET estado = 'asignado' WHERE id_registroPedido = %s"""
        
        for r in registros:
            cursor.execute(sql_insert, (nuevo_numero_pedido, r[0]))
            cursor.execute(sql_update, (r[0],))  # Actualizar estado

        con.connection.commit()

        return jsonify({'mensaje': 'Pedido creado correctamente', 'numero_pedido': nuevo_numero_pedido, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f'Error al crear el pedido: {str(ex)}', 'exito': False})



# 📌 Obtener los pedidos detallados con sliders, cantidad y secuencia
@app.route("/obtenerPedidosDetallados", methods=['GET'])
def obtener_pedidos_detallados():
    try:
        cursor = con.connection.cursor()
        sql = """
            SELECT p.numero_pedido, s.nombreSlider, r.cantidad, r.secuencia 
            FROM pedido p
            JOIN registroPedido r ON p.id_registroPedido = r.id_registroPedido
            JOIN sliders s ON r.id_slider = s.id_sliders
            ORDER BY p.numero_pedido DESC;
        """
        cursor.execute(sql)
        pedidos = cursor.fetchall()

        resultado = {}
        for pedido in pedidos:
            numero_pedido, nombre_slider, cantidad, secuencia = pedido
            if numero_pedido not in resultado:
                resultado[numero_pedido] = []
            resultado[numero_pedido].append({
                'nombre_slider': nombre_slider,
                'cantidad': cantidad,
                'secuencia': secuencia
            })

        return jsonify({'pedidos': resultado, 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f'Error al obtener pedidos detallados: {str(ex)}', 'exito': False})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
