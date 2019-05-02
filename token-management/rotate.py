# Example Python script for automated API token rotation in combination 
# with a HashiCorp vault server

import requests

# CONFIGURATION
# configure list of all secrets we want to rotate
SECRETS = [ 'dynatrace/automation_script1', 'dynatrace/automation_script2' ] 
# HashiCorp vault information
VAULT = 'http://YOUR_VAULT_SERVER_ADDRESS:8200/v1/secret/data/'
X_VAULT_TOKEN = 'YOUR_VAULT_ACCESS_KEY'
# Dynatrace master token must have 'token management' permission assigned 
DT_MASTER_TOKEN = 'dynatrace/master'
# Your Dynatrace environment URL
DT_URL = 'https://YOURENVIRONMENT.live.dynatrace.com'
# END CONFIGURATION

def vault_receive_secret(secret_path, vault, token):
    resp = requests.get(url=vault + '' + secret_path, headers={'x-vault-token' : X_VAULT_TOKEN})
    if resp.status_code == 200:
        return True, resp.json()['data']['data']['token'] 
    return False, {}

def dt_receive_token_info(token, dt_url, dt_api_token):
    resp = requests.post(url=dt_url + '/api/v1/tokens/lookup/', json={'token' : token}, headers={'Authorization' : 'Api-Token ' + dt_api_token})
    if resp.status_code == 200:
        return True, resp.json() 
    return False, {}

# fetch master token '/dynatrace/master' from vault
m_ret = requests.get(url=VAULT + '' + DT_MASTER_TOKEN, headers={'x-vault-token' : X_VAULT_TOKEN})
if m_ret.status_code != 200:
    print('There was no master token found within your vault under path /dynatrace/master')
    exit()
else:
    DT_MASTER_TOKEN = m_ret.json()['data']['data']['token']

for secret in SECRETS:
    print('>Rotate: ' + secret)
    # fetch old secret from vault
    success, old_sec = vault_receive_secret(secret, VAULT, X_VAULT_TOKEN)
    if success:
        # receive secret metainfos from Dynatrace
        success, t_info = dt_receive_token_info(old_sec, DT_URL, DT_MASTER_TOKEN)
        if success:
            # create new secret with same scope as old
            resp = requests.post(url=DT_URL + '/api/v1/tokens', json=t_info, headers={'Authorization' : 'Api-Token ' + DT_MASTER_TOKEN})
            if resp.status_code == 201:
                new_token = resp.json()['token'] 
                # store new token in secret vault
                c_ret = requests.post(url=VAULT + secret, json={ 'data' : { 'token': new_token}}, headers={'x-vault-token' : X_VAULT_TOKEN})
                if c_ret.status_code == 200:
                    # if creation was successful delete old Dynatrace token through Dynatrace API
                    d_resp = requests.delete(url=DT_URL + '/api/v1/tokens/' + t_info['id'], headers={'Authorization' : 'Api-Token ' + DT_MASTER_TOKEN})
                    if d_resp.status_code == 204:
                        print('  Old Dynatrace token successfully deleted')
                        print('  Token rotation successful')
                    else:
                        print('  Failed to delete old Dynatrace token')
            else:
                print('Failed to rotate secret: ' + secret)
        else:
            print('  Api token not found in Dynatrace')
    else:
        print('  Secret not found in vault')
    
