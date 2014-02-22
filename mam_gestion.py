# -*- coding: utf8 -*-
from osv import fields,osv

class mam_am(osv.Model):
    _name = 'mam.am'
    _description = "Assistante maternelle"
    def _get_nomprenom(self, cr, uid, ids, name, args, context=None):
        """nom affichable de l'am"""
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= record.prenom + " " + record.nom
        return result
    _columns = {
        'nom': fields.char('Nom',size=50,required=True, help='Nom de l''assistante maternelle'),
        'prenom': fields.char('Prénom',size=50,required=True, help='Prénom de l''assistante maternelle'),
        'nomprenom': fields.function(
            _get_nomprenom,
            type="char",
            string="Nom Complet",
            store=None,
            #select=True,
        ),
        'date_naiss': fields.date('Date de naissance',required=True, help='Date de naissance de l''assistante maternelle'),
        'date_embauche': fields.date('Date d''embauche',required=True, help='Date d''embauche de l''assistante maternelle'),
        'num_sal': fields.char('Numéro de salarié',size=50,required=True, help='Numéro de salarié de l''assistante maternelle'),
        'num_ss': fields.char('Numéro de Sécurité Sociale',size=50,required=True, help='Numéro de Sécurité Sociale de l''assistante maternelle'),
        'adresse': fields.text('Adresse',required=True, help='Adresse complète de l''assistante maternelle'),
        'tel_fixe': fields.char('Téléphone fixe',size=20, help='Téléphone fixe de l''assistante maternelle'),
        'tel_mobile': fields.char('Téléphone mobile',size=20, help='Téléphone mobile de l''assistante maternelle'),
        'date_agrement': fields.date('Date dernier agrément',required=True, help='Date de la dernière décision d''agrément de l''assistante maternelle'),
        'nb_agrements': fields.char('Nombre d''agréments',size=50,required=True, help='Nombre d''agréments total de l''assistante maternelle'),
    }
    _rec_name = 'nomprenom'
mam_am()

class mam_contact(osv.Model):
    _name = 'mam.contact'
    _description = "Contact"
    _columns = {
        'nom': fields.char('Nom',size=50,required=True, help='Nom du contact'),
        'prenom': fields.char('Prénom',size=50,required=True, help='Prénom du contact'),
        'adresse': fields.text('Adresse', help='Adresse complète du contact'),
        'tel_fixe': fields.char('Téléphone fixe',size=20, help='Téléphone fixe du contact'),
        'tel_mobile': fields.char('Téléphone mobile',size=20, help='Téléphone mobile du contact'),
#        'rel_enfant_id': fields.one2many('mam.rel_enfant_contact', 'contact_id', 'Liste des enfants', help='Liste des enfants du contact'),
        'enfant_ids': fields.many2many('mam.enfant','mam_enfant_contact_rel','enfant_id','contact_id',string="Enfants associés"),
    }
    _rec_name = 'prenom'
mam_contact()

class mam_presence_e(osv.Model):
    _name = 'mam.presence_e'
    _description = "Presence de l'enfant"
    _columns = {
        'enfant_id': fields.many2one('mam.enfant','Enfant',required=True, help='Enfant concerné par la présence'),
        'est_reel': fields.boolean('Présence/absence réelle', help='Décoché = présence prévisionnelle'), # REEL, PREV, POSS
        'type': fields.selection((('PRE','Présence normale'), ('MAL','Malade (avec certif)'), ('MAB','Malade longue durée'), ('ABS','Absent'), ('AMA','Absent car manque Ass. Mat.')), 'Type'), # MAL, MAB, ABS, AMA
        'date_debut': fields.datetime('Début de présence',required=True, help='Date/heure de début de présence de l''enfant'),
        'date_fin': fields.datetime('Fin de présence', help='Date/heure de fin de présence de l''enfant'),
        'mange_midi': fields.boolean('Mange le midi', help='Prise du repas du midi'),
        'mange_gouter': fields.boolean('Mange au gouter', help='Prise du gouter'),
        'commentaire': fields.text('Commentaire journée', help='Commentaire sur la présence ou l''absence'),
    }
    defaults = {
        'est_reel': True,
        'type': 'PRE',
    }
mam_presence_e()
#???
#def default_get(self, cr, uid, fields, context=None):
#    res = super(jbbookmark_jbbookmark, self).default_get(cr, uid, fields,     context=context)
#    res['name'] = 'initial value test'
#    res['description'] = 'initial value test'
#    return res


#class mam_rel_enfant_contact(osv.Model):
#    _name = 'mam.rel_enfant_contact'
#    _description = "Relation Enfants - Contacts"
#    _columns = {
#        'enfant_id': fields.many2one('mam.enfant','Enfant', help='Enfant en relation avec le contact'),
#        'contact_id': fields.many2one('mam.contact','Contact', help='Contact en relation avec l''enfant'),
#        'relation': fields.selection((('pere','Père'), ('maman','Mère'), ('parent','Parent'), ('ami','Ami des parents'), ('medecin','Medecin')), 'Relation'),
##type de relation
#    }
#mam_rel_enfant_contact()

