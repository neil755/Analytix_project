# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import msal
import json
import secrets

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TeamsConnector(models.Model):
    _name = 'teams.connector'
    _description = 'Microsoft Teams Connector'

    @api.model
    def default_get(self, fields):
        res = super(TeamsConnector, self).default_get(fields)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        res['redirect_url'] = base_url + '/callback'
        return res

    name = fields.Char("Name")
    client_id = fields.Char(
        string="Client Id",
        help="Application (client) ID of application you have registered on Azure -> Microsoft Entra ID -> App registrations",
    )
    client_secret = fields.Char(
        string="Client Secret",
        help="Client secret generated for your application in Azure -> Microsoft Entra ID -> App registrations -> Certificates & secrets",
    )
    tenant_id = fields.Char(
        string="Tenant Id",
        help="Directory (tenant) ID found in Azure -> Microsoft Entra ID -> Overview",
    )
    redirect_url = fields.Char(
        string="Redirect URL",
        help="This must match one of the redirect URIs specified in your Azure app registration.",
    )
    access_token = fields.Char("Access Token")
    refresh_token = fields.Text("Refresh Token")
    token_expiry = fields.Datetime("Token Expiry")
    auth_flow = fields.Text("Auth Flow", help="Stores the authentication flow context")
    connection_state = fields.Selection([
        ('not_connected', 'Not Connected'),
        ('connected', 'Connected'),
    ], default='not_connected', string="Connection Status", compute="_compute_connection_state")

    @api.depends('access_token', 'token_expiry')
    def _compute_connection_state(self):
        for record in self:
            if not record.access_token:
                record.connection_state = 'not_connected'
            else:
                record.connection_state = 'connected'

    def microsoft_bearer_token(self):
        """Generate Microsoft Power BI authentication URL or refresh token if expired"""
        if not self.client_id or not self.tenant_id or not self.client_secret:
            raise ValidationError(_("Client ID, Tenant ID, and Client Secret are required!"))

        if self.token_expiry and self.token_expiry < fields.Datetime.now():
            return self.refresh_access_token()

        # If the token is still valid, don't refresh it
        if self.token_expiry and self.token_expiry >= fields.Datetime.now():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Power BI is already connected and the token is valid.'),
                    'sticky': False,
                    'type': 'success'
                }
            }

        # If there's no valid token and no refresh token, start authentication flow
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret,
            )

            # Include the connection ID in the state parameter
            state = f"{self.id}_{secrets.token_urlsafe(24)}"

            flow = app.initiate_auth_code_flow(
                scopes=["https://graph.microsoft.com/.default"],
                redirect_uri=self.redirect_url,
                state=state,
                prompt="login"  # Force showing login page
            )

            self.auth_flow = json.dumps(flow)
            return {'type': 'ir.actions.act_url', 'url': flow["auth_uri"], 'target': 'self'}

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': _('Error'), 'message': str(e), 'sticky': True, 'type': 'danger'}
            }

    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        self.ensure_one()

        if not self.refresh_token:
            raise ValidationError("Reauthorization required.")
        if self.token_expiry and self.access_token and fields.Datetime.now() < self.token_expiry:
            return

        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret,
            )

            result = app.acquire_token_by_refresh_token(
                self.refresh_token,
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "error" in result:
                raise ValidationError(_(f"Error refreshing token: {result.get('error_description', 'Unknown error')}"))

            access_token = result.get('access_token')
            refresh_token = result.get('refresh_token', self.refresh_token)
            expires_in = result.get('expires_in')

            if access_token and expires_in:
                now = fields.Datetime.now()
                expiry = now + timedelta(seconds=expires_in)
                self.write({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expiry': expiry,
                })
                return True
            else:
                raise ValidationError(
                    _("No access token received when refreshing"))

        except Exception as e:
            raise ValidationError(_(f"Failed to refresh token: {str(e)}"))

    def _get_token_expiry(self, expires_in):
        """Calculate token expiry datetime from expires_in seconds"""
        return datetime.now() + timedelta(seconds=expires_in)
