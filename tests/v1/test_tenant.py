import json

from flask_testing import TestCase
from mock import MagicMock, patch

from connector.app import app
from connector.config import Config
from connector.fbclient.reseller import Reseller
from connector.v1.resources import OACommunicationException
from connector.v1.resources.tenant import get_name_for_tenant
from tests.v1.utils import bypass_auth

config = Config()


class TestTenant(TestCase):
    def create_app(self):
        app.config.update({'TESTING': True})
        self.client = app.test_client()
        self.headers = {'Content-type': 'application/json',
                        'aps-instance-id': '123-123-123',
                        'aps-identity-id': '123-123-123',
                        'aps-controller-uri': 'https://localhost'}
        self.new_tenant = json.dumps({'aps': {'type': 'http://new.app', 'id': '123-123-123'},
                                      config.diskspace_resource: {'limit': 1000},
                                      'oaSubscription': {'aps': {'id': 555}},
                                      'oaAccount': {'aps': {'id': 555}}})
        self.diskless_tenant = json.dumps({'aps': {'type': 'http://new.app', 'id': '123-123-123'},
                                           'oaSubscription': {'aps': {'id': 555}},
                                           'oaAccount': {'aps': {'id': 555}}})

        return app

    @bypass_auth
    def test_new_tenant(self):
        with patch('connector.v1.resources.tenant.Client') as fake_client, \
                patch('connector.v1.resources.tenant.OA') as fake_oa:
            instance = fake_client.return_value
            instance.name = 'fake_company_name'
            instance.reseller = Reseller('fake_reseller')
            fake_oa.get_resource.side_effect = [{'companyName': 'fake_company'},
                                                {'subscriptionId': 555}]
            res = self.client.post('/v1/tenant', headers=self.headers, data=self.new_tenant)
            instance.create.assert_called()
        assert res.status_code == 201

    @bypass_auth
    def test_new_tenant_no_diskspace(self):
        with patch('connector.v1.resources.tenant.Client') as fake_client, \
                patch('connector.v1.resources.tenant.OA') as fake_oa:
            instance = fake_client.return_value
            instance.name = 'fake_company_name'
            instance.reseller = Reseller('fake_reseller')
            fake_oa.get_resource.side_effect = [{'companyName': 'fake_company'},
                                                {'subscriptionId': 555}]
            res = self.client.post('/v1/tenant', headers=self.headers, data=self.diskless_tenant)
            instance.create.assert_called()
        assert res.status_code == 201

    @bypass_auth
    def test_resource_usage(self):
        with patch('connector.v1.resources.tenant.Client') as fake_client, \
                patch('connector.v1.resources.tenant.get_name_for_tenant') as fake_name:
            instance = fake_client.return_value
            fake_name.return_value = 'fake_client'
            instance.users_by_type = {
                'default': 1,
                'gold': 2
            }
            instance.storage = {'usage': 1}
            res = self.client.get('/v1/tenant/123', headers=self.headers)
            data = res.json
            assert data[config.diskspace_resource]['usage'] == 1
            assert data[config.users_resource]['usage'] == 1
            assert res.status_code == 200

    @bypass_auth
    def test_update_tenant(self):
        with patch('connector.v1.resources.tenant.Client') as fake_client, \
                patch('connector.v1.resources.tenant.get_name_for_tenant') as fake_name:
            instance = fake_client.return_value
            fake_name.return_value = 'fake_client'
            res = self.client.put('/v1/tenant/123', headers=self.headers,
                                  data=self.new_tenant)
            instance.update.assert_called()
            assert res.status_code == 200

    @bypass_auth
    def test_delete_tenant(self):
        with patch('connector.v1.resources.tenant.Client') as fake_client, \
                patch('connector.v1.resources.tenant.get_name_for_tenant') as fake_name:
            fake_name.return_value = 'fake_client'
            instance = fake_client.return_value
            res = self.client.delete('/v1/tenant/123', headers=self.headers)
            instance.delete.assert_called()
            assert res.status_code == 204

    @bypass_auth
    def test_tenant_disable(self):
        res = self.client.put('/v1/tenant/123/disable', headers=self.headers)
        assert res.status_code == 200

    @bypass_auth
    def test_tenant_enable(self):
        res = self.client.put('/v1/tenant/123/enable', headers=self.headers)
        assert res.status_code == 200

    @bypass_auth
    def test_admin_login(self):
        with patch('connector.v1.resources.tenant.get_name_for_tenant') as fake_name, \
                patch('connector.v1.resources.tenant.g') as fake_g, \
                patch('connector.v1.resources.tenant.OA'), \
                patch('connector.v1.resources.tenant.FbUser') as fake_user:
            fake_name.return_value = 'fake_client'
            fake_g.reseller = Reseller('fake_reseller')
            user_instance = fake_user.return_value
            user_instance.login_link.return_value = 'login_link_with_token'
            res = self.client.get('/v1/tenant/123/adminlogin', headers=self.headers)
            assert res.status_code == 200
            assert b'token' in res.data

    @bypass_auth
    def test_admin_login_no_user_in_oa(self):
        with patch('connector.v1.resources.tenant.get_name_for_tenant') as fake_name, \
                patch('connector.v1.resources.tenant.g') as fake_g, \
                patch('connector.v1.resources.tenant.OA') as fake_oa, \
                patch('connector.v1.resources.tenant.FbUser') as fake_user:
            fake_name.return_value = 'fake_client'
            fake_g.reseller = Reseller('fake_reseller')
            fake_oa_response = MagicMock()
            fake_oa_response.status_code = 404
            fake_oa_response.text = 'Get user from OA failed'
            fake_oa.get_resource.side_effect = OACommunicationException(fake_oa_response)
            user_instance = fake_user.return_value
            user_instance.login_link.return_value = 'login_link_for_manual_login'
            res = self.client.get('/v1/tenant/123/adminlogin', headers=self.headers)
            assert res.status_code == 200

    def test_get_name_for_tenant(self):
        with patch('connector.v1.resources.tenant.OA') as fake_oa:
            fake_oa.get_resource.return_value = {'tenantId': 'fake_client'}
            assert get_name_for_tenant('123-123-123') == 'fake_client'

    def test_get_name_for_tenant_fail(self):
        with patch('connector.v1.resources.tenant.OA') as fake_oa:
            fake_oa.get_resource.return_value = {}
            self.assertRaises(KeyError, get_name_for_tenant, 'broken_tenant')

    @bypass_auth
    def test_tenant_delete_user(self):
        res = self.client.delete('/v1/tenant/123/users/123', headers=self.headers)
        assert res.status_code == 200

    @bypass_auth
    def test_tenant_new_user(self):
        res = self.client.post('/v1/tenant/123/users', headers=self.headers)
        assert res.status_code == 200
