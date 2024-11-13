from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class HrPromotion(models.Model):
    _name = 'hr.promotion'
    _description = 'Employee Promotion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_name = fields.Char(
        string='Order Name',
        required=True,
        default=lambda self: _('New')
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

    effective_date = fields.Date(
        string='Effective Date',
        default=fields.Date.today
    )

    current_salary = fields.Monetary(
        string='Current Salary',
        compute='_compute_current_salary', store=True
    )




    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.company.currency_id.id)

    grade_id = fields.Many2one(
        'hr.payroll.structure.type',
        string='Grade',compute='_compute_current_salary', store=True
    )

    promoted_salary = fields.Monetary(
        string='Promoted Salary',

    )

    promoted_grade_id = fields.Many2one(
        'hr.payroll.structure.type',
        string='Promoted Grade'
    )

    promotion_line_ids = fields.One2many('hr.promotion.line', 'promotion_id', string="Promotion Lines")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr', 'HR'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')



    @api.model
    def create(self, vals):
        if not vals.get('order_name') or vals.get('order_name') == _('New'):
            current_year = date.today().year
            sequence_number = self.env['ir.sequence'].next_by_code('hr.promotion')
            if not sequence_number:
                raise UserError(_('Could not generate sequence number for HR promotion.'))
            vals['order_name'] = f"HR/PRO/{current_year}/{sequence_number}"
        return super(HrPromotion, self).create(vals)


    def action_submit(self):
        self.write({'state': 'hr'})


    def action_approve(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_create_invoice(self):
        print("Here we dont have nesessory fields so that we cannot create Invoice(fields needed for account.move.line)")

    @api.depends('employee_id')
    def _compute_current_salary(self):
        for salary in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', salary.employee_id.id),('state', '=', 'open')], limit=1)
            if contract:
                salary.current_salary = contract.wage
                salary.grade_id = contract.structure_type_id
            else:
                salary.current_salary = 0.0
                salary.grade_id = False



class HrPromotionLine(models.Model):
    _name = 'hr.promotion.line'
    _description = 'Employee Promotion Line'

    promotion_id = fields.Many2one('hr.promotion', string="Promotion", required=True, ondelete='cascade')

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.company.currency_id.id)


    salary_rule_id = fields.Many2one('hr.salary.rule',string='Salary Rule',required=True,domain="[('category_id.name', '=', 'Allowance')]")



    current_amount = fields.Monetary(
        string='Current Amount', compute='_compute_current_amount', store=True
    )
    new_amount = fields.Monetary(
        string='New Amount',compute='_compute_new_amount', store=True

    )

    @api.depends('salary_rule_id', 'promotion_id.employee_id')
    def _compute_current_amount(self):
        for line in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', line.promotion_id.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract and line.salary_rule_id:
                line.current_amount = contract.wage * line.salary_rule_id.amount_percentage / 100
            else:
                line.current_amount = 0.0

    @api.depends('salary_rule_id', 'promotion_id.promoted_grade_id')
    def _compute_new_amount(self):
        for line in self:
            if line.salary_rule_id and line.promotion_id.promoted_grade_id:
                grade_salary = line.promotion_id.promoted_grade_id.salary_rule_ids.filtered(lambda r: r.category_id.name == 'line.salary_rule_id.name')
                if grade_salary:
                    line.new_amount = grade_salary[0].amount * line.salary_rule_id.amount_percentage / 100
                else:
                    line.new_amount = 0.0
            else:
                line.new_amount = 0.0