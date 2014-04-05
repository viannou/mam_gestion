# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date,timedelta
import calendar
import mam_tools
from mam_tools import pl, ppl
import pprint
import logging

_logger = logging.getLogger("recap ::::")

class mam_mois_e(osv.Model):
    _name = 'mam.mois_e'
    _description = "Detail mois"
    def calculs_mois(self, cr, uid, ids, name, args, context=None):
        # Tous les calculs de fin de mois
        # Problème du début de contrat (d'avenants) en milieu de mois : on considère que le premier mois est une régul. 
        # L'année commence le mois suivant.

        # Valeurs partagées
        eur_salaire_horaire_net = 3.2 # 3.2€ / heure 
        eur_salaire_complementaire_net = 3.2 # 3.2€ / heure 
        eur_salaire_supplementaire_net = 4.0 # 4.0€ / heure 
        eur_entretien_0_9 = 3.2 # 3.2€ / jour si moins de 9h
        eur_entretien_9_plus = 4.0 # 4.0€ / jour si plus de 9h
        eur_repas_midi_6_18m = 2.0
        eur_repas_midi_plus_18m = 3.0
        eur_repas_gouter = 1.0
        coef_net_brut = 1.3



        result = {}
        for mois_e in self.browse(cr, uid, ids, context=context):

            #type_contrat = mois_e.avenant_id.contrat_id.type
            date_debut_avenant = mois_e.avenant_id.date_debut # au format yyyy-mm-dd
            date_fin_avenant = mois_e.avenant_id.date_fin # au format yyyy-mm-dd (ou false s'il n'y en a pas)

            jour_debut = 1
            if date_debut_avenant[:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois du début du contrat, le jour_début est le premier jour du contrat.
                jour_debut = int(date_debut_avenant[8:])
            date_debut_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_debut)
            date_debut_mois_d = datetime.date(mois_e.annee, mois_e.mois, jour_debut)

            jour_fin = calendar.monthrange(mois_e.annee, mois_e.mois)[1] # dernier jour du mois = nombre de jours dans le mois
            if date_fin_avenant and date_fin_avenant [:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois de fin du contrat, le jour_fin est le dernier jour du contrat.
                jour_fin = int(date_fin_avenant[8:])
            date_fin_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_fin)

            _logger.info(pl("--- debut calcul mois :", mois_e.avenant_id.contrat_id.enfant_id.nomprenom, date_debut_mois, date_fin_mois))

            # calcul du nombre de jours à récupérer du mois précédent pour le calcul des heures complémentaires par semaines
            lundi_mois_prec_d = date_debut_mois_d - timedelta(days=date_debut_mois_d.weekday())

            # tarif du repas du midi par rapport à l'age
            age_mois = (datetime.strptime(date_fin_mois,'%Y-%m-%d') - datetime.strptime(mois_e.avenant_id.contrat_id.enfant_id.date_naiss,'%Y-%m-%d')).days / 30
            _logger.info(pl( "age du gamin", age_mois))
            if age_mois > 18:
                eur_repas_midi = eur_repas_midi_plus_18m
                _logger.info(pl( "> 18, repas midi :",eur_repas_midi))
            else:
                eur_repas_midi = eur_repas_midi_6_18m
                _logger.info(pl( ">= 18, repas midi :",eur_repas_midi))

            # calcul du mois de régul
            if date_debut_avenant[8:] == "01": # le contrat commence en début de mois
                # calcul du mois de regul de l'avenant (mois précédant l'anniversaire)
                mois_de_regul_avenant = int(date_debut_avenant[5:7]) - 1
                if mois_de_regul_avenant == 0:
                    mois_de_regul_avenant = 12 # décembre
            else:
                # sinon la regul se fait le mois anniversaire et non pas le mois précédent
                mois_de_regul_avenant = int(date_debut_avenant[5:7])
            _logger.info(pl( "mois de regul avenant : ", mois_de_regul_avenant))

            # faut-il faire une régul ce mois-ci ?
            faire_regul = (mois_de_regul_avenant == mois_e.mois)
            _logger.info(pl( "faire regul : ", faire_regul))

            # on parcourt les jours pour récupérer les infos
            m_pres_prev = m_pres_imprev = m_absent = m_excuse = 0
            indemnite_entretien = 0.0
            indemnite_midi = indemnite_gouter = indemnite_frais = 0.0
            mam_jour_e = self.pool.get('mam.jour_e')
            _logger.info(pl( "enfant_id", mois_e.avenant_id.contrat_id.enfant_id.id))
            # attention : on recherche tous les jours en commençant au lundi de la semaine d'avant pour les calculs à la semaine
            jour_e_ids = mam_jour_e.search(cr, uid, [('enfant_id','=',mois_e.avenant_id.contrat_id.enfant_id.id),('jour','>=',str(lundi_mois_prec_d)),('jour','<=',date_fin_mois)], context=context)
            for jour_e in mam_jour_e.browse(cr, uid, jour_e_ids, context=context):
                if (jour_e.jour < date_debut_mois)
                    # jours du mois précédent
                    _logger.info(pl( "semaine prec:", jour_e.jour))
                    
                    # mais on ne va pas plus loin
                    continue
                j_pres_prev = mam_tools.conv_str2minutes(jour_e.minutes_present_prevu)
                j_pres_imprev = mam_tools.conv_str2minutes(jour_e.minutes_present_imprevu)
                j_absent = mam_tools.conv_str2minutes(jour_e.minutes_absent)
                j_excuse = mam_tools.conv_str2minutes(jour_e.minutes_excuse)
                m_pres_prev += j_pres_prev
                m_pres_imprev += j_pres_imprev
                m_absent += j_absent
                m_excuse += j_excuse

                # calculs des frais d'entretiens
                if j_pres_prev + j_pres_imprev > 0:
                    if j_pres_prev + j_pres_imprev <= 9*60:
                        indemnite_entretien += eur_entretien_0_9
                    else:
                        indemnite_entretien += eur_entretien_9_plus

                # calcul des frais repas + autres
                if jour_e.mange_midi:
                    indemnite_midi += eur_repas_midi
                if jour_e.mange_gouter:
                    indemnite_gouter += eur_repas_gouter
                indemnite_frais += jour_e.frais_montant

