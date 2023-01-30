#Google calender Integration using django rest api - Using OAuth 2.0 for Web Server Application

To run this Project first install requirement

```sh
pip install - r requirments.txt
```

to use this project you need to enable specific api and services for project project or web application and get OAuth 2.0 Client IDs

one can find the resource on how to get started [here] (https://developers.google.com/identity/protocols/oauth2/web-server) 

Enalbe Api's for your project

Create Authorization Credentails 

Resource for Google Api Client Libraries

After that install language specific API client libraries python [here] (https://developers.google.com/identity/protocols/oauth2/web-server#python)

you should have installed all the requirements

Now makemigrations and migrate
```sh
python manage.py makemigrations
```
```sh
python manage.py migrations
```

Now start your project

```sh
python manage.py runserver
```

this project contains two end points

- Endpoints:
```
/rest/v1/calendar/init/ -> GoogleCalendarInitView()
```
This view should start step 1 of the OAuth. Which will prompt user for his/her credentials

```
/rest/v1/calendar/redirect/ -> GoogleCalendarRedirectView()
```
This view will do two things
1. Handle redirect request sent by google with code for token. You
need to implement mechanism to get access_token from given
code
2. Once got the access_token get list of events in users calendar
