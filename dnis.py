import json
from collections import defaultdict
from datetime import datetime, timezone


class PhoneStatistics:

    def __init__(self, phone):
        self._phone = phone
        self._calls = []

    def add_call(self, call):
        self._calls.append(call)

    @property
    def calls(self):
        return self._calls



class DnisFrame:

    def __init__(self, **params):
        self.params = params

    
    
class DnisStatistics:

    """
    Calling-Number
    Date
    Total Ingress Attempt
    Valid Ingress Attempt
    Non Zero Call
    Total Duration
    """
    
    def __init__(self, dnis, **params):
        self.dnis = dnis
        self._cnt = 1
        self.params = params
        self.errors = defaultdict(int)
        self._duration = 0
        self.connection_date = None
        self._total_ingress_attempt = 0
        self._valid_ingress_attempt = 0
        self._lrn = dnis[:3]
        self._calls = []

        
    def add_error(self, error):
        self.errors[error] += 1

    def add_pdd(self, pdd):
        self._pdds.append(pdd)

    def add_call(self, call):
        self._calls.append(call)
        
    def upsert_connection_date(self, new_timestamp):
        if new_timestamp and new_timestamp != "0":
            new_timestamp = datetime.fromtimestamp(float(str(new_timestamp[:10])),
                                                   timezone.utc)
            if not self.connection_date:
                self.connection_date = new_timestamp
                return new_timestamp
            
            if self.connection_date < new_timestamp:
                self.connection_date = new_timestamp
                
        return self.connection_date
        
    def to_json(self):
        object_dump = self.__dict__
        date_val = getattr(self, 'connection_date')
        if date_val:
            date_val = date_val.strftime("%Y-%m-%d %H:%M:%S.%Z")
            object_dump["connection_date"] = date_val
        
        return self.__dict__

    @property
    def lrn(self):
        return self._lrn

    @property
    def carrier(self):
        return self._carrier
    
    @carrier.setter
    def carrier(self, value):
        self._carrier = value
    
    @property
    def total_attempt(self):
        return self._total_ingress_attempt

    @total_attempt.setter
    def total_attempt(self, value):
        self._total_ingress_attempt = value

    @property
    def valid_attempt(self):
        return self._valid_ingress_attempt

    @valid_attempt.setter
    def valid_attempt(self, value):
        self._valid_ingress_attempt = value
    
    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration += value
    
    @property
    def code_200(self):
        return self._code_200

    @code_200.setter
    def code_200(self, value):
        self._code_200 = value

    @property
    def code_404(self):
        return self._code_404

    @code_404.setter
    def code_404(self, value):
        self._code_404 = value

    @property
    def code_503(self):
        return self._code_503

    @code_503.setter
    def code_503(self, value):
        return self._code_503

    @property
    def code_486(self):
        return self._code_486

    @code_486.setter
    def code_486(self, value):
        self._code_486 = value

    @property
    def code_487(self):
        return self._code_487

    @code_487.setter
    def code_487(self, value):
        self._code_487 = value

    @property
    def code_402(self):
        self._code_402

    @code_402.setter
    def code_402(self, value):
        self._code_402 = value

    @property
    def code_480(self):
        return self._code_480

    @code_480.setter
    def code_480(self, value):
        self._code_480 = value

    @property
    def code_other_4(self):
        return self._code_other_4

    @code_other_4.setter
    def code_other_4(self, value):
        self._code_other_4 = value

    @property
    def code_other_5(self):
        return self._code_other_5

    @code_other_5.setter
    def code_other_4(self, value):
        self._code_other_5 = value

    @property
    def last_connection_on(self):
        return self._last_connection_on

    @property
    def last_block_on(self):
        return self._xlast_block_on

    @property
    def cnt(self):
        return self._cnt

    @cnt.setter
    def cnt(self, value):
        self._cnt = value
