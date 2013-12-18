Google Drive Authentication
===========================

Authorizing a new installation of Karmaworld with Google Drive is a convoluted 
process.
But it happens infrequently enough that we haven't simplified the process.
This should probably happen in the future, 
but in the meantime we can document the process.

* Start a django interactive shell
* Import the `karmaworld.apps.notes.gdrive` module.
* build a flow object called `flow`
* open a private browsing instance in a browser
* Log into the google drive account of the GOOGLE_USER set in `karmaworld.secrets.drive`
* get the authorization url

    flow.step1_get_authorize_url()

* go to that url in your browser
* it will redirecto you to a url in the format of:

   http://localhost:8000/oauth2callback?code=EXCHANGE_CODE

The url of the page you are re-directed to will contain the EXCHANGE_CODE required to complete the authentication

take the EXCHANGE_CODE from the url, and feed it as a string to 

    credentials = flow.step2_exchange('EXCHANGE_CODE')

This gives you a credentials object, keep this value

Create an instance of DriveAuth()

    from karmaworld.apps.notes.models import DriveAuth
    auth = DriveAuth()
    
and feed the credentials object to it with store()

    auth.store(credentials)
    
This will save the DriveAuth()

You are now authenticated!


