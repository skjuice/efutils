import logging
import requests
import json
from pprint import pprint

api_url = None
logger = logging.getLogger(__name__)

def configure(**kwargs):
    global api_token

    api_token = kwargs.get('api_token')

def get(url, **kwargs):
    if '?' in url:
        url = url + '&api_token=' + api_token
    else:
        url = url + '?api_token=' + api_token

    if 'parse_json' in kwargs:
        parse_json = kwargs.get('parse_json')
    else:
        parse_json = True

    headers = {'Authorization': 'Bearer ' + api_token, "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        #response_data = json.loads(response.text)
        log_response(response)

        if 'return_http_status' in kwargs:
            return response.status_code

        if parse_json is True:
            return json.loads(response.text)
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return 0

def get2(url, headers, **kwargs):
    if 'parse_json' in kwargs:
        parse_json = kwargs.get('parse_json')
    else:
        parse_json = True

    try:
        response = requests.get(url, headers=headers)

        if 'return_http_status' in kwargs:
            return response.status_code

        if parse_json is True:
            return json.loads(response.text)
        else:
            return response.text
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return 0

def get3(url, headers, **kwargs):
    if 'parse_json' in kwargs:
        parse_json = kwargs.get('parse_json')
    else:
        parse_json = True

    try:
        response = requests.get(url, headers=headers)

        if parse_json is True and response.status_code == 200:
            data = json.loads(response.text)
        else:
            data = response.text

        return response.status_code, data
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return 0

def call(data):
    """SEND DATA TO API ENDPOINT
        data signature:
        an array of elements where first element is for general-data and all other elements are for files (each one for ONE file)

    """
    if '?' in api_url:
        url = api_url + '&api_token=' + api_token
    else:
        url = api_url + '?api_token=' + api_token

    headers = {'Authorization': 'Bearer ' + api_token, "Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        #response_data = json.loads(response.text)
        log_response(response)
        return response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return 0

def call2(data, **kwargs):
    """SEND POST (or other HTTP VERB) TO API ENDPOINT
        data signature:
        an array of elements where first element is for general-data and all other elements are for files (each one for ONE file)
        parses returned json into dictionary and returns that

        If a POST call is to be made to an endpoint with no data, the first parameter can be empty string ''

    """
    if 'method' in kwargs:
        method = kwargs.get('method')
    else:
        method = 'post'

    if '?' in api_url:
        url = api_url + '&api_token=' + api_token
    else:
        url = api_url + '?api_token=' + api_token

    headers = {'Authorization': 'Bearer ' + api_token, "Content-Type": "application/json"}
    try:
        if method == 'post':
            response = requests.post(url, data=json.dumps(data), headers=headers)
        elif method == 'put':
            response = requests.put(url, data=json.dumps(data), headers=headers)

        if 'return_http_status' in kwargs:
            return response.status_code

        output = {}
        try:
            output['response'] = json.loads(response.text)
        except ValueError:
            output['response'] = response.text

        output['http_status_code'] = response.status_code
        log_response(response)
        return output
    except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
        logger.error('Connection to server timed out')
        return False
    except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
        logger.error('Server sent too many redirects')
        return False
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error(e)
        return False


def post(url, data, headers, **kwargs):
    kwargs['method'] = 'post'
    return call3(url, data, headers, **kwargs)

def call3(url, data, headers, **kwargs):
    """SEND POST (or other HTTP VERB) TO API ENDPOINT
        data signature:
        an array of elements where first element is for general-data and all other elements are for files (each one for ONE file)
        parses returned json into dictionary and returns that

        If a POST call is to be made to an endpoint with no data, the first parameter can be empty string ''

    """
    if 'method' in kwargs:
        method = kwargs.get('method')
    else:
        method = 'post'

    #headers = {'Authorization': 'Bearer ' + api_token, "Content-Type": "application/json"} #now comming in as function argument
    try:
        if method == 'post':
            response = requests.post(url, data=json.dumps(data), headers=headers)
        elif method == 'put':
            response = requests.put(url, data=json.dumps(data), headers=headers)

        if 'return_http_status' in kwargs:
            return response.status_code

        output = {}
        try:
            output['response'] = json.loads(response.text)
        except ValueError:
            output['response'] = response.text

        output['http_status_code'] = response.status_code
        #log_response(response)
        return output
    except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
        logger.error('Connection to server timed out')
        return False
    except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
        logger.error('Server sent too many redirects')
        return False
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error(e)
        return False


def call4(url, data, headers, **kwargs):
    """SEND POST (or other HTTP VERB) TO API ENDPOINT
        data signature:
        an array of elements where first element is for general-data and all other elements are for files (each one for ONE file)
        parses returned json into dictionary if possible

        If a POST call is to be made to an endpoint with no data, the second parameter can be empty string ''

    """
    if 'method' in kwargs:
        method = kwargs.get('method')
    else:
        method = 'post'

    #headers = {'Authorization': 'Bearer ' + api_token, 'Content-Type': 'application/json', 'Accept': 'application/json'} #now comming in as function argument
    try:
        if method == 'post':
            #response = requests.post(url, data=json.dumps(data), headers=headers)
            #below because some value in data might not be string/int. Example error: TypeError: Object of type datetime is not JSON serializable
            response = requests.post(url, data=json.dumps(data, indent=4, sort_keys=True, default=str), headers=headers)

        elif method == 'put':
            response = requests.put(url, data=json.dumps(data, indent=4, sort_keys=True, default=str), headers=headers)

        data = {}
        data['response_raw_bytes'] = response.content
        try:
            data['response_dict'] = response.json()   # trying to load json string into dictionary
        except ValueError:
            data['response_dict'] = None
            data['response_text_string'] = response.text

        data['status_code'] = response.status_code

        return data
    except requests.exceptions.Timeout:

        logger.error('Connection to server timed out')
        return False
    except requests.exceptions.TooManyRedirects:

        logger.error('Server sent too many redirects')
        return False
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error(e)
        return False


def log_response(response):
    #pprint(response)   # prints <Response [200]>
    code = response.status_code
    if code == 401:
        logger.error('Authorization Error, Response HTTP Code: ' + str(code))
    elif code == 200:
        logger.info('Everything Ok, Response HTTP Code: ' + str(code))
    else:
        logger.error('Response HTTP Code: ' + str(code))
        #logger.info('Server response content type : ' + response.headers['Content-Type'])



    """
    Server could return json text in body no matter what the status code

    In case the JSON decoding fails, r.json() raises an exception. For example, if the response gets a 204 (No Content),
    or if the response contains invalid JSON, attempting r.json() raises ValueError: No JSON object could be decoded.
    It should be noted that the success of the call to r.json() does not indicate the success of the response. Some servers
    may return a JSON object in a failed response (e.g. error details with HTTP 500). Such JSON will be decoded and returned.
    To check that a request is successful, use r.raise_for_status() or check r.status_code is what you expect.
    """
    try:
        responses = response.json()
        # this must be true: response.headers['Content-Type'] == 'application/json'
        if responses:
            if code == 200:
                pass
                #logger.info(json.dumps(responses)) #this logs same as response.text
            else:
                pass
                #logger.error(json.dumps(responses))
    except ValueError:
        # no JSON returned
        """ Requests library will automatically decode content from the server. Most unicode charsets are seamlessly decoded.
            When you make a request, Requests library makes educated guesses about the encoding of the response based on the
            HTTP headers. The text encoding guessed by Requests is used when you access r.text. """
        if response.text:
            pass

