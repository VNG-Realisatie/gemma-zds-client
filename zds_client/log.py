from datetime import datetime


class Log:
    _entries = []
    max_entries = 100

    @classmethod
    def add(cls, service, url, method, request_headers, request_data, response_status, response_headers, response_data):
        # Definitly not thread-safe
        if len(cls._entries) >= cls.max_entries:
            cls._entries.pop(0)

        entry = {
            'timestamp': datetime.now(),
            'service': service,
            'request': {
                'url': url,
                'method': method,
                'headers': request_headers,
                'data': request_data,
            },
            'response': {
                'status': response_status,
                'headers': response_headers,
                'data': response_data,
            }
        }

        cls._entries.append(entry)

    @classmethod
    def clear(cls):
        cls._entries = []

    @classmethod
    def entries(cls):
        return cls._entries
