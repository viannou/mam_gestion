# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date

class mam_jour_e(osv.Model):
    _name = 'mam.jour_e'
    _description = "Détail jour"
    _columns = {
        'date': fields.date('Date',required=True, help='La date'),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'frais_montant': fields.float('Montant des frais', digits=(6,2), help='Montant des frais en euros'),
        'frais_libelle': fields.char('Libellé des frais', help='Libellé des frais'),
        'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
    }
    _rec_name = 'date'
mam_jour_e()
