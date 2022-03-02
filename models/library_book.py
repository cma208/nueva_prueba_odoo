from odoo import models, fields, api


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'  # para añadir un titulo mas user-friendly al modelo
    _order = 'date_release desc, name'  # ordena de el mas nuevo al mas antiguo, luego por el titulo
    _rec_name = 'short_name'
    cost_price = fields.Float('Book Cost', digits='Book Price')
    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', required=True, translate=True,
                             index=True)  # to use as the record representation
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Not Available'), ('available', 'Available'), ('lost', 'Lost')], 'State', default="draft")
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of print?)')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependement=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4), )
    currency_id = fields.Many2one(
        'res.currency', string='Currency'
    )
    author_ids = fields.Many2many(
        'res.partner', relation='relation_table', string='Authors',
    )
    published_book_ids = fields.One2many(
        'library.book', 'publisher_id', string='Published Books'
    )
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher', ondolete='set null', context={}, domain={},
    )
    retail_price = fields.Monetary(
        'Retail Price', currency_field='currency_id'
    )
    authored_book_ids = fields.Many2many(
        'library.book', string='Authored Books', relation='library_book_res_partner_rel'
    )
    _sql_contrains=[
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'), ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

