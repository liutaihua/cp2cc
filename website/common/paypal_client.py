import cgi
import urllib
from httplib import HTTPSConnection

from mochiads_lib import cfg

class PaypalError(Exception):
    pass

def paypal_request(host, body, path=None):
    if path is None:
        path = '/cgi-bin/webscr'

    conn = HTTPSConnection(host, 443)
    conn.request('POST', path, body,
                 {'Content-Type': 'application/x-www-form-urlencoded'})

    return conn.getresponse()


def get_info_for_paypal_txn(tx, reqfn=paypal_request):
    token = cfg.get_config_value('paypal_token')
    urlencoded = urllib.urlencode(
        [('cmd', '_notify-synch'), ('tx', tx), ('at', token)])

    result = reqfn(
        cfg.get_config_value('paypal_domain'),
        urlencoded)

    body = result.read()

    if not body.startswith('SUCCESS\n'):
        raise PaypalError('%s with %s returned %s' % (
                cfg.get_config_value('paypal_domain'),
                urlencoded,
                body))

    success, rest = body.split('\n', 1)

    response_args = dict(
        (key, urllib.unquote_plus(val).decode('utf-8'))
        for (key, val) in
        [x.split('=', 1) for x in rest.split('\n') if x.strip()])

    return response_args


def validate_ipn(post_data, reqfn=paypal_request):
    """
    Returns A 2-tuple of a bool and a 2-tuple or None.
    The bool will be True when the ipn validates, otherwise it will be false.
    When the bool is false the second item will be a 2-tuple of
    request and response
    """
    body = urllib.urlencode(post_data)
    body += '&cmd=_notify-validate'

    response = reqfn(
        cfg.get_config_value('paypal_domain'),
        body)

    response_body = response.read()
    if not (response.status == 200 and response_body == 'VERIFIED'):
        return False, (body, response_body)

    return True, None


TEMPLATE = "USER=%(user)s&PWD=%(pwd)s&VERSION=55.0&SIGNATURE=%(signature)s&METHOD=DoDirectPayment&PAYMENTACTION=Sale&IPADDRESS=%(ipaddress)s&CREDITCARDTYPE=%(cctype)s&ACCT=%(ccnum)s&EXPDATE=%(expdate)s&CVV2=%(cvv2)s&EMAIL=%(email)s&COUNTRYCODE=%(countrycode)s&BUSINESS=%(business)s&SALUTATION=%(salutation)s&FIRSTNAME=%(firstname)s&MIDDLENAME=%(middlename)s&LASTNAME=%(lastname)s&SUFFIX=%(suffix)s&STREET=%(street)s&STREET2=%(street2)s&CITY=%(city)s&STATE=%(state)s&ZIP=%(zip)s&PHONENUM=%(phonenum)s&AMT=%(amt)s&NOTIFYURL=%(notifyurl)s"


def do_paypal_pro(fields, remote_ip, ipn_url, reqfn=paypal_request):
    new = fields.copy()
    new.update(
        dict(
            user=cfg.get_config_value('paypal_pro_user'),
            pwd=cfg.get_config_value('paypal_pro_password'),
            signature=cfg.get_config_value('paypal_pro_signature'),
            ipaddress=remote_ip,
            notifyurl=ipn_url))

    if 'middlename' not in new:
        ## Hack so maguire can leave the middle name out of the form
        new['middlename'] = ''
    if 'suffix' not in new:
        new['suffix'] = ''

    new = dict((key, urllib.quote(value.encode('utf-8')))
               for (key, value) in new.items())

    body = TEMPLATE % new
    domain = cfg.get_config_value('paypal_pro_domain')
    result = reqfn(domain, body, '/nvp')
    result = cgi.parse_qs(result.read())
    return result


GET_TRANSACTION_DETAILS_TEMPLATE = "USER=%(user)s&PWD=%(pwd)s&VERSION=55.0&SIGNATURE=%(signature)s&METHOD=GetTransactionDetails&TRANSACTIONID=%(tx)s"


PAYPAL_SUCKS = {
    'AMT': 'mc_gross',
    'CURRENCYCODE': 'mc_currency',
    'FIRSTNAME': 'first_name',
    'LASTNAME': 'last_name',
    'PAYMENTSTATUS': 'payment_status',
    'TRANSACTIONID': 'txn_id',
}


def get_pro_transaction_details(tx, reqfn=paypal_request):
    stuff = dict(
        user=urllib.quote(cfg.get_config_value('paypal_pro_user')),
        pwd=cfg.get_config_value('paypal_pro_password'),
        signature=cfg.get_config_value('paypal_pro_signature'),
        tx=tx
    )

    domain = cfg.get_config_value('paypal_pro_domain')
    result = reqfn(
        domain,
        GET_TRANSACTION_DETAILS_TEMPLATE % stuff,
        '/nvp')

    body = result.read()

    response_args = dict(
        (key, urllib.unquote_plus(val).decode('utf-8'))
        for (key, val) in
        [x.split('=', 1) for x in body.split('&') if x.strip()])

    if response_args.get('ACK') == 'Failure':
        raise PaypalError('%s with %s returned %s' % (
                cfg.get_config_value('paypal_domain'),
                GET_TRANSACTION_DETAILS_TEMPLATE % stuff,
                body))

    for (key, key2) in PAYPAL_SUCKS.items():
        response_args[key2] = response_args[key]

    return response_args

