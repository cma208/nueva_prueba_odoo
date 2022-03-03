from odoo import models, fields, api
#from datetime import timedelta


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'  # para añadir un titulo mas user-friendly al modelo
    _order = 'date_release desc, name'  # ordena de el mas nuevo al mas antiguo, luego por el titulo
    _rec_name = 'short_name'
    _order = 'name'
    cost_price = fields.Float('Book Cost', digits='Book Price')
    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', required=True, translate=True,
                             index=True)  # to use as the record representation
    notes = fields.Text('Internal Notes')
    state = fields.Selection([('draft', 'Not Available'), ('available', 'Available'), ('lost', 'Lost')], 'State',
                             default="draft")
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of print?)')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependement=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4), )
    age_days = fields.Float(string='Days Since Release', compute='_compute_age', search='_search_age', store=False,
                            compute_sudo=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency'
    )
    author_ids = fields.Many2many(
        'res.partner', relation='relation_table', string='Authors',
    )
    published_book_ids = fields.One2many(
        'library.book', 'publisher_id', string='Published Books'
    )
    publisher_city = fields.Char(
        'Publisher City', related='publisher_id.city', readonly=True
    )
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher', ondolete='set null', context={}, domain={},
    )
    retail_price = fields.Monetary(
        'Retail Price', currency_field='currency_id'
    )
    authored_book_ids = fields.Many2many(
        'library.book', string='Authored Books', relation='library_book_res_partner_rel',
        count_books=fields.Integer('Number of Authored Books', compute='_compute_count_books')

    )
    _sql_contrains = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')


    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books=len(r.authored_book_ids)


    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0
