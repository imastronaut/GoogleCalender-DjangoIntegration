from django.shortcuts import render,redirect
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect
from django.urls import reverse

#Importing google client library for OAuth2.0 authentication and authorization
import google.oauth2.credentials
import google_auth_oauthlib.flow
#import google module to create an Api Service Object that request access from google APi service provider
import googleapiclient.discovery
import os


#Oauth2 works through SSL layer. If your server is not parametrized to allow HTTPS,
# the fetch_token method will raise an oauthlib.oauth2.rfc6749.errors.InsecureTransportError . 
#We Can disbale it for our local testing by
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


CLIENT_SECRET_FILE = 'client_secret.json'
# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.


REDIRECT_URL = 'http://127.0.0.1:8000/rest/v1/calendar/redirect/'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

#Define the scopes that our application wants to get access to user data
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile','openid'
]


# Create your views here.
@api_view(['GET'])
def GoogleCalendarInitView(request):
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES)
    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = REDIRECT_URL
    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    
    request.session['state'] = state

    return HttpResponseRedirect(authorization_url)

    
@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URL

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    
    user_info = get_user_info(credentials)
    email_address=''
    if user_info:
        email_address = user_info.get('email')
    request.session['credentials'] = credentials_to_dict(credentials)

    if not request.session['credentials']:
        return HttpResponseRedirect(reverse('google_permission'))

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])



    #Build a calender service object that encodes the necessary request information and scopes needed by the application
    #describing 3 parameters - 1.Api service name 2.APi Version 3.Credentails
    

    calendar = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)


    #Get the list of calendars in users account
    calendar_list = calendar.calendarList().list().execute()
    #code to get calender events that belog to user's primary account
    events = calendar.events().list(calendarId='primary').execute()
    events_list = []
    if not events['items']:
        return Response("No events found in this user's calender")
    for event in events['items']:
        events_list.append(event)
        return Response(events_list)
    return Response({"No events found for this user"})



def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def get_user_info(credentials):
  """Send a request to the UserInfo API to retrieve the user's information.

  Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
  Returns:
    User information as a dict.
  """
  user_info_service = googleapiclient.discovery.build(
      serviceName='oauth2', version='v2',
      credentials=credentials)
  user_info = user_info_service.userinfo().get().execute()
  return user_info