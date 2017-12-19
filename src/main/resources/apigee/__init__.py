#
# Copyright 2017 XebiaLabs, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import requests
from requests.packages.urllib3.exceptions import SNIMissingWarning, InsecurePlatformWarning, InsecureRequestWarning
import onetimepass as otp


# The variable authorizationHeader has always the same value
authorizationHeader = "ZWRnZWNsaTplZGdlY2xpc2VjcmV0"


def setup_urllib():
    requests.packages.urllib3.disable_warnings(SNIMissingWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ApigeeClient(object):

    def __init__(self, organization, target_environment=None):
        self.organization = organization
        if target_environment is not None:
            self.target_environment = target_environment.environmentName
        self.authentication = (organization.username, organization.password)
        self.mfa = organization.mfa
        self.sso_login_url = "https://login.apigee.com/oauth/token"
        self.proxy_dict = None
        if organization.proxy:
            address = organization.proxy.address
            idx = address.index(':')
            self.proxy_dict = {address[0:idx]: address + ":" + str(organization.proxy.port)}

    def check_organization_connection(self):
        url = self.build_org_url()
        authorization_headers = self.build_authorization_header()
        print(url)
        headers = authorization_headers
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.get(url, proxies=self.proxy_dict, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.get(url, auth=self.authentication, proxies=self.proxy_dict, verify=False, headers=headers)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during checking the connection of Apigee organization")
        return resp

    def import_api_proxy(self, api_proxy, path):
        url = self.build_org_url() + '/apis'
        params = {'action': 'import', 'name': api_proxy}
        authorization_headers = self.build_authorization_header()
        print(url)
        headers = authorization_headers
        filename = path.split('/')[-1]
        data = {'file': (filename, open(path, 'rb'), 'application/binary')}
        headers['Content-Type'] = 'multipart/form-data'
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.post(url, params=params, proxies=self.proxy_dict, verify=False, headers=headers, files=data)
        else:
            print("Multi factor authentication is off")
            resp = requests.post(url, auth=self.authentication, params=params, proxies=self.proxy_dict, verify=False, headers=headers, files=data)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during importing of Apigee: %s" % (api_proxy))
        return resp

    def import_shared_flow(self, shared_flow, path):
        url = self.build_org_url() + '/sharedflows'
        params = {'action': 'import', 'name': shared_flow}
        authorization_headers = self.build_authorization_header()
        print(url)
        headers = authorization_headers
        filename = path.split('/')[-1]
        data = {'file': (filename, open(path, 'rb'), 'application/binary')}
        headers['Content-Type'] = 'multipart/form-data'
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.post(url, params=params, proxies=self.proxy_dict, verify=False, headers=headers, files=data)
        else:
            print("Multi factor authentication is off")
            resp = requests.post(url, auth=self.authentication, params=params, proxies=self.proxy_dict, verify=False, headers=headers, files=data)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during importing of Apigee: %s" % (api_proxy))
        return resp

    def delete_api_proxy_revision(self, api_proxy, api_proxy_revision):
        url = self.build_org_url()
        url = url + "/apis/" + api_proxy
        return self.delete_revision(url, api_proxy, api_proxy_revision)

    def delete_shared_flow_revision(self, shared_flow, shared_flow_revision):
        url = self.build_org_url()
        url = url + "/sharedflows/" + shared_flow
        return self.delete_revision(url, shared_flow, shared_flow_revision)

    def delete_revision(self, url, api_proxy, api_proxy_revision):
        url = url + "/revisions/" + api_proxy_revision
        print(url)
        authorization_headers = self.build_authorization_header()
        headers = authorization_headers
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.delete(url, proxies=self.proxy_dict, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.delete(url, proxies=self.proxy_dict, verify=False, auth=self.authentication)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during removing of Apigee: %s/%s" % (api_proxy, api_proxy_revision))
        return resp

    def deploy_api_proxy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_api_proxy_url(api_proxy, revision)
        return self.deploy(url, api_proxy, api_proxy_revision)

    def deploy_shared_flow(self, shared_flow, shared_flow_revision):
        revision = self.parse_revision(shared_flow_revision)
        url = self.build_shared_flow_url(shared_flow, revision)
        return self.deploy(url, shared_flow, shared_flow_revision)

    def deploy(self, url, api_proxy, api_proxy_revision):
        url = url + "/deployments"
        params = {'override': 'true'}
        authorization_headers = self.build_authorization_header()
        print(url)
        headers = authorization_headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.post(url, params=params, proxies=self.proxy_dict, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.post(url, auth=self.authentication, params=params, proxies=self.proxy_dict, verify=False, headers=headers)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during deployment of Apigee: %s/%s to environment %s" % (api_proxy, api_proxy_revision, self.target_environment))
        return resp

    def undeploy_api_proxy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_api_proxy_url(api_proxy, revision)
        return self.undeploy(url, api_proxy, api_proxy_revision)

    def undeploy_shared_flow(self, shared_flow, shared_flow_revision):
        revision = self.parse_revision(shared_flow_revision)
        url = self.build_shared_flow_url(shared_flow, revision)
        return self.undeploy(url, shared_flow, shared_flow_revision)

    def undeploy(self, url, api_proxy, api_proxy_revision):
        url = url + "/deployments"
        print(url)
        authorization_headers = self.build_authorization_header()
        headers = authorization_headers
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.delete(url, proxies=self.proxy_dict, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.delete(url, proxies=self.proxy_dict, verify=False, auth=self.authentication)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during undeployment of Apigee: %s/%s from environment %s" % (api_proxy, api_proxy_revision, self.target_environment))
        return resp

    def create_one_time_password(self):
        my_secret = self.organization.secretKey
        if my_secret is None:
            raise Exception("Error during creating one time password. The secret key is empty.")
        my_token = otp.get_totp(my_secret)
        if len(str(my_token)) == 5:
            my_token = "0%s" % my_token
        return my_token

    def build_authorization_header(self):
        # Check the connection with an http head request. Otherwise, the password is printed when mfa is on.
        resp = requests.head(self.sso_login_url, proxies=self.proxy_dict, verify=False)
        authorization_headers = {}
        if self.mfa:
            my_token = self.create_one_time_password()
            headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Accept': 'application/json;charset=utf-8', 'Authorization': 'Basic ' + authorizationHeader}
            params = {'username': self.organization.username, 'password': self.organization.password, 'grant_type': 'password', 'mfa_token': my_token}
            resp = requests.post(self.sso_login_url, params=params, proxies=self.proxy_dict, verify=False, headers=headers)
            if resp.status_code > 399:
                print(resp.status_code)
                print(resp.json())
                raise Exception("Error during creating authorization header")
            data = resp.json()
            access_token = data['access_token']
            authorization_headers = {'Authorization': 'Bearer ' + access_token}
        return authorization_headers

    def build_org_url(self):
        base_url = self.organization.url
        url = base_url + "/v1/organizations/" + self.organization.organizationName
        return url

    def build_api_proxy_url(self, api_proxy, api_proxy_revision):
        url = self.build_org_url()
        url = url + "/environments/" + self.target_environment
        url = url + "/apis/" + api_proxy
        url = url + "/revisions/" + api_proxy_revision
        return url

    def build_shared_flow_url(self, shared_flow, shared_flow_revision):
        url = self.build_org_url()
        url = url + "/environments/" + self.target_environment
        url = url + "/sharedflows/" + shared_flow
        url = url + "/revisions/" + shared_flow_revision
        return url

    def parse_revision(self, revision):
        if revision.startswith('rev'):
            return revision[3:]
        return revision
