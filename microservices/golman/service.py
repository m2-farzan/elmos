from core import login, update, Edu

from datetime import datetime, timedelta
import json
from os import environ
from time import sleep
import requests
from sys import exit


def main(config):
    print('Service started.')
    print('Started login attempt...')
    captcha_functor = lambda image: get_captcha(image, config['captcha_timeout'], config['captcha_base'])
    state = login(config['edu'], config['edu_user'], config['edu_pass'], captcha_functor) # Blocks until captcha is fed.
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


def get_captcha(captcha, timeout, captcha_base):
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
    }
    main(config)
