import re
from datetime import datetime
from collections import namedtuple


def format_cef(
        vendor, product, product_version, event_id, event_name, severity,
        extensions):
    """Produces a CEF compliant message from the arguments.

    :parameter str vendor: Vendor part of the product type identifier
    :parameter str product: Product part of the product type identifier
    :parameter str product_version: Version part of the product type identifier
    :parameter str event_id: A unique identifier for the type of event being
        reported
    :parameter str event_name: A human-friendly description of the event
    :parameter int severity: Between 0 and 10 inclusive.
    :parameter dict extensions: key-value pairs for event metadata.
    """
    extension_strs = {
        valid_extensions[name].key_name:
            _equals_escaper(valid_extensions[name].sanitiser(value, name))
        for name, value in extensions.items()}
    extensions_str = ' '.join(sorted(
        '{}={}'.format(k, v) for k, v in extension_strs.items()))
    pfs = _prefix_field_str_sanitiser
    return '|'.join((
        'CEF:0', pfs(vendor, 'VENDOR'), pfs(product, 'PRODUCT'),
        pfs(product_version, 'VERSION'), pfs(event_id, 'EVENT_ID'),
        pfs(event_name, 'EVENT_NAME'),
        _severity_sanitiser(severity, 'SEVERITY'), extensions_str))


def escaper(special_chars):
    strip_escaped_re = re.compile(
        r'\\([{}\\])'.format(special_chars))
    do_escape_re = re.compile(r'([{}\\])'.format(special_chars))

    def escape(s):
        stripped = strip_escaped_re.sub(r'\1', s)
        return do_escape_re.sub(r'\\\1', stripped)
    return escape


def int_sanitiser(max=0, min=0):
    def sanitise(n, debug_name):
        if not isinstance(n, int):
            raise TypeError('{}: Expected int, got {}'.format(
                debug_name, type(n)))
        elif not min <= n <= max:
            raise ValueError('{}: {} out of range {}-{}'.format(
                debug_name, n, min, max))
        else:
            return str(n)
    return sanitise


_severity_sanitiser = int_sanitiser(min=0, max=10)


def str_sanitiser(regex_str='.*', escape_chars='', min_len=0, max_len=None):
    regex = re.compile('^{}$'.format(regex_str))
    escape = escaper(escape_chars)

    def sanitise(s, debug_name):
        if not isinstance(s, basestring):
            raise TypeError('{}: Expected str, got {}'.format(
                debug_name, type(s)))
        elif not regex.match(s):
            raise ValueError(
                '{}: {!r} did not match regex {!r}'.format(
                    debug_name, s, regex_str))
        else:
            if isinstance(s, unicode):
                s = s.encode('utf-8')
            s = escape(s)
            if max_len is None:
                if len(s) <= min_len:
                    raise ValueError(
                        '{}: String longer than {} characters'.format(
                            debug_name, min_len))
            else:
                if not min_len <= len(s) <= max_len:
                    raise ValueError(
                        '{}: String length out of range {}-{}'.format(
                            debug_name, min_len, max_len))
            return s
    return sanitise


_prefix_field_str_sanitiser = str_sanitiser('[^\r\n]*', escape_chars='|')
_equals_escaper = escaper('=')


def datetime_sanitiser():
    def sanitise(t, debug_name):
        if not isinstance(t, datetime):
            raise TypeError('{}: Expected datetime, got {}'.format(
                debug_name, type(t)))
        else:
            return t.strftime('%b %d %Y %H:%M:%S')
    return sanitise


Extension = namedtuple('Extension', ('key_name', 'sanitiser'))
ipv4_addr = str_sanitiser(r'\.'.join(['\d{1,3}'] * 4))
str_31 = str_sanitiser(max_len=31)
str_63 = str_sanitiser(max_len=63)
str_1023 = str_sanitiser(max_len=1023)

# An incomplete list of valid CEF extensions
valid_extensions = {
    'deviceAction': Extension('act', str_63),
    'deviceAddress': Extension('dvc', ipv4_addr),
    'deviceHostName': Extension('dvchost', str_sanitiser(max_len=100)),
    'destinationAddress': Extension('dst', ipv4_addr),
    'destinationHostName': Extension('dhost', str_1023),
    'destinationPort': Extension('dpt', int_sanitiser(min=0, max=65535)),
    'destinationUserName': Extension('duser', str_1023),
    'endTime': Extension('end', datetime_sanitiser()),
    'fileName': Extension('fname', str_1023),
    'filePath': Extension('act', str_63),
    'message': Extension('msg', str_1023),
    'eventOutcome': Extension('outcome', str_63),
    'reason': Extension('reason', str_1023),
    'applicationProtocol': Extension('app', str_31),
    'transportProtocol': Extension('proto', str_31),
    'sourceAddress': Extension('src', ipv4_addr),
    'sourceHostName': Extension('shost', str_1023),
    'sourceUserName': Extension('suser', str_1023),
    'start': Extension('start', datetime_sanitiser()),
    'deviceCustomString1': Extension('cs1', str_1023),
    'deviceCustomStringLabel1': Extension('cs1Label', str_1023),
    'deviceCustomString2': Extension('cs2', str_1023),
    'deviceCustomStringLabel2': Extension('cs2Label', str_1023),
    'deviceCustomString3': Extension('cs3', str_1023),
    'deviceCustomStringLabel3': Extension('cs3Label', str_1023),
    'deviceCustomString4': Extension('cs4', str_1023),
    'deviceCustomStringLabel4': Extension('cs4Label', str_1023),
    'deviceCustomString5': Extension('cs5', str_1023),
    'deviceCustomStringLabel5': Extension('cs5Label', str_1023),
    'deviceCustomString6': Extension('cs6', str_1023),
    'deviceCustomStringLabel6': Extension('cs6Label', str_1023),
}
