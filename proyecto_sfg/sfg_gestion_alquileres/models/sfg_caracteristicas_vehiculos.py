from odoo import models, fields

class sfg_caracteristicas_vehiculos(models.Model):
    _name = 'caracteristicas.vehiculos'
    _description = 'Características de Vehículos'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer('color')
    secuencia = fields.Integer('secuencia')
    # RESTRICCIONES
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El nombre de la característica del vehículo debe ser único'),
    ]