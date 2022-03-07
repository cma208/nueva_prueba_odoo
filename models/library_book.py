from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


# from datetime import timedelta


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
    state = fields.Selection(
        [('draft', 'Not Available'), ('available', 'Available'), ('borrowed', 'Borrowed'), ('lost', 'Lost')], 'State',
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
        comodel_name='res.partner', relation='relation_table', string='Authors',
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
    """_sql_contrains = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]
    """

    def log_all_library_members(self):
        # this is an empty recordset of model library member
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS", all_members)
        return True

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'), ('available', 'borrowed'), ('borrowed', 'available'), ('available', 'lost'),
                   ('borrowedd', 'lost'), ('lost', 'available')]
        return (old_state, new_state) in allowed

    def predicate(book):
        if len(book.author_ids) > 1:
            return True
        return False

    def books_with_multiple_authors(self, all_books):
        return all_books.filter(lambda b: len(b.author_ids) > 1)

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s in not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def change_update_date(self):
        self.ensure_one()
        self.update({'date_release': fields.Datetime.now(), 'another_field': 'value'})

    def find_book(self):
        domain = ['|', '&', ('name', 'ilike', 'Book Name'), ('Category Name'), '&', ('name', 'ilike', 'Book Name 2'),
                  ('category_id.name', 'ilike', 'Category Name 2')]
        books = self.search(domain)
        print(books)

    def find_partner(self):
        PartnerObj = self.env['res.partner']
        domain = [('phone', '=', '1234')]
        partner = PartnerObj.search(domain)
        print(partner.name)


class LibraryBookRent(models.Model):
    _name = 'library.book.rent'
    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower', required=True)
    state = fields.Selection([('ongoing', 'Ongoing'), ('returned', 'Returned'), ('lost', 'Lost')], 'State',
                             default='ongoing', required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({'book_id': self.id, 'borrowe_id': self.env.user.partner_id.id})

    def book_lost(self):
        self.ensure_one()
        self.sudo().state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.sudo().make_lost()

    def make_lost(self):
        self.ensure_one()
        self.state = 'lost'
        if not self.env.context.get('avoid_deactivate'):
            self.active = False


class SaleOrder(models.Model):
    _inherit = "sale.order"
    name_2 = fields.Char('Segundo Cliente')
