import requests

def quick_functional_test_of_invalidprovider():

    url = "http://localhost:6543/server/login/openid"
    r = requests.post(url, data={'openid_identifier':
                                 'http://paulbrian.myopenid.foobar'})
    assert(r.text.find("Failed validation: Error fetching XRDS document: ") >=0)
    

if __name__ == '__main__':
    quick_functional_test_of_invalidprovider()
