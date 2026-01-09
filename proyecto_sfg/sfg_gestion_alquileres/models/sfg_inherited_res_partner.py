from odoo import fields, models

class sfg_InheritedResPartner(models.Model):
    _inherit='res.partner'

    #RELACION 1:N ENTRE CLIENTE Y ALQUILERES DE VEHICULOS
    alquileres_ids = fields.One2many(
        'alquileres.vehiculos',
        'cliente_id',
        string='Alquileres de Vehículos'
    )