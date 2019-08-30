# -*- coding: utf-8 -*-
"""
FileName:   utils
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/30

Description:

Changelog:
"""
import errno

ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)
if hasattr(errno, "WSAEWOULDBLOCK"):
    ERRNO_WOULDBLOCK += (errno.WSAEWOULDBLOCK,)  # type: ignore


def errno_from_exception(e):
    if hasattr(e, 'errno'):
        return e.errno  # type: ignore
    elif e.args:
        return e.args[0]
    else:
        return None


STATUS_CODES = {
    100: b"Continue",
    101: b"Switching Protocols",
    102: b"Processing",
    200: b"OK",
    201: b"Created",
    202: b"Accepted",
    203: b"Non-Authoritative Information",
    204: b"No Content",
    205: b"Reset Content",
    206: b"Partial Content",
    207: b"Multi-Status",
    208: b"Already Reported",
    226: b"IM Used",
    300: b"Multiple Choices",
    301: b"Moved Permanently",
    302: b"Found",
    303: b"See Other",
    304: b"Not Modified",
    305: b"Use Proxy",
    307: b"Temporary Redirect",
    308: b"Permanent Redirect",
    400: b"Bad Request",
    401: b"Unauthorized",
    402: b"Payment Required",
    403: b"Forbidden",
    404: b"Not Found",
    405: b"Method Not Allowed",
    406: b"Not Acceptable",
    407: b"Proxy Authentication Required",
    408: b"Request Timeout",
    409: b"Conflict",
    410: b"Gone",
    411: b"Length Required",
    412: b"Precondition Failed",
    413: b"Request Entity Too Large",
    414: b"Request-URI Too Long",
    415: b"Unsupported Media Type",
    416: b"Requested Range Not Satisfiable",
    417: b"Expectation Failed",
    418: b"I'm a teapot",
    422: b"Unprocessable Entity",
    423: b"Locked",
    424: b"Failed Dependency",
    426: b"Upgrade Required",
    428: b"Precondition Required",
    429: b"Too Many Requests",
    431: b"Request Header Fields Too Large",
    451: b"Unavailable For Legal Reasons",
    500: b"Internal Server Error",
    501: b"Not Implemented",
    502: b"Bad Gateway",
    503: b"Service Unavailable",
    504: b"Gateway Timeout",
    505: b"HTTP Version Not Supported",
    506: b"Variant Also Negotiates",
    507: b"Insufficient Storage",
    508: b"Loop Detected",
    510: b"Not Extended",
    511: b"Network Authentication Required",
}


# According to https://tools.ietf.org/html/rfc2616#section-7.1
_ENTITY_HEADERS = frozenset(
    [
        "allow",
        "content-encoding",
        "content-language",
        "content-length",
        "content-location",
        "content-md5",
        "content-range",
        "content-type",
        "expires",
        "last-modified",
        "extension-header",
    ]
)


def is_entity_header(header):
    """Checks if the given header is an Entity Header"""
    return header.lower() in _ENTITY_HEADERS


def remove_entity_headers(headers, allowed=("content-location", "expires")):
    """
    Removes all the entity headers present in the headers given.
    According to RFC 2616 Section 10.3.5,
    Content-Location and Expires are allowed as for the
    "strong cache validator".
    https://tools.ietf.org/html/rfc2616#section-10.3.5

    returns the headers without the entity headers
    """
    allowed = set([h.lower() for h in allowed])
    headers = {
        header: value
        for header, value in headers.items()
        if not is_entity_header(header) and header.lower() not in allowed
    }
    return headers
