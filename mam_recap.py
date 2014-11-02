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
        eur_entretien_minimum = 32.0 # 32 € d'entretien minimum
        eur_repas_midi_6_18m = 2.0
        eur_repas_midi_plus_18m = 3.0
        eur_repas_gouter = 1.0
        coef_net_brut = 1.3



        result = {}
        for mois_e in self.browse(cr, uid, ids, context=context):

            type_contrat = mois_e.avenant_id.contrat_id.type
            date_debut_avenant = mois_e.avenant_id.date_debut # au format yyyy-mm-dd
            date_fin_avenant = mois_e.avenant_id.date_fin # au format yyyy-mm-dd (ou false s'il n'y en a pas)

            remarques = ""
            jour_debut = 1
            est_debut_avenant = False
            est_fin_avenant = False
            if date_debut_avenant[:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois du début du contrat, le jour_début est le premier jour du contrat.
                jour_debut = int(date_debut_avenant[8:])
                est_debut_avenant = True
            date_debut_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_debut)
            date_debut_mois_d = date(mois_e.annee, mois_e.mois, jour_debut)

            jour_fin = calendar.monthrange(mois_e.annee, mois_e.mois)[1] # dernier jour du mois = nombre de jours dans le mois
            if date_fin_avenant and date_fin_avenant [:7] == "{0}-{1:02d}".format(mois_e.annee, mois_e.mois): # le mois de fin du contrat, le jour_fin est le dernier jour du contrat.
                jour_fin = int(date_fin_avenant[8:])
                est_fin_avenant = True
            date_fin_mois = "{0}-{1:02d}-{2:02d}".format(mois_e.annee, mois_e.mois, jour_fin)

            _logger.info(pl("--- debut calcul mois :", mois_e.avenant_id.contrat_id.enfant_id.nomprenom, date_debut_mois, date_fin_mois))

            # calcul du nombre de jours à récupérer du mois précédent pour le calcul des heures complémentaires par semaines
            if date_debut_mois_d.weekday() >= 5: # le premier du mois est samedi ou dimanche
                lundi_mois_prec_d = date_debut_mois_d # on ne va pas chercher les dates du mois précédent
            else:
                # on commence la recherche au lundi d'avant
                lundi_mois_prec_d = date_debut_mois_d - timedelta(days=date_debut_mois_d.weekday())

            # tarif du repas du midi par rapport à l'age
            age_mois = int((datetime.strptime(date_fin_mois,'%Y-%m-%d') - datetime.strptime(mois_e.avenant_id.contrat_id.enfant_id.date_naiss,'%Y-%m-%d')).days / 30.417)
            _logger.info(pl( "age du gamin", age_mois))
            if age_mois > 18:
                eur_repas_midi = eur_repas_midi_plus_18m
                _logger.info(pl( "> 18, repas midi :",eur_repas_midi))
            else:
                eur_repas_midi = eur_repas_midi_6_18m
                _logger.info(pl( ">= 18, repas midi :",eur_repas_midi))
            remarques += "age enfant (mois) : " + `age_mois` + "\n"
            remarques += "tarif repas : " + `eur_repas_midi` + "\n"
                
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
            if faire_regul:
                remarques += "il faut faire une régul ce mois-ci\n"
            else:
                remarques += "il ne faut pas faire une régul ce mois-ci\n"

            
            # on parcourt les jours pour récupérer les infos
            m_pres_prev = m_pres_imprev = m_absent = m_excuse = 0
            m_complementaires = m_supplementaires = m_imprev_semaine = 0
            indemnite_entretien = 0.0
            indemnite_midi = indemnite_gouter = indemnite_frais = 0.0
            nb_jours_activite = 0
            mam_jour_e = self.pool.get('mam.jour_e')
            _logger.info(pl( "enfant_id", mois_e.avenant_id.contrat_id.enfant_id.id))
            # attention : on recherche tous les jours en commençant au lundi de la semaine d'avant pour les calculs à la semaine
            jour_e_ids = mam_jour_e.search(cr, uid, [('enfant_id','=',mois_e.avenant_id.contrat_id.enfant_id.id),('jour','>=',str(lundi_mois_prec_d)),('jour','<=',date_fin_mois)], order='jour', context=context)
            for jour_e in mam_jour_e.browse(cr, uid, jour_e_ids, context=context):
                if (jour_e.jour < date_debut_mois):
                    # jours du mois précédent
                    _logger.info(pl( "semaine prec:", jour_e.jour))
                    m_imprev_semaine += mam_tools.conv_str2minutes(jour_e.minutes_present_imprevu)
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
                if j_pres_prev + j_pres_imprev + j_absent > 0:
                    nb_jours_activite += 1
                
                # pour les contrats halte garderie, il n'y a pas de prévu, seulement de l'imprévu ; on transfert tout dans l'imprévu.
                if type_contrat != u'normal':
                    m_pres_imprev += m_pres_prev
                    m_pres_prev = 0


                # pour un contrat normal, on compte les heures complémentaires et supplémentaires
                m_imprev_semaine += j_pres_imprev
                # le vendredi, calcul des jours complémentaires/supplémentaires
                if datetime.strptime(jour_e.jour,'%Y-%m-%d').weekday() == 4:
                    # heure complémentaire : heure non prévue au contrat jusqu'à 46h par semaine # on stocke des minutes
                    # au delà, c'est des heures supplémentaires
                    if m_imprev_semaine <= 46*60:
                        m_complementaires += m_imprev_semaine
                    else:
                        m_complementaires += 46*60
                        m_supplementaires += m_imprev_semaine - 46*60
                    _logger.error(pl( "semaine ",jour_e.jour,":", m_imprev_semaine, "compl:", m_complementaires, "suppl:",m_supplementaires))
                    remarques += "imprevu semaine du " + jour_e.jour + ": "+ `m_imprev_semaine`+ " m, total compl:"+ `m_complementaires`+ " m, total suppl:"+`m_supplementaires`+" m\n"
                    # on remet le compteur à zero pour la semaine suivante
                    m_imprev_semaine = 0
                # pour un contrat halte garderie, on ne compte que les heures supplémentaires
                if type_contrat != u'normal':
                    m_complementaires = 0

                    
                # calculs des frais d'entretiens
                if j_pres_prev + j_pres_imprev > 0:
                    if j_pres_prev + j_pres_imprev < 9*60:
                        indemnite_entretien += eur_entretien_0_9
                    else:
                        indemnite_entretien += eur_entretien_9_plus

                # calcul des frais repas + autres
                if jour_e.mange_midi:
                    indemnite_midi += eur_repas_midi
                if jour_e.mange_gouter:
                    indemnite_gouter += eur_repas_gouter
                indemnite_frais += jour_e.frais_montant

            m_contrat = 0
            salaire_base_net = 0
            absences_net = 0
            excuse_net = 0
            m_effectif = 0
            if type_contrat == u'normal':
                # indemnité d'entretien minimum : 32€ (si le contrat ne se termine pas ou ne commence pas)
                if indemnite_entretien < eur_entretien_minimum and not est_debut_avenant and not est_fin_avenant :
                    # TODO: a améliorer pour que si le début du contrat et le premier jour du mois ou fin = fin on prenne qd meme le minimum...
                    remarques += "Passage entretien minimum : " + `indemnite_entretien` + " --> " + `eur_entretien_minimum` + "\n"
                    indemnite_entretien = eur_entretien_minimum

