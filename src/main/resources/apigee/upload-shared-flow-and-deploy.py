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

revision_name = None
client = ApigeeClient(deployed.container.org, deployed.container)
response = client.import_shared_flow(deployed.deployable.name, deployed.file.path)
try:
    print response.json()
    revision_name = response.json()['revision']
    print("Shared flow imported as revision number: " + revision_name)
    unwrapped_deployed = unwrap(deployed)
    unwrapped_deployed.setProperty("revisionNumber", revision_name)
except ValueError:
    print("No JSON returned after importing the shared flow %s" % deployed.deployable.name)
    print(response.text)

if revision_name is not None:
    response = client.deploy_shared_flow(deployed.deployable.name, revision_name)
    print(response.text)
else:
    print("The shared flow %s is not imported. Therefore we will not deploy it" % (deployed.deployable.name))
