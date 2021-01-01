edu_default_headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://edu.iust.ac.ir',
    'Referer': 'https://edu.iust.ac.ir',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko)  Chrome/24.0.1312.57 Safari/537.17',
}


edu_default_params = {
    'auth_user': {
        'fid': '0;1',
        'tck': '',
        'lastm': '20200916065922',
    },
    '102': {
        'fid': '1;102',
        'b': '0',
        'l': '0',
        'tck': '', # must be set dynamically
        'lastm': '20190829142532',
    },
}

edu_endpoints = {
    'session_id': '/_templates/unvarm/unvarm.aspx?typ=1', # Yes, it's the first req that gen's sessionID cookie. I mean... wtf!
    'auth_user': '/Forms/AuthenticateUser/AuthUser.aspx',
    'captcha': '/Forms/AuthenticateUser/captcha.aspx',
    '102': '/Forms/F0202_PROCESS_REP_FILTER/F0202_01_PROCESS_REP_FILTER_DAT.ASPX'
}

edu_form_data_dummy = {
    'auth_user': {
        'TxtMiddle': '<r/>',
        'Fm_Action': '00',
        'Frm_Type': '',
        'Frm_No': '',
        'TicketTextBox': '',
    },
    '102': lambda ticket_textbox: {
        'Fm_Action': '00',
        'Frm_Type': '',
        'Frm_No': '',
        'F_ID': '',
        'XmlPriPrm': '',
        'XmlPubPrm': '',
        'XmlMoredi': '',
        'F9999': '',
        'HelpCode': '',
        'Ref1': '',
        'Ref2': '',
        'Ref3': '',
        'Ref4': '',
        'Ref5': '',
        'NameH': '',
        'FacNoH': '',
        'GrpNoH': '',
        'TicketTextBox': ticket_textbox,
        'RepSrc': '',
        'ShowError': '',
        'TxtMiddle': '<r/>',
        'tbExcel': '',
        'txtuqid': '',
        'ex': ''
    }
}

edu_form_data = {
    'auth_user': lambda user, password, captcha: {
        'TxtMiddle': '<r F51851="" F80351="%s" F80401="%s" F51701="%s" F83181=""/>'%(user, password, captcha),
        'Fm_Action': '09',
        'Frm_Type': '',
        'Frm_No': '',
        'TicketTextBox': '',
    },
    '102': lambda ticket_textbox, term, csfv: {
        'Fm_Action': '09',
        'Frm_Type': '',
        'Frm_No': '',
        'F_ID': '',
        'XmlPriPrm': '<Root><N UQID="48" id="4" F="" T=""/><N UQID="50" id="8" F="" T=""/><N UQID="52" id="12" F="" T=""/><N UQID="62" id="16" F="" T=""/><N UQID="14" id="18" F="" T=""/><N UQID="16" id="20" F="" T=""/><N UQID="18" id="22" F="" T=""/><N UQID="20" id="24" F="" T=""/><N UQID="22" id="26" F="" T=""/></Root>',
        'XmlPubPrm': '<Root><N id="4" F1="%s" T1="%s" F2="" T2="" A="1" S="1" Q="1" B="B"/><N id="6" F1="%s" T1="%s" F2="" T2="" A="" S="" Q="" B=""/><N id="12" F1="" T1="" F2="" T2="" A="0" S="1" Q="2" B="B"/><N id="16" F1="" T1="" F2="" T2="" A="0" S="1" Q="3" B="B"/><N id="20" F1="" T1="" F2="" T2="" A="0" S="" Q="6" B="S"/><N id="24" F1="" T1="" F2="" T2="" A="0" S="" Q="7" B="S"/></Root>'%(term, term, csfv, csfv),
        'XmlMoredi': '',
        'F9999': '',
        'HelpCode': '',
        'Ref1': '',
        'Ref2': '',
        'Ref3': '',
        'Ref4': '',
        'Ref5': '',
        'NameH': '',
        'FacNoH': '',
        'GrpNoH': '',
        'TicketTextBox': ticket_textbox,
        'RepSrc': '',
        'ShowError': '',
        'TxtMiddle': '<r/>',
        'tbExcel': '',
        'txtuqid': '',
        'ex': ''
    }
}