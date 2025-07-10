# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import msal
import json

from odoo import http, fields
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


class TeamsController(http.Controller):

    @http.route('/callback', type='http', auth='public', csrf=False)
    def teams_callback(self, **kw):
        """Handle the callback from Microsoft authentication"""
        _logger.info("Received callback from Microsoft OAuth")

        code = kw.get('code')
        error = kw.get('error')
        error_description = kw.get('error_description')
        state = kw.get('state', '')

        # Extract connection ID from state
        connection_id = None
        if state and '_' in state:
            try:
                connection_id = int(state.split('_')[0])
                _logger.info(f"Extracted connection ID {connection_id} from state")
            except (ValueError, IndexError):
                _logger.error("Invalid state parameter format")

        if error:
            _logger.error(f"OAuth error: {error} - {error_description}")
            return http.Response(
                f"<html><body><h1>Authentication Error</h1><p>{error}: {error_description}</p></body></html>",
                status=400
            )

        if not code:
            _logger.error("No authorization code received in callback")
            return http.Response(
                "<html><body><h1>Authentication Error</h1><p>No authorization code received</p></body></html>",
                status=400
            )

        # Find the specific connection that initiated this auth flow
        connection = None
        if connection_id:
            connection = request.env['teams.connector'].sudo().browse(connection_id).exists()
            _logger.info(f"Found connection by ID: {bool(connection)}")

        # If we can't find it by ID, fall back to the original method
        if not connection:
            _logger.warning("Connection ID not found or invalid, falling back to default search")
            connection = request.env['teams.connector'].sudo().search([], limit=1)

        if not connection:
            _logger.error("No Microsoft Teams connection configuration found")
            return http.Response(
                "<html><body><h1>Configuration Error</h1><p>No Microsoft Teams connection configuration found</p></body></html>",
                status=500
            )

        try:
            if not connection.auth_flow:
                _logger.error(f"No auth flow data found in connection ID {connection.id}")
                return http.Response(
                    "<html><body><h1>Authentication Error</h1><p>No authentication flow data found. Please start the authentication process again.</p></body></html>",
                    status=400
                )

            flow_data = json.loads(connection.auth_flow)

            app = msal.ConfidentialClientApplication(
                connection.client_id,
                authority=f"https://login.microsoftonline.com/{connection.tenant_id}",
                client_credential=connection.client_secret,
            )

            result = app.acquire_token_by_auth_code_flow(
                flow_data,
                kw,
            )

            if "error" in result:
                _logger.error(f"Error acquiring token: {result.get('error')} - {result.get('error_description')}")
                return http.Response(
                    f"<html><body><h1>Token Error</h1><p>{result.get('error')}: {result.get('error_description')}</p></body></html>",
                    status=400
                )

            access_token = result.get('access_token')
            refresh_token = result.get('refresh_token')
            expires_in = result.get('expires_in')

            if access_token and expires_in:
                expiry = connection._get_token_expiry(expires_in)

                connection.sudo().write({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expiry': expiry,
                    'auth_flow': '',
                })
                _logger.info(f"Successfully updated tokens for connection ID {connection.id}")

                return request.redirect('/web#id=%s&model=teams.connector&view_type=form' % connection.id)

            else:
                _logger.error("No access token or expiry received in token response")
                return http.Response(
                    "<html><body><h1>Token Error</h1><p>No access token received</p></body></html>",
                    status=400
                )

        except Exception as e:
            _logger.exception(f"Exception in callback processing: {str(e)}")
            return http.Response(
                f"<html><body><h1>Error</h1><p>An error occurred: {str(e)}</p></body></html>",
                status=500
            )