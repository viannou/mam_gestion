# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date,timedelta
import re
import mam_tools
import logging

_logger = logging.getLogger("presence ::::")

class mam_jour_e(osv.Model):
    _name = 'mam.jour_e'
    _description = "Detail jour"
    def _filter_jour_presence_e(self, cr, uid, ids, context=None):
        """helper function appelé par le store triggerpour savoir quel jour doit être recalculé si une présence a changée
        """
        result = dict()
        presence_e_ids = self.pool.get('mam.presence_e').browse(
            cr, uid, ids, context=context
        )
        for presence_e in presence_e_ids:
            if presence_e.jour_e_id:
                result[presence_e.jour_e_id.id] = True
        return result.keys()
    def _filter_jour_presence_prevue(self, cr, uid, ids, context=None):
        """helper function appelé par le store triggerpour savoir quel jour doit être recalculé si une présence a changée
        """
        result = dict()
        presence_prevue_ids = self.pool.get('mam.presence_prevue').browse(
            cr, uid, ids, context=context
        )
        for presence_prevue in presence_prevue_ids:
            if presence_prevue.jour_e_id:
                result[presence_prevue.jour_e_id.id] = True
        return result.keys()

    def _get_libelle_prevue(self, cr, uid, ids, name, args, context=None):
        """nom affichable des horaires pevues """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            res = []
            for presence_prevue in record.presence_prevue_ids:
                if presence_prevue.libelle:
                    res.append(presence_prevue.libelle)
            result[record.id] = "\n+  ".join(res)
        return result
    def _get_libelle_reel(self, cr, uid, ids, name, args, context=None):
        """nom affichable des horaires pevues """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            res = []
            for presence_e in record.presence_e_ids:
                if presence_e.libelle:
                    res.append(presence_e.libelle)
            result[record.id] = "\n+  ".join(res)
        return result
    def _get_minutes(self, cr, uid, ids, name, args, context=None):
        """minutes bilan de la journée """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            print "* calcul minutes jour ", record.id,
            liste = []
            # on crée une liste au format (heure,type,est_debut)
            for prevu in record.presence_prevue_ids: # p = prévu
                liste += [(mam_tools.conv_str2minutes(prevu.heure_debut),'p',True), (mam_tools.conv_str2minutes(prevu.heure_fin),'p',False)]
            for reel in record.presence_e_ids:
                if reel.type in [u'normal']: # r = réel
                    liste += [(mam_tools.conv_str2minutes(reel.heure_debut),'r',True), (mam_tools.conv_str2minutes(reel.heure_fin),'r',False)]
                if reel.type in [u'malade',u'cause_am']: # e = excusé
                    liste += [(mam_tools.conv_str2minutes(reel.heure_debut),'e',True), (mam_tools.conv_str2minutes(reel.heure_fin),'e',False)]
                if reel.type in [u'abus',u'absent']: # a = abus
                    liste += [(mam_tools.conv_str2minutes(reel.heure_debut),'a',True), (mam_tools.conv_str2minutes(reel.heure_fin),'a',False)]
            liste.sort()
            # print liste
            
            hdebut = 0
            est_prevu = est_present = est_excuse = est_abus = False
            m_pres_prev = m_pres_imprev = m_absent = m_excuse = 0
            for (heure,type,est_debut) in liste:
                # print (heure,type,est_debut)
                delta = heure - hdebut
                if est_prevu and est_present:
                    m_pres_prev += delta
                if est_prevu and est_excuse:
                    m_excuse += delta
                elif not est_prevu and est_present:
                    m_pres_imprev += delta
                elif (est_prevu and not est_present and not est_excuse) or est_abus:
                    m_absent += delta

                if est_prevu and type == 'p':
                    #assert est_debut == False
                    est_prevu = est_debut
                elif not est_prevu and type == 'p':
                    #assert est_debut == True
                    est_prevu = est_debut
                elif est_present and type == 'r':
                    #assert est_debut == False
                    est_present = est_debut
                elif not est_present and type == 'r':
                    #assert est_debut == True
                    est_present = est_debut
                elif est_excuse and type == 'e':
                    #assert est_debut == False
                    est_excuse = est_debut
                elif not est_excuse and type == 'e':
                    #assert est_debut == True
                    est_excuse = est_debut
                elif est_abus and type == 'a':
                    #assert est_debut == False
                    est_abus = est_debut
                elif not est_abus and type == 'a':
                    #assert est_debut == True
                    est_abus = est_debut
                hdebut = heure
            # print "minutes_present_prevu ", m_pres_prev
            # print "minutes_present_imprevu ", m_pres_imprev
            # print "minutes_absent ", m_absent
            
            result[record.id] = {}
            result[record.id]['minutes_present_prevu'] = mam_tools.conv_minutes2str(m_pres_prev)
            result[record.id]['minutes_present_imprevu'] = mam_tools.conv_minutes2str(m_pres_imprev)
            result[record.id]['minutes_absent'] = mam_tools.conv_minutes2str(m_absent)
            result[record.id]['minutes_excuse'] = mam_tools.conv_minutes2str(m_excuse)
        print
        return result
    STATE_SELECTION = [
        (u'encours', u'En cours'),
        (u'valide', u'Valide'),
        (u'cloture', u'Cloture'),
    ]
    _columns = {
        'jour': fields.date('Jour',required=True, help='La date'),
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la journée'),
        'mange_midi': fields.boolean('Midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Gouter', help='Prise du gouter'),
        'frais_montant': fields.float('Frais', digits=(6,2), help='Montant des frais en euros'),
        'frais_libelle': fields.char('Libellé des frais', help='Libellé des frais'),
        'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
        'state': fields.selection(STATE_SELECTION, 'Statut',required=True,  help='Le statut de la journée pour l''enfant'),
        'presence_e_ids': fields.one2many('mam.presence_e', 'jour_e_id', 'Liste des présences réelles', help='Liste des présences réelles de l''enfant'),
        'presence_prevue_ids': fields.one2many('mam.presence_prevue', 'jour_e_id', 'Liste des présences prevues', help='Liste des présences prevues de l''enfant'),
        "minutes_present_prevu": fields.function(
            _get_minutes,
            type="char",
            string="Prés. prévu",
            # store={
                # "mam.presence_e": (
                    # _filter_jour_presence_e, ['heure_debut', 'heure_fin'], 10),
                # "mam.presence_prevue": (
                    # _filter_jour_presence_prevue, ['heure_debut', 'heure_fin'], 10),
            # },
            store=None,
            multi='get_minutes',
        ),
        "minutes_present_imprevu": fields.function(
            _get_minutes,
            type="char",
            string="Prés. imprévu",
            store=None,
            multi='get_minutes',
        ),
        "minutes_absent": fields.function(
            _get_minutes,
            type="char",
            string="Absent",
            store=None,
            multi='get_minutes',
        ),
        "minutes_excuse": fields.function(
            _get_minutes,
            type="char",
            string="Excusé",
            store=None,
            multi='get_minutes',
        ),

        'libelle_prevue': fields.function(
            _get_libelle_prevue,
            type="char",
            string="Prevu",
            store=None,
        ),
        'libelle_reel': fields.function(
            _get_libelle_reel,
            type="char",
            string="Reel",
            store=None,
        ),
        'jour_type_ids' : fields.related('enfant_id', 'jour_type_ids', type='many2many', readonly=True, relation='mam.jour_type', string='Jours types disponibles'),
    }
    _defaults = {
        'enfant_id': lambda self,cr,uid,context: context.get('enfant_id', 0), 
        'mange_midi': False,
        'mange_gouter': False,
        'state': 'encours',
    }
    _rec_name = 'jour'
    _order = "jour"
    def action_associer_jour_type_1(self, cr, uid, ids, context=None):
        return self.action_associer_jour_type(cr, uid, ids, 0, context)
    def action_associer_jour_type_2(self, cr, uid, ids, context=None):
        return self.action_associer_jour_type(cr, uid, ids, 1, context)
    def action_associer_jour_type_3(self, cr, uid, ids, context=None):
        return self.action_associer_jour_type(cr, uid, ids, 2, context)
    def action_associer_jour_type_4(self, cr, uid, ids, context=None):
        return self.action_associer_jour_type(cr, uid, ids, 3, context)
    def action_associer_jour_type(self, cr, uid, ids, numero, context=None):
        """associe un jour type a un jour d'un enfant
            pour l'instant, on associe au premier jour type trouvé !"""
        for jour_e in self.browse(cr, uid, ids, context=context):
            jour_type_ids = jour_e.enfant_id.jour_type_ids
            if len(jour_type_ids) <= numero:
                continue
            self.write(cr, uid, jour_e.id, {'mange_midi':jour_type_ids[numero].mange_midi,'mange_gouter':jour_type_ids[numero].mange_gouter,})
            for presence_type in jour_type_ids[numero].presence_type_ids:
                print "cree ", presence_type.heure_debut, presence_type.heure_fin
                self.pool.get('mam.presence_prevue').create(cr, uid,{'jour_e_id': jour_e.id, 'heure_debut': presence_type.heure_debut, 'heure_fin': presence_type.heure_fin,})
        return True
    def action_effacer_prevision(self, cr, uid, ids, context=None):
        """effacer les previsions de presence du jour"""
        for jour_e in self.browse(cr, uid, ids, context=context):
            print jour_e.jour, jour_e.enfant_id.prenom, jour_e.presence_prevue_ids
            for presence_prevue in jour_e.presence_prevue_ids:
                self.pool.get('mam.presence_prevue').unlink(cr, uid, presence_prevue.id, context=context)
        return True
    def action_copier_presence_prevue(self, cr, uid, ids, context=None):
        """Cliquer ici pour copier les présences prévisionnelles dans les présences réelles"""
        for jour_e in self.browse(cr, uid, ids, context=context):
            print jour_e.jour, jour_e.enfant_id.prenom, jour_e.presence_prevue_ids
            for presence_prevue in jour_e.presence_prevue_ids:
                print "copie des jours prev", presence_prevue.heure_debut, presence_prevue.heure_fin
                self.pool.get('mam.presence_e').create(cr, uid,{'jour_e_id': jour_e.id, 'type': u'normal', 'heure_debut': presence_prevue.heure_debut, 'heure_fin': presence_prevue.heure_fin, 'libelle': presence_prevue.libelle})
        return True
