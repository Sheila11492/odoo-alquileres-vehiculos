from odoo import models, fields, Command
from datetime import date

class sfg_inherited_alquileres(models.Model):
    _inherit = "alquileres.vehiculos"  # Heredamos del modelo de alquileres de vehículos

    # Método que se sobrescribe para crear la factura cuando se pulsa el botón "Facturar alquiler"
    def action_facturar_alquiler(self):
        for record in self:
            # Crear la factura
            factura = self.env["account.move"].create(
                {
                    "partner_id": record.cliente_id,  # Cliente relacionado con el alquiler
                    "move_type": "out_invoice",  # Tipo de factura (venta)
                    "journal_id": 1,  # Diario de contabilidad
                    "invoice_date": fields.Date.today(),  # Fecha de la factura (hoy)
                    "invoice_line_ids": [
                        Command.create({
                            "name": f"{record.vehiculo_id.name} ({record.vehiculo_id.codigo}) - {record.duracion} días alquilados",
                            "quantity": 1,
                            "price_unit": record.precio_final,  # Precio total del alquiler
                        }),
                        Command.create({
                            "name": "Gastos del seguro obligatorio",
                            "quantity": 1,
                            "price_unit": 20,  # Costo del seguro
                        }),
                    ],
                }
            )
        return super().action_facturar_alquiler()