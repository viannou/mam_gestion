# -*- coding: utf8 -*-
from osv import fields,osv

class mam_enfant(osv.Model):
    _name = 'mam.enfant'
    _description = "Enfant"
    def _get_nomprenom(self, cr, uid, ids, name, args, context=None):
        """nom affichable de l'enfant"""
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id]= record.prenom + " " + record.nom
        return result
    _columns = {
        'nom': fields.char('Nom',size=50,required=True, help='Nom de l''enfant'),
        'prenom': fields.char('Pr�nom',size=50,required=True, help='Pr�nom de l''enfant'),
        'nomprenom': fields.function(
            _get_nomprenom,
            type="char",
            string="Nom Complet",
            store=None,
            #select=True,
        ),
        'date_naiss': fields.date('Date de naissance',required=True, help='Date de naissance de l''enfant'),
        'am_id': fields.many2one('mam.am','Assistante maternelle de r�f�rence',required=True, help='Assistante maternelle de r�f�rence pour l''enfant'),
#liste des contacts
#        'rel_contact_id': fields.one2many('mam.rel_enfant_contact', 'enfant_id', 'Liste des contacts', help='Liste des contacts de l''enfant'),
        'contact_ids': fields.many2many('mam.contact','mam_enfant_contact_rel','contact_id','enfant_id',string="Contacts"),
        'allergies': fields.text('Allergies', help='Allergies de l''enfant'),
        'recommandations': fields.text('Recommandations g�n�rales', help='Recommandations g�n�rales pour l''enfant'),
#liste des contrats
    }
    _rec_name = 'nomprenom'
mam_enfant()
