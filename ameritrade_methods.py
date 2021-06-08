import json
import os
import requests
# ameritrade api creds.
import api.models as models
from datetime import datetime, timedelta


from api.emailer import send_new_auth  ## you will need to implement your own email sending method.

def send_full_auth_email():
    #this wil lsend to user to auth via ameritrade credentials

    current_env = os.environ.get('ENVIRONMENT')

    if current_env == 'DEV':
        #send_new_auth('')
        #pass
       
       ## This link is what the account owner will use to re-login to their account and generate a new code. 
       ## That new code once generated is passed to the your redirect_uri  specified in the link. 
        send_new_auth('https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2FyourdomainherefromTDAPIdashboard&client_id=clientidhere%40AMER.OAUTHAP')

    elif current_env == 'PROD':
        pass



def refresh_token(refresh_code):

    # make request with refresh code

    current_env = os.environ.get('ENVIRONMENT')
    ## store your 'Token' from TD Ameritrade either in an ENV, or in your database models
    token_obj = models.AmeritradeAuth.objects.get(environment=current_env)
    refresh_token = token_obj.refresh_token
    redirect_uri = token_obj.redirect_uri
    

    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = { 'grant_type': 'refresh_token', 'refresh_token': refresh_token, 'client_id': 'client_id', 'redirect_uri': redirect_uri }
    auth_reply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)

    print(" refresh_token status code = " + str(auth_reply.status_code ) + str(auth_reply.text))
 
 
    if auth_reply.status_code == 401 or auth_reply.status_code == 400:
        # If you receive a 400 or 401,  the refresh token did NOT work.  You need to re-authenticate by actually 
        # visiting the tdameritrade link and logging back into your account.

        print("sending auth email")
        send_full_auth_email()


    else:
        print("different auth_reply other than 401 ") 

        json_data = json.loads(auth_reply.text)
        new_token = json_data['access_token']

        current_env = os.environ.get('ENVIRONMENT')
        token_obj = models.AmeritradeAuth.objects.get(environment=current_env)
        token_obj.access_token = new_token
        token_obj.save()
        print("refreshed token method completed")
        return True 




def get_recent_orders():

    # get token from DB.
    current_env = os.environ.get('ENVIRONMENT')
    account_number = os.environ.get('AMERITRADE')

    token_obj = models.AmeritradeAuth.objects.get(environment=current_env)
    headers = { 'Authorization': 'Bearer ' + str(token_obj.access_token) }

    
    url = 'https://api.tdameritrade.com/v1/accounts/' + str(account_number) + '/transactions/'
    url = 'https://api.tdameritrade.com/v1/accounts/' + str(account_number) + '/orders/'
   
    today = (datetime.today()- timedelta(days=2)).strftime('%Y-%m-%d')

    print("today " + today) 
    params = {}
    account_reply = requests.get(url, headers=headers, params=params)

    if account_reply.status_code != 201 and account_reply.status_code != 200:

        print('status code returned ' + str(account_reply.status_code ))
        print("issue with account, refreshing token " + str(account_reply.text))
        refresh_status = refresh_token(token_obj.refresh_token)
        if refresh_status:
            print("refreshed: ")
            token_obj = models.AmeritradeAuth.objects.get(environment=current_env)
            headers = { 'Authorization': 'Bearer ' + str(token_obj.access_token) }
            account_reply = requests.get(url, headers=headers, params=params)
            json_data = json.loads(account_reply.text)
            
    else:
        #was 201 so parse it.
        print("200 response so parse. ")
        json_data = json.loads(account_reply.text)
        
    with open ('account-dump2.txt', 'w') as f:
        f.write(account_reply.text)

    print("returing json data " + str(json_data))
    return json_data


    # parse orders now and see if they are already in database
    # if not, then we need to trigger an ew trade, create new legs.



