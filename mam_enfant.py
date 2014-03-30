# -*- coding: utf8 -*-
from osv import fields,osv
from datetime import datetime,date,timedelta

class mam_enfant(osv.Model):
    _name = 'mam.enfant'
    _description = "Enfant"
    def _get_nomprenom(self, cr, uid, ids, name, args, context=None):
        """nom affichable de l'enfant """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= record.prenom + " " + record.nom
        return result
    def _get_age_mois(self, cr, uid, ids, name, args, context=None):
        """calcul l'age de l'enfant """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= (date.today() - datetime.strptime(record.date_naiss,'%Y-%m-%d')).days / 30
        return result
    # def _get_today_info(self, cr, uid, ids, name, args, context=None):
        # """toutes les infos d'aujourd'hui"""
        # result = dict()
        # for enfant in self.browse(cr, uid, ids, context=context):
            # result[enfant.id] = dict()
            # result[enfant.id]['today_presence_ids'] = list()
            # result[enfant.id]['today_est_present'] = False
            # result[enfant.id]['today_mange_midi'] = False
            # result[enfant.id]['today_mange_gouter'] = False
            # for presence in enfant.presence_ids:
                # date_debut = datetime.strptime(presence.date_debut,'%Y-%m-%d %H:%M:%S')
                # if date_debut.date() == date.today():
                    # result[enfant.id]['today_presence_ids'].append(presence.id)
                    # if date_debut < datetime.now():
                        # if presence.date_fin is False or datetime.strptime(presence.date_fin,'%Y-%m-%d %H:%M:%S') > datetime.now():
                            # result[enfant.id]['today_est_present'] = True
                            # result[enfant.id]['today_cur_presence'] = presence.id
                    # if presence.mange_midi:
                        # result[enfant.id]['today_mange_midi'] = True
                    # if presence.mange_gouter:
                        # result[enfant.id]['today_mange_gouter'] = True
        # return result
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
        'age_mois': fields.function(
            _get_age_mois,
            type="integer",
            string="Age en mois",
            store=None,
            #select=True,
        ),
        'am_id': fields.many2one('mam.am','Assistante maternelle de référence',required=True, help='Assistante maternelle de référence pour l''enfant'),
        'contact_ids': fields.many2many('mam.contact','mam_enfant_contact_rel','contact_id','enfant_id',string="Contacts"),
        'allergies': fields.text('Allergies', help='Allergies de l''enfant'),
        'recommandations': fields.text('Recommandations générales', help='Recommandations generales pour l''enfant'),
        'jour_e_ids': fields.one2many('mam.jour_e', 'enfant_id', 'Liste des jours', help='Liste des jours de presences de l''enfant'),
        'jour_type_ids': fields.one2many('mam.jour_type', 'enfant_id', 'Liste des jours types', help='Liste des jours types de l''enfant'),
        # 'today_presence_ids': fields.function(
            # _get_today_info,
            # string="Présences aujourd'hui",
            # type="one2many",
            # obj="mam.presence_e",
            # field="enfant_id",
            # multi=True,
        # ),
        # 'today_est_present': fields.function(
            # _get_today_info,
            # string="Présent en ce moment",
            # type="boolean",
            # multi=True,
        # ),
        # 'today_cur_presence': fields.function(
            # _get_today_info,
            # string="Présence en ce moment",
            # type="many2one",
            # obj="mam.presence_e",
            # multi=True,
        # ),
        # 'today_mange_midi': fields.function(
            # _get_today_info,
            # string="Mange aujourd'hui",
            # type="boolean",
            # multi=True,
        # ),
        # 'today_mange_gouter': fields.function(
            # _get_today_info,
            # string="Mange aujourd'hui",
            # type="boolean",
            # multi=True,
        # ),
        # 'today_resume': fields.function(
            # _get_today_info,
            # string="Résumé",
            # type="char",
            # multi=True,
        # ),
    }
    _rec_name = 'nomprenom'
    _order = "prenom"
    # def clique_presence_debut(self, cr, uid, ids, context=None):
        # """ajoute une présence """
        # for enfant in self.browse(cr, uid, ids, context=context):
            # self.pool.get('mam.presence_e').create(cr, uid, {'enfant_id':enfant.id, 'date_debut':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        # return True
    # def clique_presence_fin(self, cr, uid, ids, context=None):
        # """termine une présence """
        # for enfant in self.browse(cr, uid, ids, context=context):
            # self.pool.get('mam.presence_e').write(cr, uid, enfant.today_cur_presence.id, {'date_fin':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        # return True
    # def clique_mange_midi(self, cr, uid, ids, context=None):
        # """coche ou décoche mange midi """
        # for enfant in self.browse(cr, uid, ids, context=context):
            # inverse = not enfant.today_mange_midi
            # for presence in enfant.today_presence_ids:
                # self.pool.get('mam.presence_e').write(cr, uid, presence.id, {'mange_midi':inverse})
        # return True
    # def clique_mange_gouter(self, cr, uid, ids, context=None):
        # """coche ou décoche mange gouter """
        # for enfant in self.browse(cr, uid, ids, context=context):
            # inverse = not enfant.today_mange_gouter
            # for presence in enfant.today_presence_ids:
                # self.pool.get('mam.presence_e').write(cr, uid, presence.id, {'mange_gouter':inverse})
        # return True

    def action_creer_jours(self, cr, uid, ids, context=None):
        """ajoute pour l'enfant sélectionné le jour type sélectionné pour les 90 jours à venir (sauf samedi dimanche)"""
        for enfant in self.browse(cr, uid, ids, context=context):
            mam_jour_e = self.pool.get('mam.jour_e')
            # créer les jours
            for date_d in (date.today() + timedelta(n) for n in range(90)):
                if date_d.weekday() == 5 or date_d.weekday() == 6:
                    continue
                print date_d
                jour_e_ids = mam_jour_e.search(cr, uid, [('jour','=', date_d),('enfant_id','=',enfant.id)], context=context)
                if not jour_e_ids: # le jour de l'enfant n'existe pas encore
                    print "creation enfant ", enfant.id, " date ", date_d 
                    mam_jour_e.create(cr, uid,{ 'jour': date_d,'enfant_id' : enfant.id,})
        return True
