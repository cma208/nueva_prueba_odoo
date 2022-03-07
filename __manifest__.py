{
    'name': 'My Library',
    'summary': "Manage books easily",
    'autor': "Your name",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '14',
    'depends': ['base', 'sale'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data_book.xml',
        'data/res.partner.csv',
        'data/library.book.csv',
        'views/library_book.xml',
        'views/library_book_categ.xml'
    ],
    'demo': ['demo.xml'],
}
