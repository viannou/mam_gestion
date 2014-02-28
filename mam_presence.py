# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date,timedelta
import re

def verif_heures(hdebut, hfin):
    try:
        matchObj = re.match( r"^(\d{1,2})[ -_.:;'hH]?(\d{1,2})[mM]?$", hdebut)
        if matchObj:
            hdebut = "{:%H:%M}".format(datetime.strptime(matchObj.group(1)+":"+matchObj.group(2),"%H:%M"))
        else:
            return False
        if hfin == "" :
            return [hdebut,""]
        matchObj = re.match( r"^(\d{1,2})[ -_.:;'hH]?(\d{1,2})[mM]?$", hfin)
        if matchObj:
            hfin = "{:%H:%M}".format(datetime.strptime(matchObj.group(1)+":"+matchObj.group(2),"%H:%M"))
        else:
            return False
        return [hdebut,hfin]
    except:
        return False


class mam_jour_e(osv.Model):
    _name = 'mam.jour_e'
    _description = "Detail jour"
    STATE_SELECTION = [
        ('encours', 'En cours'),
        ('valide', 'Valide'),
        ('cloture', 'Cloture'),
    ]
    _columns = {
        'jour': fields.date('Jour',required=True, help='La date'),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'frais_montant': fields.float('Montant des frais', digits=(6,2), help='Montant des frais en euros'),
        'frais_libelle': fields.char('Libellé des frais', help='Libellé des frais'),
        'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
        'state': fields.selection(STATE_SELECTION, 'Statut',required=True,  help='Le statut de la journée pour l''enfant'),
    }
    _defaults = {
        'enfant_id': lambda self,cr,uid,context: context.get('enfant_id', 0), 
        'mange_midi': False,
        'mange_gouter': False,
        'state': 'encours',
    }
    _rec_name = 'jour'
    _order = "jour"
mam_jour_e()

# class mam_presence_e(osv.Model):
    # _name = 'mam.presence_e'
    # _description = "Detail presence"
    # _columns = {
        # 'jour_e_id': fields.many2one('mam.jour_e','Jour',required=True, help='Jour concerne par la presence'),
        # 'heure_debut': fields.datetime('Heure debut',required=True, help='L heure de debut'),
        # 'heure_fin': fields.datetime('Heure fin',required=True, help='L heure de fin'),
# # ajouter le type de présence
    # }
    # # _rec_name = 'jour'
# mam_presence_e()

class mam_jour_type(osv.Model):
    _name = 'mam.jour_type'
    _description = "Jours type de presence"
    def _get_creneaux(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            res = []
            for presence_type in record.presence_type_ids:
                if presence_type.libelle:
                    res.append(presence_type.libelle)
            result[record.id] = "\n+  ".join(res)
        return result
    _columns = {
        'libelle': fields.function(
            _get_creneaux,
            type="char",
            string="Créneaux",
            store=None,
            # store={'mam.jour_type': (lambda self, cr, uid, ids, c={}: ids, ["presence_type_ids"], 10),},
        ),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'presence_type_ids': fields.one2many('mam.presence_type', 'jour_type_id', 'Liste des présences du jour type', help='Liste des présences du jour type de l''enfant'),
    }
    _rec_name = 'libelle'
mam_jour_type()

class mam_presence_type(osv.Model):
    _name = 'mam.presence_type'
    _description = "Presence type"
    _rec_name = 'libelle'
    def _get_lib_date(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {}
            result[record.id]['libelle'] = record.heure_debut + " - " + record.heure_fin
        return result
    def on_change_heure(self, cr, uid, ids, heure_debut, heure_fin, context=None):
        res = verif_heures(heure_debut, heure_fin)
        if res:
            return {'value': {'heure_debut':res[0],'heure_fin':res[1]}}
        return {'value':{},'warning':{'title':'Erreur','message':'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10'}}
    _columns = {
        'jour_type_id': fields.many2one('mam.jour_type','Jour type',required=True, help='Jour type concerné par la présence'),
        'heure_debut': fields.char('Heure début',required=True, help='Heure de début'),
        'heure_fin': fields.char('Heure fin', help='Heure de fin'),
        "libelle": fields.function(
            _get_lib_date,
            type="char",
            string="Créneau",
            store=None,
            multi='modif_date',
        ),
    }
    def check_heures(self, cr, uid, ids, context=None):
        reads = self.read(cr, uid, ids, ['heure_debut', 'heure_fin'], context=context)
        for records in reads:
            if not verif_heures(records['heure_debut'],records['heure_fin']):
                return False
        return True
    _constraints = [(check_heures, 'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10', ['heure_debut', 'heure_fin']),]
mam_presence_type()