mam_jour_e()

class mam_presence_e(osv.Model):
    _name = 'mam.presence_e'
    _description = "Detail presence"
    _rec_name = 'libelle'
    def _get_lib_date(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {}
            result[record.id]['libelle'] = self.TYPE_SELECTION_dict[record.type] + " (" + record.heure_debut + "-" + record.heure_fin + ")"
        return result
    def on_change_heure(self, cr, uid, ids, heure_debut, heure_fin, context=None):
        res = mam_tools.verif_heures(heure_debut, heure_fin)
        if res:
            return {'value': {'heure_debut':res[0],'heure_fin':res[1]}}
        return {'value':{},'warning':{'title':'Erreur','message':'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10'}}
    TYPE_SELECTION = [
        (u'normal', u'Présence normale'),
        (u'malade', u'Enfant malade ou accident, certificat a fournir sous 48h'),
        (u'abus', u'Enfant malade trop souvent (>10 j)'),
        (u'absent', u'Enfant absent sans justificatif du médecin'),
        (u'cause_am', u'Enfant forcé de s absenter parce que l AM est absente'),
    ]
    TYPE_SELECTION_dict = dict(TYPE_SELECTION)
    _columns = {
        'jour_e_id': fields.many2one('mam.jour_e','Jour',required=True, help='Jour concerne par la presence/absence'),
        'type': fields.selection(TYPE_SELECTION, 'Type',required=True,  help='Type de présence/absence de l''enfant'),
        'heure_debut': fields.char('Heure début',required=True, help='Heure de début'),
        'heure_fin': fields.char('Heure fin',required=True, help='Heure de fin'),
        "libelle": fields.function(
            _get_lib_date,
            type="char",
            string="Créneau",
            store=None,
            multi='modif_date',
        ),
    }
    _defaults = {
        'type': 'normal',
    }
    def check_heures(self, cr, uid, ids, context=None):
        reads = self.read(cr, uid, ids, ['heure_debut', 'heure_fin'], context=context)
        for records in reads:
            if not mam_tools.verif_heures(records['heure_debut'],records['heure_fin']):
                return False
        return True
    _constraints = [(check_heures, 'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10', ['heure_debut', 'heure_fin']),]
mam_presence_e()

class mam_presence_prevue(osv.Model):
    _name = 'mam.presence_prevue'
    _description = "Presence prevue"
    _rec_name = 'libelle'
    def _get_lib_date(self, cr, uid, ids, name, args, context=None):
        """nom affichable de la presence """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = {}
            result[record.id]['libelle'] = record.heure_debut + "-" + record.heure_fin
        return result
    def on_change_heure(self, cr, uid, ids, heure_debut, heure_fin, context=None):
        res = mam_tools.verif_heures(heure_debut, heure_fin)
        if res:
            return {'value': {'heure_debut':res[0],'heure_fin':res[1]}}
        return {'value':{},'warning':{'title':'Erreur','message':'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10'}}
    _columns = {
        'jour_e_id': fields.many2one('mam.jour_e','Jour',required=True, help='Jour concerné par la présence'),
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
            if not mam_tools.verif_heures(records['heure_debut'],records['heure_fin']):
                return False
        return True
    _constraints = [(check_heures, 'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10', ['heure_debut', 'heure_fin']),]
mam_presence_prevue()

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
    _order = "enfant_id"
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
            result[record.id]['libelle'] = record.heure_debut + "-" + record.heure_fin
        return result
    def on_change_heure(self, cr, uid, ids, heure_debut, heure_fin, context=None):
        res = mam_tools.verif_heures(heure_debut, heure_fin, False)
        if res:
            return {'value': {'heure_debut':res[0],'heure_fin':res[1]}}
        return {'value':{},'warning':{'title':'Erreur','message':'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10'}}
    _columns = {
        'jour_type_id': fields.many2one('mam.jour_type','Jour type',required=True, help='Jour type concerné par la présence'),
        'heure_debut': fields.char('Heure début',required=True, help='Heure de début'),
        'heure_fin': fields.char('Heure fin',required=True, help='Heure de fin'),
        "libelle": fields.function(
            _get_lib_date,
            type="char",
            string="Créneau",
            store=None,
            multi='modif_date',
        ),
    }
    _order = "heure_debut"
    def check_heures(self, cr, uid, ids, context=None):
        reads = self.read(cr, uid, ids, ['heure_debut', 'heure_fin'], context=context)
        for records in reads:
            if not mam_tools.verif_heures(records['heure_debut'],records['heure_fin'], True):
                return False
        return True
    _constraints = [(check_heures, 'Format invalide : Veuillez entrer des heures valides comme 8:30 ou 15h10', ['heure_debut', 'heure_fin']),]
mam_presence_type()