# quand enfant malade avec justif : les heures sont déduites du salaire de base mensuel + on décompte le nombre d'heures restantes du nombre total d'heures prévues au contrat
# cause am = comme quand malade

                m_contrat = mois_e.avenant_id.nb_h_par_an * (60/12) # on stocke des minutes par mois
                salaire_base_net = float(m_contrat)/60 * eur_salaire_horaire_net

                m_effectif = m_contrat - m_excuse
                # on arrondit au dessus :
                m_effectif = (m_effectif + 59) / 60 * 60
            
            if type_contrat == u'normal':
                m_a_comptabiliser = m_pres_prev-m_excuse
            else:
                m_a_comptabiliser = m_pres_imprev
            
            
            # Pour le premier mois, on compte comme en halte garderie : ce qui est du. Pas de congés ?
            m_ajout_arrondi = (60 - ((m_a_comptabiliser) % 60)) % 60 
            remarques += "Ajout minutes pour arrondi : " + `m_ajout_arrondi` + "\n"
            remarques += "  Total minutes après arrondi : " + mam_tools.conv_minutes2str(m_a_comptabiliser + m_ajout_arrondi) + "\n"
            complementaires_net = float(m_complementaires)/60 * eur_salaire_complementaire_net
            supplementaires_net = float(m_supplementaires)/60 * eur_salaire_supplementaire_net
            presences_net = float(m_a_comptabiliser + m_ajout_arrondi)/60 * eur_salaire_horaire_net

            # salaire_hors_cp_abs_net :
            # Pour les contrats CDI : salaire de base prévu au contrat (sauf pour le premier mois où c’est le salaire au réel, càd en fonction du nombre d’heures réalisées dans le mois
            # Pour les contrats occasionnels : nb d’heures réalisées dans le mois x 3,20€
            cp_net = 0
            if type_contrat == u'normal':
                # TODO : le premier mois il est compté en présence_net
                if est_debut_avenant:
                    salaire_hors_cp_abs_net = presences_net
                else:
                    salaire_hors_cp_abs_net = salaire_base_net
                # TODO :
                # les congés payés ne sont pas pris en compte depuis le début jusqu'au 31 mais
                # a partir du 1er juin qui suit le début du contrat, il faut ajouter les congés payés qui sont fonction du début du contrat
                # les CP, c'est un montant fixe 1/12 de 1/10 de la rémunération net (salaire net) qui a eu lieu jusqu'à présent
                # ce montant, c'est toujours le même pendant 1 an.
                # L'année d'après, on refait le calcul (et pour l'histoire, le salaire net comprend les congés payés de l'année précédente...)
                cp_net = 0
                excuse_net = float(m_excuse)/60 * eur_salaire_horaire_net
                salaire_net = salaire_hors_cp_abs_net + cp_net - excuse_net  + complementaires_net + supplementaires_net
            else:
                salaire_hors_cp_abs_net = presences_net
                absences_net = float(m_absent)/60 * eur_salaire_horaire_net
                # CP : 10% tous les mois
                cp_net = (salaire_hors_cp_abs_net + absences_net) * 0.1
                salaire_net = salaire_hors_cp_abs_net + absences_net + cp_net  + complementaires_net + supplementaires_net

            
            # TODO : calcul de l'indemnité de rupture :
            # il faut que le contrat ait plus d'un an d'ancienneté
            # = 1/120 du total des salaires net perçus pendant la totalité du contrat
            indemnite_rupture = 0

            result[mois_e.id] = {}
            result[mois_e.id]['jour_debut'] = jour_debut
            result[mois_e.id]['jour_fin'] = jour_fin
            result[mois_e.id]['type_contrat'] = type_contrat
            result[mois_e.id]['minutes_present_prevu'] = mam_tools.conv_minutes2str(m_pres_prev)
            result[mois_e.id]['minutes_present_imprevu'] = mam_tools.conv_minutes2str(m_pres_imprev)
            result[mois_e.id]['minutes_absent'] = mam_tools.conv_minutes2str(m_absent)
            result[mois_e.id]['minutes_excuse'] = mam_tools.conv_minutes2str(m_excuse)
            result[mois_e.id]['nb_heures_mois_contrat'] = mam_tools.conv_minutes2str(m_contrat)
            result[mois_e.id]['salaire_base_brut'] = salaire_base_net * coef_net_brut
            result[mois_e.id]['salaire_base_net'] = salaire_base_net
            result[mois_e.id]['nb_heures_mois_effectif'] = mam_tools.conv_minutes2str(m_effectif)
            result[mois_e.id]['nb_heures_complementaires'] = mam_tools.conv_minutes2str(m_complementaires)
            result[mois_e.id]['nb_heures_supplementaires'] = mam_tools.conv_minutes2str(m_supplementaires)
            result[mois_e.id]['nb_jours_activite'] = nb_jours_activite
            result[mois_e.id]['presences_brut'] = presences_net * coef_net_brut
            result[mois_e.id]['presences_net'] = presences_net
            result[mois_e.id]['salaire_hors_cp_abs_brut'] = salaire_hors_cp_abs_net * coef_net_brut
            result[mois_e.id]['salaire_hors_cp_abs_net'] = salaire_hors_cp_abs_net
            result[mois_e.id]['absences_brut'] = absences_net * coef_net_brut
            result[mois_e.id]['absences_net'] = absences_net
            result[mois_e.id]['excuse_brut'] = excuse_net * coef_net_brut
            result[mois_e.id]['excuse_net'] = excuse_net
            result[mois_e.id]['cp_brut'] = cp_net * coef_net_brut
            result[mois_e.id]['cp_net'] = cp_net
            result[mois_e.id]['salaire_brut'] = salaire_net * coef_net_brut
            result[mois_e.id]['salaire_net'] = salaire_net
            result[mois_e.id]['indemnite_rupture'] = indemnite_rupture
            result[mois_e.id]['indemnite_entretien'] = indemnite_entretien
            result[mois_e.id]['indemnite_midi'] = indemnite_midi
            result[mois_e.id]['indemnite_gouter'] = indemnite_gouter
            result[mois_e.id]['indemnite_frais'] = indemnite_frais
            result[mois_e.id]['remarques'] = remarques
        return result
    _columns = {
        'annee': fields.integer('Année',required=True, help='L''année'),
        'mois': fields.integer('Mois',required=True, help='Le mois de l''année'),
        'avenant_id': fields.many2one('mam.avenant','Avenant',required=True, help='Avenant concerné par le mois'),

        # this is a special field used if you want to force the recalculation of all fileds.function fields
        "force_update_date": fields.datetime('Mise à jour'),
 
 
        "jour_debut": fields.function(
            calculs_mois,
            type="integer",
            string="jour début",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "jour_fin": fields.function(
            calculs_mois,
            type="integer",
            string="jour fin",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "minutes_present_prevu": fields.function(
            calculs_mois,
            type="char",
            string="Prés. prévu",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "type_contrat": fields.function(
            calculs_mois,
            type="char",
            string="Type de contrat",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "minutes_present_imprevu": fields.function(
            calculs_mois,
            type="char",
            string="Prés. imprévu",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "minutes_absent": fields.function(
            calculs_mois,
            type="char",
            string="Absent",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "minutes_excuse": fields.function(
            calculs_mois,
            type="char",
            string="Excusé",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "nb_heures_mois_contrat": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures par mois contrat",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "nb_heures_mois_effectif": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures par mois effectif",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "nb_heures_complementaires": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures complementaires",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "nb_heures_supplementaires": fields.function(
            calculs_mois,
            type="char",
            string="Nb heures supplémentaires",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "nb_jours_activite": fields.function(
            calculs_mois,
            type="integer",
            string="Nb jours d'activité",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "presences_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire présences brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "presences_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire présences net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "absences_brut": fields.function(
            calculs_mois,
            type="float",
            string="Absences brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "absences_net": fields.function(
            calculs_mois,
            type="float",
            string="Absences net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "excuse_brut": fields.function(
            calculs_mois,
            type="float",
            string="Excuse brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "excuse_net": fields.function(
            calculs_mois,
            type="float",
            string="Excuse net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_base_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire de base brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_base_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire de base net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_hors_cp_abs_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire hors CP et absences brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_hors_cp_abs_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire hors CP et absences net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "cp_brut": fields.function(
            calculs_mois,
            type="float",
            string="CP brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "cp_net": fields.function(
            calculs_mois,
            type="float",
            string="CP net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_brut": fields.function(
            calculs_mois,
            type="float",
            string="Salaire brut",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "salaire_net": fields.function(
            calculs_mois,
            type="float",
            string="Salaire net",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "indemnite_entretien": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité d'entretien",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "indemnite_midi": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité de repas midi",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "indemnite_gouter": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité de repas goûter",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "indemnite_frais": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité kilométrique",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "indemnite_rupture": fields.function(
            calculs_mois,
            type="float",
            string="Indemnité de rupture",
            store={'mam.mois_e': (lambda self, cr, uid, ids, context: ids, ['force_update_date'], 10),},
            multi='calculs_mois',
        ),
        "remarques": fields.function(
            calculs_mois,
            type="text",
            string="Remarques",
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
        # here we force the calculation on creation 
        #"force_update_date": lambda *a: datetime.today(),
    }
    def action_update(self, cr, uid, ids, context=None):
        """Faire tous les calculs du mois : invoquer force_update"""

        #for mois_e in self.browse(cr, uid, ids, context=context):
        for id in ids:
            self.write(
                cr, uid, id,
                {'force_update_date': datetime.today()},
                context=context
            )
    def action_creer_mois_suivant(self, cr, uid, ids, context=None):
        """Créer le mois suivant de l'avenant : j'essaie d'invoquer l'action de l'avenant..."""
        mam_avenant = self.pool.get('mam.avenant')

        #for id in ids:
        #    mam_avenant.action_creer_mois(cr, uid, id, context=context)
        """crée les mois inexistant pour l'avenant"""
        for mois_e in self.browse(cr, uid, ids, context=context):
            mois = mois_e.mois + 1
            if mois == 13:
                mois = 1
                annee = mois_e.annee + 1
            else:
                annee = mois_e.annee
            print "mois ", mois, " année ", annee 
            avenant_ids = mam_avenant.search(cr, uid, [('contrat_id','=',mois_e.avenant_id.contrat_id.id)], context=context)
            for avenant in mam_avenant.browse(cr, uid, avenant_ids, context=context):
                datetime.strptime(avenant.date_debut,'%Y-%m-%d')
                # si le mois a des jours dans l'avenant (on triche, on met la fin du mois le 28 (il y a un 28 tous les mois)
                print avenant.date_debut, "{0}-{1}-28".format(annee, mois), avenant.date_fin, "{0}-{1}-01".format(annee, mois)
                if (avenant.date_debut < "{0}-{1}-28".format(annee, mois)) and (avenant.date_fin < "{0}-{1}-01".format(annee, mois)):
                    mois_e_ids = self.search(cr, uid, [('avenant_id','=',avenant.id),('annee','=', annee),('mois','=', mois)], context=context)
                    if not mois_e_ids: # le mois de l'avenant n'existe pas encore
                        print "cree mois avenant ", avenant.id, " annee ", annee, " mois ", mois
                        self.create(cr, uid,{ 'annee': annee,'mois': mois,'avenant_id' : avenant.id,})
        return True
            
mam_mois_e()