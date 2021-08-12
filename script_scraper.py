import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import os
from tqdm import tqdm

# Site we want to scrape
url = "https://www.w3schools.com/"

# initializing a session
session = requests.Session()

# set the User-agent as a regular browser
session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"

# to get the HTML file content
html = session.get(url).content

# parsing the HTML using beautiful soup
soup = bs(html, "html.parser")

# get the JavaScript files

# list which will contain all js files
script_files = []


# Searching for script tag with src attribute
for script in soup.find_all("script"):
    if script.attrs.get("src"):
        # if the tag has the attribute 'src'
        script_url = urljoin(url, script.attrs.get("src"))
        script_files.append(script_url)


# get the CSS files

# list which will contain all js files
css_files = []


# Searching for link tag with href attribute
for css in soup.find_all("link"):
    if css.attrs.get("href"):
        # if the link tag has the 'href' attribute
        css_url = urljoin(url, css.attrs.get("href"))
        css_files.append(css_url)

print("Total CSS files found:", len(css_files))
print("Total script files found:", len(script_files))

# Writing the absolute path of files in our css and js files using file handling

with open("css_files.txt", "w") as f:
    for css_file in css_files:
        print(css_file, file=f)

with open("js_files.txt", "w") as f:
    for js_file in script_files:
        print(js_file, file=f)

# If the website being scraped, bans your IP address, then use a proxy server.

# we just check if 'netloc': domain name & 'scheme': protocol is there or not
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


# this will get all image urls of the site
def get_all_images(url):
    
    soup = bs(requests.get(url).content, "html.parser")

# Now all the html file content is in 'soup' object
# we need to find the image tags from it

    urls = []

    # tqdm will print a progress bar here
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url: # in case of no scr attrbt found
            continue

        # getting the absolute url, by joining domain name with the retrieved urls
        img_url = urljoin(url, img_url)

        # if url has HTTP GET key value pair e.g. '/abc.png?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]  # find the '?' position and remove everything after it

        except ValueError:
            pass

        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls


def download(url, pathname):
    
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

def main(url, path):
    imgs = get_all_images(url)
    for img in imgs:
        
        download(img, path)

main("https://www.w3schools.com/", 'w3-images')