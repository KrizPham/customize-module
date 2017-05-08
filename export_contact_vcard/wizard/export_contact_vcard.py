# -*- coding: utf-8 -*-
import base64
import cStringIO
import contextlib
import csv


from odoo import api, fields, models


class ExportContact(models.TransientModel):
    _name = 'export.contact.wizard'

    name = fields.Char(string="File Name", readonly=True)
    data = fields.Binary(string="File", readonly=True)
    contact_id = fields.Many2one('res.partner', string="Contact", required=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    @api.multi
    def do_export2(self):
        if self.contact_id:
            contacts = self.env['res.partner'].search([('id', '=', self.contact_id.id)], limit=1)
            with contextlib.closing(cStringIO.StringIO()) as buf:

                writer = csv.writer(buf, delimiter=" ", quotechar='"')
                writer.writerow(("BEGIN VCARD", ""))
                writer.writerow(("VERSION:3.0", ""))
                for item in contacts:
                    writer.writerow(("FULL NAME:", item.name if item.name else ''))
                    writer.writerow(("ORG:", item.parent_id.name if item.parent_id.name else ''))
                    writer.writerow(("TITLE:", item.function if item.function else ''))
                    writer.writerow(("TEL;TYPE=WORK,VOICE:", item.phone if item.phone else ''))
                    writer.writerow(("TEL;TYPE=HOME,VOICE:", item.mobile if item.mobile else ''))
                    writer.writerow(("ADR;TYPE=HOME:", item.street if item.street else '', item.city if item.city else '', item.country_id.name if item.country_id.name else ''))
                    writer.writerow(("EMAIL:", item.email if item.email else ''))

                writer.writerow(("END:", "VCARD"))
                out = base64.encodestring(buf.getvalue())
            self.write({
                'state': 'get',
                'data': out,
                'name': 'contact_info.vcf'
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'export.contact.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
