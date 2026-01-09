from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class sfg_vehiculos(models.Model):
    _name = 'vehiculos'
    _description = 'Modelo para gestionar vehículos'
    _order = 'codigo asc'

    name = fields.Char(string='Nombre', required=True)
    codigo = fields.Char(
        string='Código',
        required=True,
        default=lambda self: f"{self.env.user.id}-{datetime.now().strftime('%d%m%Y')}",
        copy=False
    )
    matricula = fields.Char(string='Matrícula', required=True)
    potencia = fields.Integer(string='Potencia', default=100)
    num_plazas = fields.Integer(string='Número de Plazas', default=5)
    fecha_fabricacion = fields.Date(string='Fecha de Fabricación')
    combustible = fields.Selection(
        [
            ('gasolina', 'Gasolina'),
            ('diesel', 'Diésel'),
            ('gas', 'Gas'),
            ('hibrido', 'Híbrido'),
            ('electrico', 'Eléctrico')
        ],
        string='Combustible'
    )
    fecha_itv = fields.Date(
        string='Fecha de ITV',
        default=lambda self: (datetime.now() + timedelta(days=6 * 365)).strftime('%Y-%m-%d'),
        copy=False
    )
    neumatico = fields.Char(string='Neumático')
    maletero = fields.Boolean(string='Maletero')
    capacidad_maletero = fields.Float(string='Capacidad del Maletero', default=0)
    precio_diario = fields.Float(string='Precio Diario')
    precio_semanal = fields.Float(
        string='Precio Semanal',
        compute='_compute_precio_semanal',
        readonly=True
    )
    numero_alquileres = fields.Integer(
        string='Número de Alquileres',
        compute='_compute_numero_alquileres',
        readonly=True
    )
    state = fields.Selection(
        [
            ('disponible', 'Disponible'),
            ('alquilado', 'Alquilado'),
            ('reparacion', 'En Reparación')
        ],
        string='Estado',
        required=True,
        default='disponible',
        readonly=True
    )

    #RELACION N:1 ENTRE VEHICULOS Y TIPOS_VEHICULOS
    tipo_vehiculo_id = fields.Many2one(
        'tipos.vehiculos',
        string='Tipo de Vehículo',
        required=True
    )
    # RELACION N:N ENTRE VEHICULOS Y CARACTERISTICAS_VEHICULOS
    caracteristicas_ids = fields.Many2many(
        'caracteristicas.vehiculos',
        'vehiculo_caracteristica_rel',
        'vehiculo_id', 'caracteristica_id',
        string='Características'
    )
    # RELACION 1:N ENTRE VEHICULOS Y ALQUILERES_VEHICULOS
    alquiler_ids = fields.One2many(
        'alquileres.vehiculos',
        'vehiculo_id',
        string='Alquileres'
    )

    # METODOS ONCHANGE
    # SI EL CAMPO MALETERO ESTA ACTIVADO ESTABLECE EL VALOR DE 300
    # SI ESTA DESACTIVADO EL VALOR ES 0

    @api.onchange('maletero')
    def _onchange_maletero(self):
        if self.maletero:
            self.capacidad_maletero = 300
        else:
            self.capacidad_maletero = 0

    #RESTRICCIONES PYTHON
    #SI SE ESTABLECE QUE TIENE MALETERO ES OBLIGATORIO ESPECIFICAR LA CAPACIDAD
    @api.constrains('maletero', 'capacidad_maletero')
    def _check_capacidad_maletero(self):
        for record in self:
            if record.maletero and not record.capacidad_maletero:
                raise ValidationError("Debe especificar la capacidad del maletero si el vehículo tiene maletero.")

    # MÉTODOS DE CAMPOS CALCULADOS
    @api.depends('precio_diario')
    def _compute_precio_semanal(self):
        for record in self:
            record.precio_semanal = record.precio_diario * 5 if record.precio_diario else 0.0

    @api.depends('alquiler_ids')  
    def _compute_numero_alquileres(self):
        for record in self:
            record.numero_alquileres = len(record.alquiler_ids)

    # RESTRICCIONES
    _sql_constraints = [
        ('numero_plazas_gt_zero', 'CHECK(num_plazas > 0)', 'El número de plazas debe ser mayor que cero'),
        ('potencia_gt_zero', 'CHECK(potencia > 0)', 'La potencia debe ser mayor que cero'),
        ('precio_diario_gt_zero', 'CHECK(precio_diario > 0)', 'El precio diario debe ser mayor que cero'),
    ]

    # METODOS PARA MANEJAR BOTONES
    def action_comenzar_reparacion(self):
        for record in self:
            if record.state == 'disponible':
                record.state = 'reparacion'
            else:
                error_message = ''
                if record.state == 'alquilado':
                    error_message = 'El vehículo está alquilado y no se puede poner en reparación.'
                elif record.state == 'reparacion':
                    error_message = 'El vehículo ya está en reparación.'
                raise ValidationError(error_message)

    def action_terminar_reparacion(self):
        for record in self:
            if record.state == 'reparacion':
                record.state = 'disponible'
            else:
                error_message = ''
                if record.state == 'disponible':
                    error_message = 'El vehículo no está en reparación.'
                elif record.state == 'alquilado':
                    error_message = 'El vehículo está alquilado y no se puede terminar la reparación.'
                raise ValidationError(error_message)

    def action_ver_modificar_recordset(self):
        """ Muestra información de los vehículos seleccionados y modifica la propiedad 'maletero'. """
        if not self:
            raise UserError("No hay vehículos seleccionados.")

        # Recopilamos la información en una cadena
        info = "Información de los vehículos seleccionados:\n\n"

        # Variables para cálculos globales
        total_alquileres = 0
        total_precio = 0
        num_vehiculos = len(self)

        for vehiculo in self:
            info += f"Vehículo: {vehiculo.name}\n"
            info += f"  - Matrícula: {vehiculo.matricula or 'N/A'}\n"
            info += f"  - Fecha de Fabricación: {vehiculo.fecha_fabricacion or 'N/A'}\n"
            info += f"  - Fecha ITV: {vehiculo.fecha_itv or 'N/A'}\n"

            # Información del tipo de vehículo
            if vehiculo.tipo_vehiculo_id:
                info += f"  - Tipo de Vehículo: {vehiculo.tipo_vehiculo_id.name}\n"
                info += f"  - Clasificación Energética: {vehiculo.tipo_vehiculo_id.clasificacion_energetica or 'Sin clasificar'}\n"

            # Acumulamos valores para cálculos globales
            total_alquileres += vehiculo.numero_alquileres
            total_precio += vehiculo.precio_diario

        # Cálculo de la media del precio diario
        media_precio_diario = total_precio / num_vehiculos if num_vehiculos > 0 else 0

        # Agregar información general
        info += f"\nTotal número de alquileres: {total_alquileres}\n"
        info += f"Media de precio diario: {media_precio_diario:.2f} €\n"

        # Modificar el campo "maletero" para todos los vehículos seleccionados
        self.write({'maletero': False})

        # Mostrar la información en una ventana emergente
        raise UserError(info)