mam_enfant()


class mam_contrat(osv.Model):
    _name = 'mam.contrat'
    _description = "Contrat"
    TYPE_CONTRAT = [
        (u'normal', u'Contrat normal'),
        (u'garderie', u'Contrat occasionnel'),
    ]
    TYPE_CONTRAT_dict = dict(TYPE_CONTRAT)
    _columns = {
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par le contrat'),
        'am_id': fields.many2one('mam.am','Assistante maternelle de référence',required=True, help='Assistante maternelle de référence pour le contrat'),
        'contact_id': fields.many2one('mam.contact','Signataire',required=True, help='Personne signataire du contrat'),
        'avenant_ids': fields.one2many('mam.avenant', 'contrat_id', 'Liste des avenants', help='Liste des avenants au contrat'),
        'type': fields.selection(TYPE_CONTRAT, 'Type',required=True,  help='Type de contrat'),
    }
    # _rec_name = 'libelle'
    _defaults = {
        'type': 'normal',
    }
    _order = "enfant_id"
mam_contrat()

class mam_avenant(osv.Model):
    _name = 'mam.avenant'
    _description = "Avenant"
    def _get_libelle(self, cr, uid, ids, name, args, context=None):
        """nom affichable de l'avenant """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= record.contrat_id.enfant_id.nomprenom + " " + str(record.date_debut)
        return result
    # def _get_calculs(self, cr, uid, ids, name, args, context=None):
        # """nom affichable de la presence """
        # result = {}
        # for record in self.browse(cr, uid, ids, context=context):
            # result[record.id] = {}
            # result[record.id]['nb_j_total'] = record.nb_j_par_s * record.nb_s_par_a
            # result[record.id]['nb_h_par_an'] = record.nb_h_par_j * record.nb_j_par_s * record.nb_s_par_a
            # result[record.id]['nb_h_total'] = record.nb_h_par_j * record.nb_j_par_s * record.nb_s_par_a
            # result[record.id]['nb_h_par_s'] = record.nb_h_par_j * record.nb_j_par_s
        # return result
    _columns = {
        'contrat_id': fields.many2one('mam.contrat','Contrat',required=True, help='Contrat concerné par l''avenant'),
        'date_debut': fields.date('Date de début',required=True, help='Date de début de l''avenant'),
        'date_fin': fields.date('Date de fin', help='Date de fin de l''avenant'),
        'libelle': fields.function(
            _get_libelle,
            type="char",
            string="Libelle",
            store=None,
            #select=True,
        ),
        # 'nb_h_par_j': fields.integer('Nombre d''heures par jour',required=True, help='Nombre d''heures par jour au contrat'),
        # 'nb_j_par_s': fields.integer('Nombre de jours par semaine',required=True, help='Nombre de jours par semaine au contrat'),
        # 'nb_s_par_a': fields.integer('Nombre de semaines par an',required=True, help='Nombre de semaines par an au contrat'),
       'nb_h_par_an': fields.integer("Nombre d'heures par an",required=True, help="Nombre d'heures par an"),
        # "nb_j_total": fields.function(_get_calculs, type="integer", string="Nombre de jours total de présence", store=True, multi='les_calculs', ),
        # "nb_h_par_an": fields.function(_get_calculs, type="integer", string="Nombre d'heures total de présence", store=True, multi='les_calculs', ),
        # "nb_h_total": fields.function(_get_calculs, type="integer", string="Nombre d'heures total de présence", store=True, multi='les_calculs', ),
        # "nb_h_par_s": fields.function(_get_calculs, type="integer", string="Nombre d'heures par semaine", store=True, multi='les_calculs', ),
# montant mensualisé net
# montant mensualisé brut
    }
    def action_creer_mois(self, cr, uid, ids, context=None):
        """crée les mois inexistant pour l'avenant"""
        for avenant in self.browse(cr, uid, ids, context=context):
            print "creer mois", str(avenant.libelle)
            mam_jour_e = self.pool.get('mam.jour_e')
            mam_mois_e = self.pool.get('mam.mois_e')
            # créer les mois par rapport aux jours existants
            jour_e_ids = mam_jour_e.search(cr, uid, [('enfant_id','=',avenant.contrat_id.enfant_id.id)], context=context)
            liste = []
            for jour_e in mam_jour_e.browse(cr, uid, jour_e_ids, context=context):
                if jour_e.jour >= avenant.date_debut and (not avenant.date_fin or jour_e.jour <= avenant.date_fin):
                    jour = datetime.strptime(jour_e.jour,'%Y-%m-%d')
                    if not (avenant.id, jour.year, jour.month) in liste:
                        liste.append( (avenant.id, jour.year, jour.month) )
                        mois_e_ids = mam_mois_e.search(cr, uid, [('avenant_id','=',avenant.id),('annee','=', jour.year),('mois','=', jour.month)], context=context)
                        if not mois_e_ids: # le mois de l'avenant n'existe pas encore
                            print "cree mois avenant ", avenant.id, " annee ", jour.year, " mois ", jour.month 
                            mam_mois_e.create(cr, uid,{ 'annee': jour.year,'mois': jour.month,'avenant_id' : avenant.id,})
        return True
    _rec_name = 'libelle'
    _order = "date_debut"
mam_avenant()

