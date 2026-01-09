from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError
from datetime import date


class sfg_alquileres_vehiculos(models.Model):
    _name = 'alquileres.vehiculos'
    _description = 'Alquileres de Vehículos'

    fecha_inicio = fields.Date(
        string='Fecha de Inicio',
        default=lambda self: fields.Date.today(),
        required=True
    )
    fecha_fin = fields.Date(
        string='Fecha de Fin',
        compute='_compute_fecha_fin',
        inverse='_inverse_fecha_fin',  # Este método se ejecutará cuando se cambie fecha_fin
    )
    duracion = fields.Integer(
        string='Duración en Días',
        compute='_compute_duracion',
        inverse='_inverse_duracion',  # Este método se ejecutará cuando se cambie duracion
        store=True
    )
    precio_final = fields.Float(
        string='Precio Final',
        compute='_compute_precio_final',
    )
    state = fields.Selection(
        [('previo', 'Previo'), ('en_proceso', 'En Proceso'), ('terminado', 'Terminado'),
         ('facturado', 'Facturado'), ('cancelado', 'Cancelado')],
        string='Estado',
        required=True,
        default='previo'
    )
    #RELACION 1:N ENTRE VEHICULOS Y ALQUILERES_VEHICULOS
    vehiculo_id = fields.Many2one('vehiculos', string='Vehículo', required=True)
    #Relacion N:1 entre alquiler_vehiculos y “res.users” (para controlar qué usuario gestiona el alquiler).
    usuario_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    #Relacion N:1 entre alquiler_vehiculos y “res.partner” (para controlar qué cliente alquila).
    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True, )

    # MÉTODOS DE CAMPOS CALCULADOS
    @api.depends('fecha_inicio', 'duracion')
    def _compute_fecha_fin(self):
        for record in self:
            if record.fecha_inicio and record.duracion:
                record.fecha_fin = record.fecha_inicio + timedelta(days=record.duracion)

    @api.depends('fecha_inicio', 'fecha_fin')
    def _compute_duracion(self):
        for record in self:
            if record.fecha_inicio and record.fecha_fin:
                delta = fields.Date.from_string(record.fecha_fin) - fields.Date.from_string(record.fecha_inicio)
                record.duracion = delta.days

    @api.depends('duracion', 'vehiculo_id.precio_diario')
    def _compute_precio_final(self):
        for record in self:
            if record.duracion and record.vehiculo_id.precio_diario:
                record.precio_final = record.duracion * record.vehiculo_id.precio_diario

    # RESTRICCIONES PYTHON
    @api.constrains('vehiculo_id', 'cliente_id', 'usuario_id', 'fecha_inicio', 'fecha_fin', 'precio_final')
    def _check_validacion_alquiler(self):
        for alquiler in self:
            # Validar que todos los campos necesarios estén presentes
            if not alquiler.vehiculo_id or not alquiler.cliente_id or not alquiler.usuario_id or not alquiler.fecha_inicio or not alquiler.fecha_fin or not alquiler.precio_final:
                raise ValidationError(
                    'Debe completar todos los campos: vehículo, cliente, usuario, fecha inicio, fecha fin y precio final.')

            # Validar que no haya alquileres en las fechas solicitadas (si no están cancelados)
            alquileres_existentes = self.env['alquileres.vehiculos'].search([
                ('vehiculo_id', '=', alquiler.vehiculo_id.id),
                ('state', 'not in', ['cancelado']),
                ('fecha_inicio', '<=', alquiler.fecha_fin),
                ('fecha_fin', '>=', alquiler.fecha_inicio),
                ('id', '!=', alquiler.id)  # Excluir el alquiler actual (en caso de edición)
            ])
            if alquileres_existentes:
                raise ValidationError('El vehículo ya está alquilado en las fechas solicitadas.')

            # Validar que el vehículo esté en estado "disponible"
            if alquiler.vehiculo_id.state != 'disponible':
                raise ValidationError('El vehículo debe estar en estado "disponible" para realizar el alquiler.')

    def _verificar_estado_vehiculo(self, vehiculo):
        if vehiculo.state != 'disponible':
            raise ValidationError('El vehículo debe estar en estado "disponible" para realizar el alquiler.')

        return super(sfg_alquileres_vehiculos, self).create(values)

    def write(self, values):
        # Verificar y actualizar el estado del vehículo cuando se actualiza el alquiler
        if 'vehiculo_id' in values:
            vehiculo = self.env['vehiculos'].browse(values['vehiculo_id'])
            if vehiculo.state != 'disponible':
                raise ValidationError('El vehículo debe estar en estado "disponible" para realizar el alquiler.')
            # Cambiar estado del vehículo a "alquilado"
            vehiculo.write({'state': 'alquilado'})

        return super(sfg_alquileres_vehiculos, self).write(values)

    # Método inverso para actualizar la fecha de fin cuando se cambia la duración
    def _inverse_duracion(self):
        for record in self:
            if record.fecha_inicio and record.duracion:
                record.fecha_fin = record.fecha_inicio + timedelta(days=record.duracion)

    # Método inverso para actualizar la duración cuando se cambia la fecha de fin
    def _inverse_fecha_fin(self):
        for record in self:
            if record.fecha_inicio and record.fecha_fin:
                delta = fields.Date.from_string(record.fecha_fin) - fields.Date.from_string(record.fecha_inicio)
                record.duracion = delta.days
        # METODOS PARA MANEJAR BOTONES
        # Método para comprobar alquileres
    def action_comprobar_alquileres(self):
            today = date.today()
            for record in self:
                if record.state not in ['facturado', 'cancelado']:
                    if today < record.fecha_inicio:
                        record.state = 'previo'
                    elif record.fecha_inicio <= today <= record.fecha_fin:
                        record.state = 'en_proceso'
                    elif today > record.fecha_fin:
                        record.state = 'terminado'

    def action_comprobar_alquiler_individual(self):
        today = date.today()
        # Este método se ejecuta solo para el alquiler específico
        for alquiler in self:
            if alquiler.state not in ['facturado', 'cancelado']:  # No se revisan estos estados
                if alquiler.fecha_inicio > today:
                    alquiler.state = 'previo'
                elif alquiler.fecha_inicio <= today <= alquiler.fecha_fin:
                    alquiler.state = 'en_proceso'
                elif alquiler.fecha_fin < today:
                    alquiler.state = 'terminado'
        return True

    def action_facturar_alquiler(self):
        for alquiler in self:
            if alquiler.state == 'terminado':
                alquiler.state = 'facturado'
            else:
                raise ValidationError('Solo puedes facturar alquileres que estén terminados.')

    def action_terminar_alquiler(self):
        for alquiler in self:
            if alquiler.state == 'en_proceso':
                # Actualiza el precio final y otros campos
                alquiler.state = 'terminado'
                alquiler.vehiculo_id.state = 'disponible'
            else:
                raise ValidationError('El alquiler debe estar en proceso para terminarlo.')

    def action_cancelar_alquiler(self):
        for alquiler in self:
            if alquiler.state in ['previo', 'en_proceso']:
                alquiler.state = 'cancelado'
                alquiler.vehiculo_id.state = 'disponible'
            else:
                raise ValidationError('No puedes cancelar un alquiler que ya está terminado o facturado.')