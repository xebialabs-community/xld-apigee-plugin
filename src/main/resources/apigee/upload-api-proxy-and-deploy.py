#
# Copyright 2017 XebiaLabs, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from apigee import ApigeeClient, setup_urllib
import json

setup_urllib()

revision_name = None
client = ApigeeClient(deployed.container.org, deployed.container)
response = client.import_api_proxy(deployed.deployable.name, deployed.file.path)
try:
    print response.json()
    revision_name = response.json()['revision']
    print("API proxy is imported as revision number " + revision_name)
    unwrapped_deployed = unwrap(deployed)
    unwrapped_deployed.setProperty("revisionNumber", revision_name)
except ValueError:
    print("No JSON returned after importing the API Proxy %s" % (deployed.deployable.name))
    print(response.text)

if revision_name is not None:
    response = client.deploy_api_proxy(deployed.deployable.name, revision_name)
    jsonData = json.loads(response.text)
    print(jsonData)

    # Check if there are multiple revisions deployed
    response = client.get_revision_numbers_of_apiproxy_deployed_to_environment(deployed.deployable.name)
    jsonData = json.loads(response.text)
    print(jsonData)
    lengthOfNames = len(jsonData['revision'])
    if (lengthOfNames > 1):
        print("There are multiple revisions of this apiproxy %s deployed to environment %s " % (deployed.deployable.name, deployed.container.environmentName))
        print("We will undeploy all of these except our latest deployed revision %s " % (revision_name))
        i = 0
        while i < lengthOfNames:
            revisionNumber = jsonData['revision'][i]['name']
            if (revisionNumber != revision_name):
                print("Undeploying revision  number: " + revisionNumber)
                response = client.undeploy_api_proxy(deployed.deployable.name, revisionNumber)
            i += 1
        response = client.get_revision_numbers_of_apiproxy_deployed_to_environment(deployed.deployable.name)
        if response.text == "":
            print("The response is empty")
        else:
            jsonData = json.loads(response.text)
            print("Deployed revision: \n")
            print(jsonData)
    else:
        print("There are no multiple revisions of this apiproxy %s deployed to environment %s " % (deployed.deployable.name, deployed.container.environmentName))
else:
    print("The API Proxy %s is not imported. Therefore we will not deploy it" % (deployed.deployable.name))
