from bs4 import BeautifulSoup
import re

# response: e.g. .content member of a response object from 'requests.get'
def parse_state_keys(content):

    bs = BeautifulSoup(content, 'html.parser')

    return {
        '__VIEWSTATE': bs.select('#__VIEWSTATE')[0]['value'],
        '__VIEWSTATEGENERATOR': bs.select('#__VIEWSTATEGENERATOR')[0]['value'],
        '__EVENTVALIDATION': bs.select('#__EVENTVALIDATION')[0]['value'],
    }

def parse_ticket_textbox(content):
    bs = BeautifulSoup(content, 'html.parser')
    return bs.select('#TicketTextBox')[0].get('value') # CHECK THIS

def parse_auth_data(content):
    html = content.decode('utf-8')
    a = html.find('parent.Commander.SavAut(')
    if a < 0:
        raise Exception("Can't find SavAut in content:\n\n" + html)
    b = html.find('\n', a)
    line = html[a:b]
    csa = line[line.find('(')+1 : line.find(')')]
    args = csa.split(',')
    return {
        'u': args[0],
        'su': args[1][1:-1], # get rid of quotes
        'ft': args[2][1:-1], # get rid of quotes
        'f': args[3], # aka `fid`
        'lt': args[4][1:-1],
        'ctk': args[5][1:-1],
        'seq': args[6]
    }

def get_xml_data(content):
    html = content.decode('utf-8')
    xml_data_match = re.findall(r"xmlDat=\'(.+)\';", html)
    if len(xml_data_match) != 1:
        raise Exception("Can't find XML data in the post response.")    
    return xml_data_match[0]

def xml_postprocess(raw):
    x = re.sub(r'<row', r'\n<row', raw)
    return x