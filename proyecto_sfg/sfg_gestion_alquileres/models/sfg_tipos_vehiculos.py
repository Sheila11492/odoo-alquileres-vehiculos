from odoo import models, fields, api
from odoo.exceptions import UserError
import random


class sfg_tipos_vehiculos(models.Model):
    _name = 'tipos.vehiculos'
    _description = 'Tipos de Vehículos'
    _order = 'name asc'

    name = fields.Char(string='Nombre', required=True)
    clasificacion_energetica = fields.Selection(
        [
            ('0', '0'),
            ('eco', 'Eco'),
            ('c', 'C'),
            ('b', 'B'),
            ('sin_clasificar', 'Sin clasificar'),
        ],
        string='Clasificación Energética',
        default='sin_clasificar',
    )
    enganche_carro = fields.Boolean(string='Enganche para Carro', default=False)
    #RELACION 1:N ENTRE TIPOS_VEHICULOS Y VEHICULOS
    vehiculos_ids = fields.One2many("vehiculos", "tipo_vehiculo_id", string="Vehículos de este tipo")
    # RESTRICCIONES
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El nombre del tipo de vehículo debe ser único'),
    ]
    # METODOS PARA MANEJAR BOTONES
    @api.model
    def action_generar_tipo_vehiculo(self):
        """Genera un nuevo tipo de vehículo con valores aleatorios y muestra información."""
        numero_aleatorio = random.randint(1, 1000)
        nuevo_nombre = f"tipo_ejemplo{numero_aleatorio}"

        # Query SQL para insertar el registro
        query = """
               INSERT INTO tipos_vehiculos (name, clasificacion_energetica, enganche_carro, create_uid, create_date, write_uid, write_date)
               VALUES (%s, %s, %s, %s, NOW(), %s, NOW())
               RETURNING id, name, enganche_carro;
           """
        usuario_id = self.env.user.id
        self.env.cr.execute(query, (nuevo_nombre, 'sin_clasificar', False, usuario_id, usuario_id))
        registro_creado = self.env.cr.fetchone()

        # Confirmar la transacción para guardar el registro
        self.env.cr.commit()

        if registro_creado:
            id_tipo, nombre_tipo, enganche = registro_creado
            usuario_actual = self.env.user
            compania_actual = self.env.company
            lenguaje_actual = self.env.context.get("lang", "No definido")

            # Construcción del mensaje
            mensaje = (
                f" **Se ha creado un nuevo tipo de vehículo.**\n\n"
                f" **Datos del tipo de vehículo:**\n"
                f"- ID: {id_tipo}\n"
                f"- Nombre: {nombre_tipo}\n"
                f"- Enganche para carro: {'Sí' if enganche else 'No'}\n\n"
                f" **Datos del entorno:**\n"
                f"- Usuario: {usuario_actual.name} (ID: {usuario_actual.id})\n"
                f"- Compañía: {compania_actual.name}\n"
                f"- Lenguaje: {lenguaje_actual}"
            )

            # Lanza el UserError para mostrar la información
            raise UserError(mensaje)