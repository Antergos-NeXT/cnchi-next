import urllib.request
import urllib.error

try:
    packages_xml = urllib.request.urlopen('https://github.com/Antergos-NeXT/packages-0.8.xml')
except urllib.error.URLError as e:
    # If the installer can't retrieve the remote file, try to install with a local
    # copy, that may not be updated
    print(e)

