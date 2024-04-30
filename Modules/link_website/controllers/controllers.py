import requests
from odoo import http, _
from odoo.http import request
from bs4 import BeautifulSoup
import logging

_logger = logging.getLogger(__name__)


class LinkWebsite(http.Controller):

    @http.route('/create_leads', auth='user', type="json", methods=['POST'])
    def create_lead(self, **kw):
        # Define custom headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Fetching leads from the website
        website_url = 'https://analytix.sa/contact-us/'
        try:
            response = requests.get(website_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to fetch website content: %s", str(e))
            return {'error': _('Failed to fetch website content: %s' % e)}

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract values from input fields
        try:
            name = soup.find('input', {'name': 'form_fields[name]'}).get('value')
            email = soup.find('input', {'name': 'form_fields[email]'}).get('value')
            phone = soup.find('input', {'name': 'form_fields[field_f7ffd51]'}).get('value')
            subject = soup.find('input', {'name': 'form_fields[field_2951a7b]'}).get('value')
            comment = soup.find('textarea', {'name': 'form_fields[field_35a2b21]'}).text.strip()
        except AttributeError as ae:
            _logger.error("Error parsing HTML content: %s", str(ae))
            return {'error': _('Error parsing HTML content: %s' % ae)}

        try:
            # Creating
            lead = request.env['link_website.link_website'].sudo().create({
                'name': name,
                'email': email,
                'phone': phone,
                'msg': comment,
            })

            _logger.debug("Lead created with ID: %s", lead.id)
            return {'lead_id': lead.id}
        except Exception as ex:
            _logger.error("Failed to create lead: %s", str(ex))
            return {'error': _('Failed to create lead: %s' % ex)}
