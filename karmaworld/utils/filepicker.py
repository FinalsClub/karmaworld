import hmac
import json
import base64

from hashlib import sha256
import os

FILEPICKER_SECRET = os.environ['FILEPICKER_SECRET']

def encode_fp_policy(policy):
    """ Return URL-safe Base64 encoded JSON Filepicker policy. """
    # Validate the JSON before trying to sign it and send it off to FP. It'll
    # be easier to trap exceptions in Python than read errors out of FP.

    # drop an exception bomb if the policy is not valid JSON.
    pypolicy = json.loads(policy)
    # ensure expiry is included. drop excepbomb if it isn't.
    pypolicy['expiry']

    # https://developers.inkfilepicker.com/docs/security/#signPolicy
    # encode and return
    return base64.urlsafe_b64encode(policy)

def sign_fp_policy(policy):
    """ Return a signature appropriate for the given encoded policy. """
    # https://developers.inkfilepicker.com/docs/security/#signPolicy
    # hash it up, bra!
    engine = hmac.new(FILEPICKER_SECRET, digestmod=sha256)
    engine.update(policy)
    return engine.hexdigest()
