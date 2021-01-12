from core import login, update, Edu

from os import environ
import requests


def main(config):
    print('Process started.')
    print('Started login attempt...')
    captcha_functor = lambda image: get_captcha(image)
    state = login(config['edu'], config['edu_user'], config['edu_pass'], captcha_functor) # Blocks until captcha is fed.
    print('Finished login attempt successfully.')

    print('Started pulling data from ' + config['edu'].base())

    state, data_avail, data_na = update(config['edu'], state, config['edu_term'])
    with open('data_avail.xml', 'w') as f:
        f.write(data_avail)
    with open('data_na.xml', 'w') as f:
        f.write(data_na)

    print('Finished pulling data from upstream.')
    print('    Data [avail] Length = {:,}'.format(len(data_avail)))
    print('    Data [na] Length = {:,}'.format(len(data_na)))

    if config['dbwriter_endpoint']:
        print('Started posting data to dbwriter...')
        upload_result = requests.post(config['dbwriter_endpoint'], files={'data_avail': data_avail, 'data_na': data_na})
        print('Finished posting data to dbwriter with status code = ' + str(upload_result.status_code))


def get_captcha(captcha, filepath='captcha.gif'):
    with open('captcha.gif', 'wb') as f:
        f.write(captcha)
    return input('Enter CAPTCHA: ')

if __name__ == "__main__":
    config = {
        'dbwriter_endpoint': environ.get('DBWRITER_ENDPOINT'),
        'edu': Edu(environ['EDU_DOMAIN'], 'https'),
        'edu_user': environ['EDU_USER'],
        'edu_pass': environ['EDU_PASS'],
        'edu_term': environ['EDU_TERM'],
    }
    main(config)
