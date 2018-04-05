import urllib2, base64, json
class Result(object):
    def __init__(self, result, headers=None):
        if headers == None:
            info = result.info()
            self.headers = info.headers
        self.contents = json.loads(result.read())
    
class Spark(object):
    
    def __init__(self, token):
        self.token = token
    
    def simple_request(self, url, data=None):
        request = urllib2.Request(url, data,
                                headers={"Accept" : "application/json",
                                         "Content-Type":"application/json"})
        request.add_header("Authorization", "Bearer " + self.token)
        return request
    
    def get(self, url):
        request = self.simple_request(url)
        response = urllib2.urlopen(request)
        return Result(response)
    
    def put(self, url, data):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, json.dumps(data),
                                headers={"Accept" : "application/json",
                                         "Content-Type":"application/json"})
        request.add_header("Authorization", "Bearer " + self.token)
        request.get_method = lambda: 'PUT'
        response = opener.open(request)
        return Result(response, headers=response.headers)

    def delete(self, url):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url,
                                headers={"Accept" : "application/json",
                                         "Content-Type":"application/json"})
        request.add_header("Authorization", "Bearer " + self.token)
        request.get_method = lambda: 'DELETE'
        response = opener.open(request)
        return Result(response, headers=response.headers)
    
    def post(self, url, data):
        request = self.simple_request(url, json.dumps(data))
        response = urllib2.urlopen(request)
        return Result(response)
