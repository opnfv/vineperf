# Copyright 2016-2017 Spirent Communications.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
@author Spirent Communications
Client class and exception for performing basic ReST API interactions.

'''

from __future__ import print_function

import base64
import os
import sys
import json
import requests


class RestHttpError(Exception):

    """
    Exception object that returns error from remote call.

    """

    def __init__(self, http_status, http_reason, msg=None, code=None):
        self.http_status = int(http_status)
        self.http_error = '%s %s' % (http_status, http_reason)
        self.msg = msg
        self.code = code

    def __int__(self):
        """Get HTTP status code."""
        return self.http_status

    def __str__(self):
        """Get error message."""
        if self.msg:
            return '%s: %s' % (self.http_error, self.msg)
        return self.http_error

    def code(self):
        """Get API error code."""
        return self.code

    def status(self):
        """Get HTTP status."""
        return self.http_status


class ConnectionError(Exception):

    def __init__(self, message, code, detail=None):
        if detail:
            self.msg = '%s: %s' % (message.rstrip('.'), detail)
        else:
            self.msg = message.rstrip('.')

        self.code = int(code)

    def __int__(self):
        """Get errno value."""
        return self.code

    def __str__(self):
        """Get error message."""
        return self.msg

    def __repr__(self):
        """Get object representation string."""
        if self.msg.find(': ') != -1:
            m, d = self.msg.split(': ', 1)
            return 'ConnectionError(message=%s, code=%d, detail=%s)' % (
                m, self.code, d)
        return 'ConnectionError(message=%s, code=%d)' % (self.msg, self.code)


class RestHttp(object):

    """
    ReST API HTTP client wrapper object base class.

    Derive application-specific ReST API class from this base class.

    """

    def __init__(self, base_url, user=None, password=None, ssl_verify=True,
                 debug_print=False):
        """Initialize the ReST API HTTP wrapper object.

        Arguments:
        base_url    -- Base URL for requests.  Ex: http://example.com/stuff/
        user        -- Optional user name for basic auth.
        password    -- Optional password for basic auth.
        ssl_verify  -- Set to False to disable SSL verification (not secure).
        debug_print -- Enable debug print statements.

        """
        self._base_url = base_url.strip('/')

        self._base_headers = {'Accept': 'application/json', 'Content-Type':'application/json'}
        self._user = user
        self._password = password
        self._verify = ssl_verify
        self._dbg_print = debug_print

        # autheticated API
        if user and password:
            b64string = base64.encodestring('%s:%s' % (user, password))[:-1]
            self._base_headers["Authorization"] = "Basic %s" % b64string

    @staticmethod
    def url(proto, server, port=None, uri=None):
        """Construct a URL from the given components."""
        url_parts = [proto, '://', server]
        if port:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError('invalid port value')
            if not ((proto == 'http' and port == 80) or
                    (proto == 'https' and port == 443)):
                url_parts.append(':')
                url_parts.append(str(port))

        if uri:
            url_parts.append('/')
            url_parts.append(requests.utils.quote(uri.strip('/')))

        url_parts.append('/')
        return ''.join(url_parts)

    def debug_print(self):
        """Return True if debug printing enabled."""
        return self._dbg_print

    def enable_debug_print(self):
        """Turn debug printing on."""
        self._dbg_print = True

    def disable_debug_print(self):
        """Turn debug printing off."""
        self._dbg_print = False

    def add_header(self, header, value):
        """Include additional header with each request."""
        self._base_headers[header] = value

    def del_header(self, header):
        """Removed a header from those included with each request."""
        self._base_headers.pop(header, None)

    def base_url(self):
        """Return the base URL used for each request."""
        return self._base_url

    def make_url(self, container=None, resource=None, query_items=None):
        """Create a URL from the specified parts."""
        pth = [self._base_url]
        if container:
            pth.append(container.strip('/'))
        if resource:
            pth.append(resource)
        else:
            pth.append('')
        url = '/'.join(pth)
        if isinstance(query_items, (list, tuple, set)):
            url += RestHttp._list_query_str(query_items)
            query_items = None
        p = requests.PreparedRequest()
        p.prepare_url(url, query_items)
        return p.url

    def head_request(self, container, resource=None):
        """Send a HEAD request."""
        url = self.make_url(container, resource)
        headers = self._make_headers(None)

        try:
            rsp = requests.head(url, headers=self._base_headers,
                                verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('HEAD', rsp.url, headers, None)

        return rsp.status_code

    def get_request(self, container, resource=None, query_items=None,
                    accept=None, to_lower=False):
        """Send a GET request."""
        url = self.make_url(container, resource)
        headers = self._make_headers(accept)

        if query_items and isinstance(query_items, (list, tuple, set)):
            url += RestHttp._list_query_str(query_items)
            query_items = None

        try:
            rsp = requests.get(url, query_items, headers=headers,
                               verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('GET', rsp.url, headers, None)

        return self._handle_response(rsp, to_lower)

    def post_request(self, container, resource=None, params=None, accept=None):
        """Send a POST request."""
        url = self.make_url(container, resource)
        headers = self._make_headers(accept)

        try:
            rsp = requests.post(url, data=json.dumps(params), headers=headers,
                                verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('POST', rsp.url, headers, params)

        return self._handle_response(rsp)

    def put_request(self, container, resource=None, params=None, accept=None):
        """Send a PUT request."""
        url = self.make_url(container, resource)
        headers = self._make_headers(accept)

        try:
            rsp = requests.put(url, params, headers=headers,
                               verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('PUT', rsp.url, headers, params)

        return self._handle_response(rsp)

    def delete_request(self, container, resource=None, query_items=None,
                       accept=None):
        """Send a DELETE request."""
        url = self.make_url(container, resource)
        headers = self._make_headers(accept)

        if query_items and isinstance(query_items, (list, tuple, set)):
            url += RestHttp._list_query_str(query_items)
            query_items = None

        try:
            rsp = requests.delete(url, params=query_items, headers=headers,
                                  verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('DELETE', rsp.url, headers, None)

        return self._handle_response(rsp)

    def download_file(self, container, resource, save_path=None, accept=None,
                      query_items=None):
        """Download a file."""
        url = self.make_url(container, resource)
        if not save_path:
            save_path = resource.split('/')[-1]

        headers = self._make_headers(accept)

        if query_items and isinstance(query_items, (list, tuple, set)):
            url += RestHttp._list_query_str(query_items)
            query_items = None

        try:
            rsp = requests.get(url, query_items, headers=headers, stream=True,
                               verify=self._verify)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)

        if self._dbg_print:
            self.__print_req('GET', rsp.url, headers, None)

        if rsp.status_code >= 300:
            raise RestHttpError(rsp.status_code, rsp.reason, rsp.text)

        file_size_dl = 0
        try:
            with open(save_path, 'wb') as f:
                for buff in rsp.iter_content(chunk_size=16384):
                    f.write(buff)
        except Exception as e:
            raise RuntimeError('could not download file: ' + str(e))
        finally:
            rsp.close()

        if self._dbg_print:
            print('===> downloaded %d bytes to %s' % (file_size_dl, save_path))

        return rsp.status_code, save_path, os.path.getsize(save_path)

    def upload_file(self, container, src_file_path, dst_name=None, put=True,
                    content_type=None):
        """Upload a single file."""
        if not os.path.exists(src_file_path):
            raise RuntimeError('file not found: ' + src_file_path)
        if not dst_name:
            dst_name = os.path.basename(src_file_path)
        if not content_type:
            content_type = "application/octet.stream"
        headers = dict(self._base_headers)
        if content_type:
            headers["content-length"] = content_type
        else:
            headers["content-length"] = "application/octet.stream"
        headers["content-length"] = str(os.path.getsize(src_file_path))
        headers['content-disposition'] = 'attachment; filename=' + dst_name
        if put:
            method = 'PUT'
            url = self.make_url(container, dst_name, None)
        else:
            method = 'POST'
            url = self.make_url(container, None, None)
        with open(src_file_path, 'rb') as up_file:
            try:
                rsp = requests.request(method, url, headers=headers,
                                       data=up_file)
            except requests.exceptions.ConnectionError as e:
                RestHttp._raise_conn_error(e)

        return self._handle_response(rsp)

    def upload_file_mp(self, container, src_file_path, dst_name=None,
                       content_type=None):
        """Upload a file using multi-part encoding."""
        if not os.path.exists(src_file_path):
            raise RuntimeError('file not found: ' + src_file_path)
        if not dst_name:
            dst_name = os.path.basename(src_file_path)
        if not content_type:
            content_type = "application/octet.stream"
        url = self.make_url(container, None, None)
        headers = self._base_headers
        with open(src_file_path, 'rb') as up_file:
            files = {'file': (dst_name, up_file, content_type)}
            try:
                rsp = requests.post(url, headers=headers, files=files)
            except requests.exceptions.ConnectionError as e:
                RestHttp._raise_conn_error(e)

        return self._handle_response(rsp)

    def upload_files(self, container, src_dst_map, content_type=None):
        """Upload multiple files."""
        if not content_type:
            content_type = "application/octet.stream"
        url = self.make_url(container, None, None)
        headers = self._base_headers
        multi_files = []
        try:
            for src_path in src_dst_map:
                dst_name = src_dst_map[src_path]
                if not dst_name:
                    dst_name = os.path.basename(src_path)
                multi_files.append(
                    ('files', (dst_name, open(src_path, 'rb'), content_type)))

            rsp = requests.post(url, headers=headers, files=multi_files)
        except requests.exceptions.ConnectionError as e:
            RestHttp._raise_conn_error(e)
        finally:
            for n, info in multi_files:
                dst, f, ctype = info
                f.close()

        return self._handle_response(rsp)

    ###########################################################################
    # private methods
    #

    def _make_headers(self, accept):
        if accept:
            headers = dict(self._base_headers)
            headers['Accept'] = accept
            return headers
        return self._base_headers

    def _handle_response(self, rsp, to_lower=False):
        if self._dbg_print:
            print('===> response status:', rsp.status_code, rsp.reason)

        app_json = 'application/json'
        data = None
        if rsp.status_code != 204:
            if rsp.headers.get('content-type', app_json).startswith(app_json):
                try:
                    data = rsp.json()
                except Exception:
                    data = None

            if data is None:
                data = rsp.content

            if data and sys.version < '3':
                # Py2.7
                data = self._uc_to_str(data, to_lower)
            elif to_lower:
                data = self._rsp_to_lower(data)

            if self._dbg_print:
                print('===> response content-type:',
                      rsp.headers.get('content-type'))
                print('===> DATA:', data)

        if rsp.status_code >= 300:
            code = None
            detail = None
            if (data and
                rsp.headers.get('content-type', '').startswith(app_json)):
                if isinstance(data, dict):
                    if 'detail' in data:
                        detail = data['detail']
                    elif 'message' in data:
                        detail = data['message']
                    elif data:
                        detail = 'unknown error: ' + str(data)
                    code = data.get('code')
                else:
                    detail = 'unknown error: ' + str(data)

            raise RestHttpError(rsp.status_code, rsp.reason, detail, code)

        return rsp.status_code, data

    @staticmethod
    def _list_query_str(items):
        return '?' + '&'.join(items)

    def _uc_to_str(self, data, lc):
        if isinstance(data, dict):
            return {self._uc_to_str(k, lc): self._uc_to_str(v, lc)
                    for k, v in data.iteritems()}
        elif isinstance(data, list):
            return [self._uc_to_str(i, lc) for i in data]
        elif isinstance(data, unicode):
            if lc:
                return str(data).lower()
            return str(data)
        elif isinstance(data, str) and lc:
            return data.lower()
        return data

    def _rsp_to_lower(self, data):
        if isinstance(data, dict):
            return {self._rsp_to_lower(k): self._rsp_to_lower(v)
                    for k, v in data.iteritems()}
        elif isinstance(data, list):
            return [self._rsp_to_lower(i) for i in data]
        elif isinstance(data, str):
            return data.lower()
        return data

    @staticmethod
    def _raise_conn_error(e):
        if isinstance(e, requests.exceptions.SSLError):
            raise ConnectionError(str(e), -1)
        try:
            msg, err = e.message
            num, detail = err
        except:
            msg = str(e)
            num = -1
            detail = None
        raise ConnectionError(msg, num, detail)

    def __print_req(self, method, url, headers, params):
        print('===> %s %s' % (method, url))
        print('  --- Headers ---')
        for k, v in headers.items():
            print('    %s: %s' % (k, v))
        if params:
            print('  --- Params ---')
            print('   ', params)
