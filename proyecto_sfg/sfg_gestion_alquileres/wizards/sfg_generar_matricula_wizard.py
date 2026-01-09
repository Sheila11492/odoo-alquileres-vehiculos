from odoo import models, fields, api
from odoo.exceptions import ValidationError


class sfg_generar_matricula_wizard(models.TransientModel):
    _name = 'generar.matricula.wizard'
    _description = 'Asistente para generar la matrícula de un vehículo'

    numero_matricula = fields.Char(string="Número de Matrícula", required=True, size=4)
    letras_matricula = fields.Char(string="Letras de Matrícula", required=True, size=3)

    # METODOS PARA MANEJAR BOTONES
    def action_generar_matricula(self):
        """ Genera la matrícula concatenando número y letras, y la asigna al vehículo. """
        if not self.numero_matricula.isdigit() or not self.letras_matricula.isalpha():
            raise ValidationError("El número debe contener solo dígitos y las letras solo caracteres alfabéticos.")

        nueva_matricula = f"{self.numero_matricula.upper()}-{self.letras_matricula.upper()}"
        vehiculo_id = self.env.context.get('active_id')
        vehiculo = self.env['vehiculos'].browse(vehiculo_id)

        if vehiculo:
            vehiculo.matricula = nueva_matricula
        return {'type': 'ir.actions.act_window_close'}
