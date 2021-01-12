import constants as c
import utils

import requests


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


# Only call this after login
def update(edu, state, term):
    state, data_avail = pull(edu, state, term, 'avail')
    state, data_na = pull(edu, state, term, 'na')
    return state, data_avail, data_na


def login(edu, user, password, captcha_functor):
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
    captcha_text = captcha_functor(captcha.content)

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
