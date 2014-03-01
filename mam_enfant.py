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
            print enfant.id, enfant.nomprenom, context
            for date_d in (date.today() + timedelta(n) for n in range(90)):
                if date_d.weekday() == 5 or date_d.weekday() == 6:
                    continue
                print date_d
                jour_e = self.pool.get('mam.jour_e')
                jours_e_ids = jour_e.search(cr, uid, [('jour','=', date_d),('enfant_id','=',enfant.id)], context=context)
                if not jours_e_ids: # le jour de l'enfant n'existe pas encore
                    print "creation enfant ", enfant.nomprenom, " date ", date_d 
                    jour_e.create(cr, uid,{ 'jour': date_d,'enfant_id' : enfant.id,})
                    


        # for jour_type in self.browse(cr, uid, ids, context=context):
            # print jour_type.id, jour_type.libelle, jour_type.enfant_id.id, jour_type.enfant_id.nomprenom, context
            # #jour_e_ids = jour_type.enfant_id.jour_e_ids
        return True
mam_enfant()

