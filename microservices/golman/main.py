import constants as c
from datetime import datetime, timedelta
import json
from os import environ
import requests
from time import sleep
from sys import exit
import utils

class State:
    def __init__(self, state_keys, cookies):
        self.state_keys = state_keys # Not even used
        self.cookies = cookies

class Edu:
    def __init__(self, domain, protocol):
        self.domain = domain
        self.protocol = protocol
    
    def base(self):
        return '%s://%s' % (self.protocol, self.domain)


def main(config):
    print('Service started.')
    print('Started login attempt...')
    state = login(config['edu'], config['edu_user'], config['edu_pass'], config['captcha_timeout'], config['captcha_mode'], config['captcha_base']) # Blocks until captcha is fed.
    print('Finished login attempt successfully.')

    print('Started update loop.')

    while True:
        print('Started pulling data from ' + config['edu'].base() + ' at ' + str(datetime.now()))

        state, data_avail, data_na = update(config['edu'], state, config['edu_term'])
        with open('data_avail.xml', 'w') as f:
            f.write(data_avail)
        with open('data_na.xml', 'w') as f:
            f.write(data_na)

        print('Finished pulling data from upstream.')
        print('    Data [avail] Length = {:,}'.format(len(data_avail)))
        print('    Data [na] Length = {:,}'.format(len(data_na)))


        print('Started posting data to dbwriter...')
        upload_result = requests.post(config['dbwriter_endpoint'], files={'data_avail': data_avail, 'data_na': data_na})
        print('Finished posting data to dbwriter with status code = ' + str(upload_result.status_code))


        print('Entering sleep for ' + str(config['refresh_sleep']) + ' seconds.')
        print('See you at ' + str(datetime.now() + timedelta(seconds=config['refresh_sleep'])))
        print(32 * '-')
        sleep(config['refresh_sleep'])
        

def update(edu, state, term):
    state, data_avail = pull(edu, state, term, 'avail')
    state, data_na = pull(edu, state, term, 'na')
    return state, data_avail, data_na


def get_captcha(captcha, timeout, mode, captcha_base):    
    if mode == 'local':
        with open('captcha.gif', 'wb') as f:
            f.write(captcha)
        return input('Enter CAPTCHA: ')

    print('    Started captcha decoding in auto mode.')
    requests.post(captcha_base + '/img', files={'file': captcha})
    sleep(5)

    print('    Waiting for remote captcha.')

    SLEEP_CAP = 3
    TIME_LEFT = timeout

    while True:
        code = json.loads( requests.get(captcha_base + '/code').content )['code']
        if not (code == 'waiting' or code == 'stale'):
            break
        TIME_LEFT -= SLEEP_CAP
        sleep(SLEEP_CAP)
        if TIME_LEFT < 0:
            requests.post(captcha_base + '/code/stale')
            print('Captcha timed out')
            exit(1)

    print('    Remote captcha was found: ' + code)
    
    return code


def login(edu, user, password, captcha_timeout, captcha_mode, captcha_base):
    # Request the session cookie (ASP.NET_SessionId)
    session_id_req = requests.get(edu.base() + c.edu_endpoints['session_id'])
    cookies = session_id_req.cookies

    # Apply the u,it='' from https://edu.iust.ac.ir/Forms/AuthenticateUser/Golestan.htm
    # Also apply other stuff that idk what they are:
    extra_cookies = {'u': '', 'lt': ''} | {'su': '', 'ft': '', 'f': '', 'seq': ''}
    for name, value in extra_cookies.items():
        cookies.set(name, value, domain=edu.domain, path='/')

    # Get the form
    form = requests.get(
        edu.base() + c.edu_endpoints['auth_user'],
        params=c.edu_default_params['auth_user'],
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    _ = requests.get(edu.base() + c.edu_endpoints['captcha'], cookies=cookies)

    # Dummy post (Edu does this too. This seems to solve the bug in edu login)
    form = requests.post(
        edu.base() + c.edu_endpoints['auth_user'],
        c.edu_form_data_dummy['auth_user'] | state_keys,
        params=c.edu_default_params['auth_user'],
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    captcha = requests.get(edu.base() + c.edu_endpoints['captcha'], cookies=cookies)

    # Wait for captcha (Blocks and may bail with exception)
    captcha_text = get_captcha(captcha.content, captcha_timeout, captcha_mode, captcha_base)

    # Actual post
    form = requests.post(
        edu.base() + c.edu_endpoints['auth_user'],
        c.edu_form_data['auth_user'](user, password, captcha_text) | state_keys,
        params=c.edu_default_params['auth_user'],
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    for cookie in form.cookies:
        cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
    
    # Save Auth Data from JS
    auth_data = utils.parse_auth_data(form.content)
    for name, value in auth_data.items():
        cookies.set(name, value, domain=edu.domain, path='/')

    return State(state_keys, cookies)


def pull(edu, state, term, course_status_filter):
    ticket = state.cookies.get_dict().get('ctk') or state.cookies.get_dict().get('lt')
    cookies = state.cookies

    # Get
    form = requests.get(
        edu.base() + c.edu_endpoints['102'],
        params=c.edu_default_params['102'] | {'tck': ticket},
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    ticket_textbox = utils.parse_ticket_textbox(form.content) # may be different from ticket
    for cookie in form.cookies:
        cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
    auth_data = utils.parse_auth_data(form.content)
    for name, value in auth_data.items():
        cookies.set(name, value, domain=edu.domain, path='/')
    
    # Dummy Post
    form = requests.post(
        edu.base() + c.edu_endpoints['102'],
        c.edu_form_data_dummy['102'](ticket_textbox) | state_keys,
        params=c.edu_default_params['102'] | {'tck': ticket},
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    ticket_textbox = utils.parse_ticket_textbox(form.content) # may be different from ticket
    for cookie in form.cookies:
        cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
    auth_data = utils.parse_auth_data(form.content)
    for name, value in auth_data.items():
        cookies.set(name, value, domain=edu.domain, path='/')
    
    # Actual Post
    csfv = '0' if course_status_filter == 'na' else '1' # course status filter value
    form = requests.post(
        edu.base() + c.edu_endpoints['102'],
        c.edu_form_data['102'](ticket_textbox, term, csfv) | state_keys,
        params=c.edu_default_params['102'] | {'tck': ticket},
        headers=c.edu_default_headers,
        cookies=cookies
    )
    state_keys = utils.parse_state_keys(form.content)
    ticket_textbox = utils.parse_ticket_textbox(form.content) # may be different from ticket
    for cookie in form.cookies:
        cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
    auth_data = utils.parse_auth_data(form.content)
    for name, value in auth_data.items():
        cookies.set(name, value, domain=edu.domain, path='/')

    # Extract data string
    xml_data = utils.get_xml_data(form.content)
    xml_data = utils.xml_postprocess(xml_data)
    
    state.cookies = cookies
    state.state_keys = state_keys
    return state, xml_data


if __name__ == "__main__":
    config = {
        'dbwriter_endpoint': 'http://dbwriter2/',
        'edu': Edu(environ['EDU_DOMAIN'], 'https'),
        'edu_user': environ['EDU_USER'],
        'edu_pass': environ['EDU_PASS'],
        'edu_term': environ['EDU_TERM'],
        'refresh_sleep': int(environ['GOLMAN_SLEEP']),
        'captcha_base': 'http://elmos/captcha',
        'captcha_timeout': 270,
        'captcha_mode': 'auto', # 'local': get captch from terminal. 'auto': submit captcha to web application and wait for users to help us.
    }
    main(config)
