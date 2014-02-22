# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date

class mam_enfant(osv.Model):
    _name = 'mam.enfant'
    _description = "Enfant"
    def _get_nomprenom(self, cr, uid, ids, name, args, context=None):
        """nom affichable de l'enfant """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= record.prenom + " " + record.nom
        return result
    def _get_today_info(self, cr, uid, ids, name, args, context=None):
        """toutes les infos d'aujourd'hui"""
        result = dict()
        for enfant in self.browse(cr, uid, ids, context=context):
            result[enfant.id] = dict()
            result[enfant.id]['today_presence_ids'] = list()
            for presence in enfant.presence_ids:
                if datetime.strptime(presence.date_debut,'%Y-%m-%d %H:%M:%S').date() == date.today():
                    result[enfant.id]['today_presence_ids'].append(presence.id)
        return result
    _columns = {
        'nom': fields.char('Nom',size=50,required=True, help='Nom de l''enfant'),
        'prenom': fields.char('Prénom',size=50,required=True, help='Prénom de l''enfant'),
        'nomprenom': fields.function(
            _get_nomprenom,
            type="char",
            string="Nom Complet",
            store=None,
            #select=True,
        ),
        'date_naiss': fields.date('Date de naissance',required=True, help='Date de naissance de l''enfant'),
        'am_id': fields.many2one('mam.am','Assistante maternelle de référence',required=True, help='Assistante maternelle de référence pour l''enfant'),
        'contact_ids': fields.many2many('mam.contact','mam_enfant_contact_rel','contact_id','enfant_id',string="Contacts"),
        'allergies': fields.text('Allergies', help='Allergies de l''enfant'),
        'recommandations': fields.text('Recommandations générales', help='Recommandations générales pour l''enfant'),
        'presence_ids': fields.one2many('mam.presence_e', 'enfant_id', 'Liste des présences', help='Liste des présences de l''enfant'),
        'today_presence_ids': fields.function(
            _get_today_info,
            string="Présences aujourd'hui",
            type="one2many",
            obj="mam.presence_e",
            field="enfant_id",
            multi=True,
        ),
    }
    _rec_name = 'nomprenom'
mam_enfant()
