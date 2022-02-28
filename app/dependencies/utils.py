from typing import Any


class StatusResponse:
    success = 0
    error = 100

class StatusCreator(StatusResponse):
    def __init__(self):
        self._applyStatusAsAttribute()

    def _applyStatusAsAttribute(self):
        allAttr = [i for i in vars(StatusResponse) if not "_" in [i[0], i[-1]]]
        for a in allAttr:
            def fetcher(attrName):
                def response(message: Any = str(attrName).replace("_", " ")):
                    code = StatusResponse.__dict__[attrName]
                    return {
                        "code": code,
                        "message": str(message)
                        }
                return response
            self.__dict__[a] = fetcher(a)

status = StatusCreator()

def create_response(data={}, meta={}, status={}):
    return {
        "data": data,
        "meta": meta,
        "status": status
    }

def get_query_dict(query_byte: bytes):
    query = query_byte.decode("utf-8")
    query = [q.split("=") for q in query.split("&")]
    return {k: v for k,v in query}

def extract_and_count_object(data: list):
    datas = []
    i = 0
    for d in data:
        i += 1
        datas.append(
            {k: v for k,v in d.__dict__.items() if "_" not in [k[0], k[-1]]}
            )
    return i, datas