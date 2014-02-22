# -*- coding: utf8 -*-
from osv import fields,osv

class mam_jour(osv.Model):
	_name = 'mam.jour'
	_description = "Jour"
	_columns = {
        "fullname": fields.function(
            _get_fullname,
            type="char",
            string="Full Name",
            store=None,
            #select=True,
		)
	}
	_rec_name = 'prenom'

    def _get_fullname(self, cr, uid, ids, name, args, context=None):
        """Test de field function"""
        result = dict()
        for id in ids:
            result[id] = "ah " + id
        return result



mam_jour()

