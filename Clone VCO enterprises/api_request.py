#!/usr/bin/env/python
#
# api_request.py
#
# Python script, provided 'as-is', as an example of how to perform upgrades via API
#
# Dependencies:
# This library depends upon client.py, which depends on requests that can be installed via pip
#
# Usage:
#
#  (1) Change the parameters within the parameters section ONLY.
#  (2) Run the script from cli with 'python api_request.py'

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from client import VcoRequestManager
import os
import sys
import json

######## PARAMETERS ###########
# username expects env variable. Can be changed to a string
# password expects env variable. Can be changed to a string
# enterpriseIdToBeCloned expects an int which represents the id of the enterprise to be cloned
# enable2FA expects True or False, based on if you want to enable 2FA for this new customer
# Example:
# hostname = "vco1-region.velocloud.net"
# username = 'your@username.com'
# password = 'yourPa$$w0rd'
# client = VcoRequestManager(hostname)
# enterpriseIdToBeCloned = 39
# enable2FA = False 

hostname = "vco.hostname.net"
username = os.environ["VC_USERNAME"] 
password = os.environ["VC_PASSWORD"]
client = VcoRequestManager(hostname)
enterpriseIdToBeCloned = 0
enableTwoFactorAuthentication = False

# new enterprise details
# ** PLEASE MODIFY ONLY: **
# - username, email, password, password2 and mobilePhone
# - name
# do not modify any other parameter as it will break the usage
newEnterpriseDetails = {
    'user': {
        "username": "user1@email.com",
        "email": "user1@email.com",
        "password": "Pa$sw0rd!",
        "password2": "Pa$sw0rd!",
        "mobilePhone": "123412341234"
    },
    'configurationId': None,
    'enableEnterpriseDelegationToOperator': None,
    'enableEnterpriseDelegationToProxy': None,
    'enableEnterpriseUserManagementDelegationToOperator': None,
    'licenses': {
        'ids': []
    },
    'gatewayPoolId': None,
    'endpointPkiMode': None,
    'id': enterpriseIdToBeCloned,
    'name': 'Enterprise Name 2',
    'with': []
}

######## END OF PARAMETERS ###########

def authenticate():
    """
    Perform user authentication
    """
    client.authenticate(username, password, False)

def getCloneableEnterprises():
    """ 
    Get enterprises from MSP that can be cloned and search for the entepriseIdToBeCloned within this list
    """
    cloneableEnterprises = client.call_api("enterpriseProxy/getEnterpriseProxyCloneableEnterprises", {})
    for enterprise in cloneableEnterprises:
        if enterprise['id'] == enterpriseIdToBeCloned:
            newEnterpriseDetails['configurationId'] = enterprise['configurationId']
            newEnterpriseDetails['enableEnterpriseDelegationToOperator'] = enterprise['enableEnterpriseDelegationToOperator']
            newEnterpriseDetails['enableEnterpriseDelegationToProxy'] = enterprise['enableEnterpriseDelegationToProxy']
            newEnterpriseDetails['enableEnterpriseUserManagementDelegationToOperator'] = enterprise['enableEnterpriseUserManagementDelegationToOperator']
            newEnterpriseDetails['gatewayPoolId'] = enterprise['gatewayPoolId']
            newEnterpriseDetails['endpointPkiMode'] = enterprise['endpointPkiMode']
            print('Found cloneable enterprise \"%s\" with id %s, starting to clone' % (enterprise['name'], enterpriseIdToBeCloned))
            return newEnterpriseDetails
    return None

def prepareClone():
    """
    Check the enterprise to be cloned details and prepare the cloning
    """
    newEnterpriseDetails = getCloneableEnterprises()
    if newEnterpriseDetails is None:
        print('Did not find cloneable enterprise with id %s' % enterpriseIdToBeCloned)
        sys.exit()

    doClone(newEnterpriseDetails, enableTwoFactorAuthentication)

def doClone(payload, twoFactorAuth):
    """
    Execute the API call to clone the enterprise. Takes a dict of the enterprise details
    """
    # try to clone
    cloningResult = client.call_api('enterprise/cloneEnterpriseV2', payload)
    # if any errors, they're catched and thrown in the client.py. Proceed to print succeed
    print('New enterprise created with details: %s' % json.dumps(cloningResult, indent=2))
    # Check if 2FA is needed 
    if "id" in cloningResult and twoFactorAuth:
        enable2FA(cloningResult['id'])


def enable2FA(enterpriseId):
    twoFA = {
        'name': 'vco.enterprise.authentication.twoFactor.enable',
        'value': 'true',
        'dataType': 'BOOLEAN',
        'enterpriseId': enterpriseId
    }
    print("Enabling Two Factor Authentication for enterpriseId %s" % enterpriseId)
    twoFactorResult = client.call_api('enterprise/insertOrUpdateEnterpriseProperty', twoFA)
    if json.dumps(twoFactorResult) == '{"rows": 1}':
        print('Two factor authentication enabled for enterpriseId %s' % enterpriseId)
    else:
        print('Something went wrong when enabling 2FA for enterpriseId %s. VCO returned %s' % (enterpriseId, twoFactorResult))

def main():
    authenticate()
    prepareClone()    
        
 
if __name__== "__main__":
    main()