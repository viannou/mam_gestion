# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date

class mam_jour_e(osv.Model):
    _name = 'mam.jour_e'
    _description = "Detail jour"
    _columns = {
        'jour': fields.date('Jour',required=True, help='La date'),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'frais_montant': fields.float('Montant des frais', digits=(6,2), help='Montant des frais en euros'),
        'frais_libelle': fields.char('Libellé des frais', help='Libellé des frais'),
        'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
    }
    _rec_name = 'jour'
mam_jour_e()

class mam_jour_type(osv.Model):
    _name = 'mam.jour_type'
    _description = "Jours type de presence"
    def _get_creneaux(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            res = []
            for presence_type in record.presence_type_ids:
                res.append(presence_type.name)
                print "a ",presence_type.name
            print "b ",res
            result[record.id] = "\n".join(res)
        return result
    _columns = {
        'name': fields.function(
            _get_creneaux,
            type="char",
            string="Créneaux",
            store={'mam.jour_type': (lambda self, cr, uid, ids, c={}: ids, ["presence_type_ids"], 10),},
        ),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'presence_type_ids': fields.one2many('mam.presence_type', 'jour_type_id', 'Liste des présences du jour type', help='Liste des présences du jour type de l''enfant'),
    }
mam_jour_type()

class mam_presence_type(osv.Model):
    _name = 'mam.presence_type'
    _description = "Jours type de presence"
    def _get_lib_date(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {}
            result[record.id]['heure_debut'] = datetime.strptime(record.heure_debut_c.replace("h",":").replace(" ",":"),"%H:%M")
            result[record.id]['heure_fin'] = datetime.strptime(record.heure_fin_c.replace("h",":").replace(" ",":"),"%H:%M")
            result[record.id]['name'] = "{:%H:%M}".format(result[record.id]['heure_debut']) + " - " + "{:%H:%M}".format(result[record.id]['heure_fin'])
        return result
    _columns = {
        'jour_type_id': fields.many2one('mam.jour_type','Jour type',required=True, help='Jour type concerné par la présence'),
        'heure_debut_c': fields.char('Heure début',required=True, help='Heure de début'),
        'heure_fin_c': fields.char('Heure fin',required=True, help='Heure de fin'),
        "heure_debut": fields.function(
            _get_lib_date,
            type="datetime",
            string="Heure début non affiche",
            store={'mam.presence_type': (lambda self, cr, uid, ids, c={}: ids, ["heure_debut_c", "heure_fin_c"], 5),
                'mam.jour_type': (lambda self, cr, uid, ids, c={}: ids, ["presence_type_ids"], 5),},
            multi='modif_date',
        ),
        "heure_fin": fields.function(
            _get_lib_date,
            type="datetime",
            string="Heure fin non affiche",
            store={'mam.presence_type': (lambda self, cr, uid, ids, c={}: ids, ["heure_debut_c", "heure_fin_c"], 5),
                'mam.jour_type': (lambda self, cr, uid, ids, c={}: ids, ["presence_type_ids"], 5),},
            multi='modif_date',
        ),
        "name": fields.function(
            _get_lib_date,
            type="char",
            string="Créneau",
            store={'mam.presence_type': (lambda self, cr, uid, ids, c={}: ids, ["heure_debut_c", "heure_fin_c"], 5),
                'mam.jour_type': (lambda self, cr, uid, ids, c={}: ids, ["presence_type_ids"], 5),},
            multi='modif_date',
        ),
    }
mam_presence_type()