# quand enfant malade avec justif : les heures sont déduites du salaire de base mensuel + on décompte le nombre d'heures restantes du nombre total d'heures prévues au contrat
# cause am = comme quand malade

            m_contrat = mois_e.avenant_id.nb_h_par_an * (60/12) # on stocke des minutes par mois
            m_effectif = m_contrat - m_excuse
            
            # heure complémentaire : heure non prévue au contrat jusqu'à 46h # on stocke des minutes
            # au delà, c'est des heures supplémentaires
            if m_pres_imprev <= 46*60:
                m_complementaires = m_pres_imprev
                m_supplementaires = 0
            else:
                m_complementaires = 46*60
                m_supplementaires = m_pres_imprev - 46*60

            # Pour le premier mois, on compte comme en halte garderie : ce qui est du. Pas de congés ?
            presences_net = float(m_pres_prev-m_excuse)/60 * eur_salaire_horaire_net + float(m_complementaires)/60 * eur_salaire_complementaire_net + float(m_supplementaires)/60 * eur_salaire_supplementaire_net
            absences_net = float(m_absent)/60 * eur_salaire_horaire_net
            salaire_net = presences_net + absences_net

            result[mois_e.id] = {}
            result[mois_e.id]['jour_debut'] = jour_debut
            result[mois_e.id]['jour_fin'] = jour_fin
            result[mois_e.id]['minutes_present_prevu'] = mam_tools.conv_minutes2str(m_pres_prev)
            result[mois_e.id]['minutes_present_imprevu'] = mam_tools.conv_minutes2str(m_pres_imprev)
            result[mois_e.id]['minutes_absent'] = mam_tools.conv_minutes2str(m_absent)
            result[mois_e.id]['minutes_excuse'] = mam_tools.conv_minutes2str(m_excuse)
            result[mois_e.id]['nb_heures_mois_contrat'] = mam_tools.conv_minutes2str(m_contrat)
            result[mois_e.id]['nb_heures_mois_effectif'] = mam_tools.conv_minutes2str(m_effectif)
            result[mois_e.id]['nb_heures_complementaires'] = mam_tools.conv_minutes2str(m_complementaires)
            result[mois_e.id]['nb_heures_supplementaires'] = mam_tools.conv_minutes2str(m_supplementaires)
            result[mois_e.id]['presences_brut'] = presences_net * coef_net_brut
            result[mois_e.id]['presences_net'] = presences_net
            result[mois_e.id]['absences_brut'] = absences_net * coef_net_brut
            result[mois_e.id]['absences_net'] = absences_net
            result[mois_e.id]['salaire_brut'] = salaire_net * coef_net_brut
            result[mois_e.id]['salaire_net'] = salaire_net
            result[mois_e.id]['indemnite_entretien'] = indemnite_entretien
            result[mois_e.id]['indemnite_midi'] = indemnite_midi
            result[mois_e.id]['indemnite_gouter'] = indemnite_gouter
            result[mois_e.id]['indemnite_frais'] = indemnite_frais
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
        "minutes_present_prevu": fields.function(
            calculs_mois,
            type="char",
            string="Prés. prévu",
            store=None,
            multi='calculs_mois',
        ),
        "minutes_present_imprevu": fields.function(
            calculs_mois,
            type="char",
            string="Prés. imprévu",
            store=None,
            multi='calculs_mois',
        ),
        "minutes_absent": fields.function(
            calculs_mois,
            type="char",
            string="Absent",
            store=None,
            multi='calculs_mois',
        ),
        "minutes_excuse": fields.function(
            calculs_mois,
            type="char",
            string="Excusé",
            store=None,
            multi='calculs_mois',
        ),
        "nb_heures_mois_contrat": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures par mois contrat",
            store=None,
            multi='calculs_mois',
        ),
        "nb_heures_mois_effectif": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures par mois effectif",
            store=None,
            multi='calculs_mois',
        ),
        "nb_heures_complementaires": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures complementaires",
            store=None,
            multi='calculs_mois',
        ),
        "nb_heures_supplementaires": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures supplémentaires",
            store=None,
            multi='calculs_mois',
        ),
        "presences_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire présences brut",
            store=None,
            multi='calculs_mois',
        ),
        "presences_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire présences net",
            store=None,
            multi='calculs_mois',
        ),
        "absences_brut": fields.function(
            calculs_mois,
            type="float",
            string="Absences brut",
            store=None,
            multi='calculs_mois',
        ),
        "absences_net": fields.function(
            calculs_mois,
            type="float",
            string="Absences net",
            store=None,
            multi='calculs_mois',
        ),
        "salaire_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire brut",
            store=None,
            multi='calculs_mois',
        ),
        "salaire_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire net",
            store=None,
            multi='calculs_mois',
        ),
        "indemnite_entretien": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité d'entretien",
            store=None,
            multi='calculs_mois',
        ),
        "indemnite_midi": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité de repas midi",
            store=None,
            multi='calculs_mois',
        ),
        "indemnite_gouter": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité de repas goûter",
            store=None,
            multi='calculs_mois',
        ),
        "indemnite_frais": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité kilométrique et de rupture",
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


    }
    _defaults = {
        'avenant_id': lambda self,cr,uid,context: context.get('avenant_id', 0), 
    }
mam_mois_e()
