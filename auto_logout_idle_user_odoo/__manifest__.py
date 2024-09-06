{
    'name': 'Logout Idle User',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': """Auto logout idle user with fixed time""",
    'description': """User can fix the timer in the user's profile, if the user
     is in idle mode the user will logout from session automatically """,
    'author': 'Neil Antony',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/res_users_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/auto_logout_idle_user_odoo/static/src/xml/systray.xml',
            '/auto_logout_idle_user_odoo/static/src/js/systray.js',
            '/auto_logout_idle_user_odoo/static/src/css/systray.css'
        ],
    },
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
