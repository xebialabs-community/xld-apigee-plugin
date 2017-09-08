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


def setup_urllib():
    requests.packages.urllib3.disable_warnings(SNIMissingWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ApigeeClient(object):
    def __init__(self, organization, target_environment):
        self.organization = organization
        self.target_environment = target_environment
        self.authentication = (organization.username, organization.password)

    def deploy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_url(api_proxy, revision)
        url = url + "/deployments"
        params = {'override': 'true'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        print(url)
        resp = requests.post(url,
                auth=self.authentication,
                params=params,
                verify=False,
                headers=headers)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during deployment of Apigee API Proxy: %s/%s to environment %s" %
                (api_proxy, api_proxy_revision, self.target_environment))
        return resp

    def undeploy(self, api_proxy, api_proxy_revision):
        revision = self.parse_revision(api_proxy_revision)
        url = self.build_url(api_proxy, revision)
        url = url + "/deployments"
        print(url)
        resp = requests.delete(url, verify=False, auth=self.authentication)
        if resp.status_code > 399:
            print(resp.status_code)
            print(resp.json())
            raise Exception("Error during undeployment of Apigee API Proxy: %s/%s from environment %s" %
                (api_proxy, api_proxy_revision, self.target_environment))
        return resp

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
