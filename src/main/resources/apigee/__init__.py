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

    def __init__(self, organization, target_environment):
        self.organization = organization
        self.target_environment = target_environment
        self.authentication = (organization.username, organization.password)
        self.mfa = organization.mfa
        self.sso_login_url = "https://login.apigee.com/oauth/token"

    def deploy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_url(api_proxy, revision)
        url = url + "/deployments"
        params = {'override': 'true'}
        authorization_headers = self.build_authorization_header()
        print(url)
        headers = authorization_headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.post(url, params=params, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.post(url, auth=self.authentication, params=params, verify=False, headers=headers)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during deployment of Apigee API Proxy: %s/%s to environment %s" % (api_proxy, api_proxy_revision, self.target_environment))
        return resp

    def undeploy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_url(api_proxy, revision)
        url = url + "/deployments"
        print(url)
        authorization_headers = self.build_authorization_header()
        headers = authorization_headers
        if self.mfa:
            print("Multi factor authentication is on")
            resp = requests.delete(url, verify=False, headers=headers)
        else:
            print("Multi factor authentication is off")
            resp = requests.delete(url, verify=False, auth=self.authentication)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during undeployment of Apigee API Proxy: %s/%s from environment %s" % (api_proxy, api_proxy_revision, self.target_environment))
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
        authorization_headers = {}
        if self.mfa:
            my_token = self.create_one_time_password()
            headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Accept': 'application/json;charset=utf-8', 'Authorization': 'Basic ' + authorizationHeader}
            params = {'username': self.organization.username, 'password': self.organization.password, 'grant_type': 'password', 'mfa_token': my_token}
            resp = requests.post(self.sso_login_url, params=params, verify=False, headers=headers)
            if resp.status_code > 399:
                print(resp.status_code)
                print(resp.json())
                raise Exception("Error during creating authorization header")
            data = resp.json()
            access_token = data['access_token']
            authorization_headers = {'Authorization': 'Bearer ' + access_token}
        return authorization_headers

    def build_url(self, api_proxy, api_proxy_revision):
        base_url = self.organization.url
        url = base_url + "/v1/o/" + self.organization.name
        url = url + "/environments/" + self.target_environment
        url = url + "/apis/" + api_proxy
        url = url + "/revisions/" + api_proxy_revision
        return url

    def parse_revision(self, api_proxy_revision):
        if api_proxy_revision.startswith('rev'):
            return api_proxy_revision[3:]
        return api_proxy_revision
