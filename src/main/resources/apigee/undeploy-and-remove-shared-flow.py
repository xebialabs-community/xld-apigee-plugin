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

setup_urllib()

client = ApigeeClient(previousDeployed.container.org, previousDeployed.container)
response = client.undeploy_shared_flow(previousDeployed.deployable.name, previousDeployed.revisionNumber)
if response.text == "":
    print("The response is empty")
else:
    print(response.text)

if previousDeployed.deployable.deleteSharedFlowRevisionAfterUndeployment:
    print("Delete revision number " + previousDeployed.revisionNumber)
    response = client.delete_shared_flow_revision(previousDeployed.deployable.name, previousDeployed.revisionNumber)
    if response.text == "":
        print("The response is empty")
    else:
        print(response.text)
else:
    print("The property deleteSharedFlowRevisionAfterUndeployment is set to False")
    print("The revision number " + previousDeployed.revisionNumber + " of " + previousDeployed.deployable.name + " will not be deleted")

