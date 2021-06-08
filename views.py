



### This view is for receiving a GET request from Td Ameritrade after a successful re-authentication.


@csrf_exempt
def receive_token(request):


    code = request.GET['code']

    #Post Access Token Request
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = { 'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code, 'client_id': 'client_id', 'redirect_uri': 'https://admin.yourredirectdomain.com' }
    auth_reply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
    
    if auth_reply.status_code == 201 or auth_reply.status_code == 200:


## Multi environment support.
        current_env = os.environ.get('ENVIRONMENT')

        if current_env == 'PROD':
            redirect_uri = 'https://admin.yourredirectdomain.com'
        else:
            redirect_uri = 'https://admin.yourredirectdomain.com'

            #redirect_uri = 'http://localhost:8000/navigation'

        json_data = json.loads(auth_reply.text)

        print(str(json_data) ) 
        print(type(json_data))
        print(str(json_data.keys()))

        eval = ast.literal_eval(auth_reply.text)
       
        print(str(eval['access_token'] ))
        
        token_obj = models.AmeritradeAuth.objects.get_or_create(
                environment=current_env,
                redirect_uri=redirect_uri
        )
        print(str(json_data))
        token_obj = models.AmeritradeAuth.objects.get(environment=current_env, redirect_uri=redirect_uri)

        token_obj.access_token = json_data['access_token']
        #token_obj.access_token = "test"
        token_obj.refresh_token = json_data['refresh_token']
      
        token_obj.save()
        return  JsonResponse(data={'status': 'udpated token successfully'})

    else:
        print("error code other than 201, notify admin" + str(auth_reply) )
        print(auth_reply.text)

        return  JsonResponse(status=404, data={'status': 'Error updating token from link, contact admin'})