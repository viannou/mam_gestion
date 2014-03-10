{
    "name" : "Gestion de MAM",
    "version" : "1.1",
    "author" : "Vianney Leclercq",
    "website" : "http://www.castelbambins.com/",
    "category" : "Tools",
    "description": """ Gestion de Maison d'Assistante Maternelle """,
    "depends" : ['base'],
    "data": [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'mam_presence_view.xml',
        'mam_enfant_view.xml',
        'mam_gestion_view.xml',
    ],
    "installable": True
}

