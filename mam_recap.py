# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date,timedelta
import calendar

class mam_mois_e(osv.Model):
    _name = 'mam.mois_e'
    _description = "Detail mois"
    def calculs_mois(self, cr, uid, ids, name, args, context=None):
        # Tous les calculs de fin de mois
        # Problème du début de contrat (d'avenants) en milieu de mois : on considère que le premier mois est une régul. 
        # L'année commence le mois suivant.
        result = {}
        for mois_e in self.browse(cr, uid, ids, context=context):

            date_debut_avenant = mois_e.avenant_id.date_debut # au format yyyy-mm-dd
            date_fin_avenant = mois_e.avenant_id.date_fin # au format yyyy-mm-dd (ou false s'il n'y en a pas)

            jour_debut = 1
            if date_debut_avenant[:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois du début du contrat, le jour_début est le premier jour du contrat.
                jour_debut = date_debut_avenant[8:]
            date_debut_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_debut)

            jour_fin = calendar.monthrange(mois_e.annee, mois_e.mois)[1] # dernier jour du mois
            if date_fin_avenant and date_fin_avenant [:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois de fin du contrat, le jour_fin est le dernier jour du contrat.
                jour_fin = date_fin_avenant[8:]
            date_fin_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_fin)

            print "---", date_debut_mois, date_fin_mois
            print "debut calcul mois : ", date_debut_mois, date_fin_mois

            # calcul du mois de régul
            if date_debut_avenant[8:] == "01": # le contrat commence en début de mois
                # calcul du mois de regul de l'avenant (mois précédant l'anniversaire)
                mois_de_regul_avenant = int(date_debut_avenant[5:7]) - 1
                if mois_de_regul_avenant == 0:
                    mois_de_regul_avenant = 12 # décembre
            else:
                # sinon la regul se fait le mois anniversaire et non pas le mois précédent
                mois_de_regul_avenant = int(date_debut_avenant[5:7])
            print "mois de regul avenant : ", mois_de_regul_avenant

            # faut-il faire une régul ce mois-ci ?
            faire_regul = (mois_de_regul_avenant == mois_e.mois)
            print "faire regul : ", faire_regul

            result[mois_e.id] = {}
            result[mois_e.id]['jour_debut'] = jour_debut
            result[mois_e.id]['jour_fin'] = jour_fin
        return result
    _columns = {
        'annee': fields.integer('Année',required=True, help='L''année'),
        'mois': fields.integer('Mois',required=True, help='Le mois de l''année'),
        'avenant_id': fields.many2one('mam.avenant','Avenant',required=True, help='Avenant concerné par le mois'),

        "jour_debut": fields.function(
            calculs_mois,
            type="integer",
            string="jour début",
            store=None,
            multi='calculs_mois',
        ),
        "jour_fin": fields.function(
            calculs_mois,
            type="integer",
            string="jour fin",
            store=None,
            multi='calculs_mois',
        ),
# -      Période du xxx au xxx/xxx/20xxx
# -      Nombre d’heures normales (moyenne prévue au contrat dans le cadre de la mensualisation, à laquelle on ajoute les heures d’absence pour congés payés (y compris les congés payés soldés en fin de contrat)) : xxx
# -      Nombre de jours d’activités : xxx (moyenne prévue au contrat dans le cadre de la mensualisation)
# -      Nombre de jours de congés payés pris (ou soldés pour une fin de contrat) : xxx
# -      Nombre d’heures complémentaires : xxx
# -      Nombre d’heures supplémentaires : xxx
# -      Salaire net de base : xxx
# -      Indemnité d’entretien : xxx
# -      Indemnité de repas, kilométriques et de rupture : xxx
# Nombre jours complets travaillés
# Nombre total d'heures travaillées
# Nombre d'heures complémentaires
# Nombre d'heures supplémentaires
# Nombre d'heures normales
# Nombre d'heures Arrêt Maladie
# Heures par rapport à 120h
# Salaire de base (120h)
# Montant heures complémentaires
# Montant heures supplémentaires
# Nombre d'heures d'absence
# Montant d'heures d'absence
# Salaire brut
# Rémunération brute congés payés
# Total retenues
# Salaire net (hors frais annexes)
# Nombre de jours <9h
# Nombre de jours >9h
# Montant indemnité entretien
# Nombre de repas
# Nombre de goûter
# Montant indemnité repas + goûter
# Nombre de kilomètres parcourus
# Montant indemnité kilométrique
# Montant sortie/avance…
# Salaire net à recevoir
# Salaire net réellement reçu
# Salaire différence
# Cumul des congés acquis par mois
# Nombre de jours de congés pris
# Congés acquis au 31/05/2012 restants


# Au niveau de la mam:
# au bout de 46h : heures sup'

# quand enfant malade avec justif : les heures sont déduites du salaire de base mensuel + on décompte le nombre d'heures restantes du nombre total d'heures prévues au contrat
# cause am = comme quand malade



        # 'mange_midi': fields.boolean('Midi', help='Prise du repas du midi'),
        # 'mange_gouter': fields.boolean('Gouter', help='Prise du gouter'),
        # 'frais_montant': fields.float('Frais', digits=(6,2), help='Montant des frais en euros'),
        # 'frais_libelle': fields.char('Libellé des frais', help='Libellé des frais'),
        # 'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
        # 'state': fields.selection(STATE_SELECTION, 'Statut',required=True,  help='Le statut de la journée pour l''enfant'),
        # 'presence_e_ids': fields.one2many('mam.presence_e', 'mois_e_id', 'Liste des présences réelles', help='Liste des présences réelles de l''enfant'),
        # 'presence_prevue_ids': fields.one2many('mam.presence_prevue', 'mois_e_id', 'Liste des présences prevues', help='Liste des présences prevues de l''enfant'),
        # "minutes_present_prevu": fields.function(
            # _get_minutes,
            # type="char",
            # string="Prés. prévu",
            # store={
                # "mam.presence_e": (
                    # _filter_jour_presence_e, ['heure_debut', 'heure_fin'], 10),
                # "mam.presence_prevue": (
                    # _filter_jour_presence_prevue, ['heure_debut', 'heure_fin'], 10),
            # },
            # multi='get_minutes',
        # ),
        # "minutes_present_imprevu": fields.function(
            # _get_minutes,
            # type="char",
            # string="Prés. imprévu",
            # store=None,
            # multi='get_minutes',
        # ),
        # "minutes_absent": fields.function(
            # _get_minutes,
            # type="char",
            # string="Absent",
            # store=None,
            # multi='get_minutes',
        # ),

        # 'libelle_prevue': fields.function(
            # _get_libelle_prevue,
            # type="char",
            # string="Prevu",
            # store=None,
        # ),
        # 'libelle_reel': fields.function(
            # _get_libelle_reel,
            # type="char",
            # string="Reel",
            # store=None,
        # ),
        # 'jour_type_ids' : fields.related('enfant_id', 'jour_type_ids', type='many2many', readonly=True, relation='mam.jour_type', string='Jours types disponibles'),
    }
    _defaults = {
        'avenant_id': lambda self,cr,uid,context: context.get('avenant_id', 0), 
    }
    # def action_associer_jour_type_1(self, cr, uid, ids, context=None):
        # return self.action_associer_jour_type(cr, uid, ids, 0, context)
    # def action_associer_jour_type_2(self, cr, uid, ids, context=None):
        # return self.action_associer_jour_type(cr, uid, ids, 1, context)
    # def action_associer_jour_type_3(self, cr, uid, ids, context=None):
        # return self.action_associer_jour_type(cr, uid, ids, 2, context)
    # def action_associer_jour_type_4(self, cr, uid, ids, context=None):
        # return self.action_associer_jour_type(cr, uid, ids, 3, context)
    # def action_associer_jour_type(self, cr, uid, ids, numero, context=None):
        # """associe un jour type a un jour d'un enfant
            # pour l'instant, on associe au premier jour type trouvé !"""
        # for mois_e in self.browse(cr, uid, ids, context=context):
            # jour_type_ids = mois_e.enfant_id.jour_type_ids
            # if len(jour_type_ids) <= numero:
                # continue
            # self.write(cr, uid, mois_e.id, {'mange_midi':jour_type_ids[numero].mange_midi,'mange_gouter':jour_type_ids[numero].mange_gouter,})
            # for presence_type in jour_type_ids[numero].presence_type_ids:
                # print "cree ", presence_type.heure_debut, presence_type.heure_fin
                # self.pool.get('mam.presence_prevue').create(cr, uid,{'mois_e_id': mois_e.id, 'heure_debut': presence_type.heure_debut, 'heure_fin': presence_type.heure_fin,})
        # return True
    # def action_effacer_prevision(self, cr, uid, ids, context=None):
        # """effacer les previsions de presence du jour"""
        # for mois_e in self.browse(cr, uid, ids, context=context):
            # print mois_e.jour, mois_e.enfant_id.prenom, mois_e.presence_prevue_ids
            # for presence_prevue in mois_e.presence_prevue_ids:
                # self.pool.get('mam.presence_prevue').unlink(cr, uid, presence_prevue.id, context=context)
        # return True
mam_mois_e()
