import pycurl
import config
import io as bio


def http_request(url, post_data=None):
    # Make an HTTP request to a given URL with optional parameters.

    print(url)
    print("data:  "+str(post_data))
    buf = bio()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url.encode('ascii', 'ignore'))

    # Disable HTTPS verification methods if insecure is set
    curl.setopt(curl.SSL_VERIFYPEER, 0)
    curl.setopt(curl.SSL_VERIFYHOST, 0)

    if post_data:
        curl.setopt(curl.HTTPPOST, post_data)
    curl.setopt(curl.WRITEFUNCTION, buf.write)
    curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_DIGEST)
    curl.setopt(pycurl.USERPWD, "%s:%s" % (config.targetuser,
                                           config.targetpassword))
    curl.setopt(curl.HTTPHEADER, ['X-Requested-Auth: Digest'])
    curl.setopt(curl.FAILONERROR, True)
    curl.setopt(curl.FOLLOWLOCATION, True)
    perform = curl.perform()
    curl.close()
    result = buf.getvalue()
    buf.close()
    return result
