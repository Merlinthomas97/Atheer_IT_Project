{
    'name': 'Employee Promotion ',
    'category': 'Custom',
    'summary': 'Module For Employee Promotion',
    'author': 'Merlin',
    'description': 'Implementing a Promotion system',
    'depends': ['base', 'hr','hr_contract','hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/employee_promotion.xml',
        'views/menu_action.xml',
    ],
    'installable': True,
    'application': True,
}