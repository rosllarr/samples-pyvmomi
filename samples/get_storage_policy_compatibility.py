#!/usr/bin/env python
"""
Written by Vadim Aleksandrov
Github: https://github.com/verdel
Email: valeksandrov@me.com

This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0

Example of using Storage Policy
Based Management (SPBM) API to get VM Home
and Virtual Disk Storage Policies

Thanks to William Lam (https://github.com/lamw) for ideas from
the script list_vm_storage_policy.py
"""

from pyVmomi import pbm, VmomiSupport, SoapStubAdapter
from tools import cli, service_instance
from pprint import pprint

def pbm_connect(stub_adapter, disable_ssl_verification=False):
    """Connect to the VMware Storage Policy Server

    :param stub_adapter: The ServiceInstance stub adapter
    :type stub_adapter: SoapStubAdapter
    :param disable_ssl_verification: A flag used to skip ssl certificate
        verification (default is False)
    :type disable_ssl_verification: bool
    :returns: A VMware Storage Policy Service content object
    :rtype: ServiceContent
    """

    if disable_ssl_verification:
        import ssl
        if hasattr(ssl, '_create_unverified_context'):
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None
    else:
        ssl_context = None

    VmomiSupport.GetRequestContext()["vcSessionCookie"] = \
        stub_adapter.cookie.split('"')[1]
    hostname = stub_adapter.host.split(":")[0]
    pbm_stub = SoapStubAdapter(
        host=hostname,
        version="pbm.version.version1",
        path="/pbm/sdk",
        poolSize=0,
        sslContext=ssl_context)
    pbm_si = pbm.ServiceInstance("ServiceInstance", pbm_stub)
    pbm_content = pbm_si.RetrieveContent()
    return pbm_content

def get_profile(profile_name, pbm_content):
    pm = pbm_content.profileManager
    profile_ids = pm.PbmQueryProfile(
        resourceType=pbm.profile.ResourceType(resourceType="STORAGE"),
        profileCategory="REQUIREMENT")
    if len(profile_ids) > 0:
        profiles = pm.PbmRetrieveContent(profileIds=profile_ids)
        for profile in profiles:
            if profile_name in profile.name:
                return profile
    raise Exception('Profile not found')

   

def get_datastore_compatibility(compatibility_result):
    datastores = []
    for result in compatibility_result:
        if result.error == [] and result.hub.hubType == 'Datastore':
            ds_id = result.hub.hubId
            datastores.append(ds_id)

    return datastores

def main():
    """Main program.
    """

    parser = cli.Parser()
    parser.add_required_arguments(cli.Argument.STORAGE_POLICY_NAME)
    args = parser.get_args()
    si = service_instance.connect(args)

    pbm_content = pbm_connect(si._stub, args.disable_ssl_verification)

    # Get storage policy profile by name
    profile = get_profile(args.storage_policy_name, pbm_content)

    # Check compatibility
    compatibility_result = pbm_content.placementSolver.PbmCheckCompatibility(profile=profile.profileId)
 
    # Get datastore compatibilities
    datastores = get_datastore_compatibility(compatibility_result)
    pprint(datastores)

if __name__ == "__main__":
    main()
