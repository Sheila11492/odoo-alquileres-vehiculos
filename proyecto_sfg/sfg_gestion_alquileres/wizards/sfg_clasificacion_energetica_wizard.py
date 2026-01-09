from odoo import models, fields, api

class sfg_clasificacion_energetica_wizard(models.TransientModel):
    _name = 'clasificacion.energetica.wizard'
    _description = 'Asistente para elegir clasificación energética'

    combustible = fields.Selection(
        [
            ('electrico_bateria', 'Eléctrico de batería'),
            ('electrico_autonomia', 'Eléctrico de autonomía extendida'),
            ('electrico_hibrido', 'Eléctrico híbrido enchufable'),
            ('hibrido_no_enchufable', 'Híbrido no enchufable'),
            ('gas', 'Gas'),
            ('gasolina_2006', 'Gasolina matriculado a partir de enero de 2006'),
            ('diesel_2015', 'Diesel matriculado a partir de septiembre de 2015'),
            ('gasolina_2001_2006', 'Gasolina matriculado entre 2001 y 2006'),
            ('diesel_2006_2015', 'Diesel matriculado entre 2006 y 2015'),
            ('otros', 'Otros'),
        ],
        string='Combustible',
        required=True
    )

    # METODOS PARA MANEJAR BOTONES
    def action_establecer_clasificacion(self):
        """ Asigna automáticamente la clasificación energética en base a la selección del usuario. """
        tipo_vehiculo_id = self.env.context.get('active_id')
        tipo_vehiculo = self.env['tipos.vehiculos'].browse(tipo_vehiculo_id)

        if not tipo_vehiculo:
            return

        clasificacion = 'sin_clasificar'
        if self.combustible in ['electrico_bateria', 'electrico_autonomia', 'electrico_hibrido']:
            clasificacion = '0'
        elif self.combustible in ['hibrido_no_enchufable', 'gas']:
            clasificacion = 'eco'
        elif self.combustible in ['gasolina_2006', 'diesel_2015']:
            clasificacion = 'c'
        elif self.combustible in ['gasolina_2001_2006', 'diesel_2006_2015']:
            clasificacion = 'b'

        tipo_vehiculo.clasificacion_energetica = clasificacion

        return {'type': 'ir.actions.act_window_close'}
