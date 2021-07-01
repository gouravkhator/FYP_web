try:
    import concurrent.futures
    import requests
    import time
    import os
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup
    import pandas as pd
except Exception as e:
    print("Some modules could not be imported")
    exit(1)

def get_free_proxies():
    ua = UserAgent()
    # generate a random user agent for the request
    user_agent = ua.random
    
    # store the url of the proxy site as a string
    url = 'https://free-proxy-list.net/'
    
    # structure request header
    ua_header = {'User-Agent': user_agent}
    
    # make a GET request from the url
    content = requests.get(url, headers = ua_header).text

    soup = BeautifulSoup(content,'html.parser')
    rows=[]
    for row in soup.findAll("tr"):
        rows.append(row)
    
    elite_https_proxies = []

    # Find the rows that are elite proxy and 'Yes' to the https column
    for row in rows:
        i = row.findAll('td')
        try:
            if i[4].text == 'elite proxy' and i[6].text == 'yes':
                # Append IP to a list (column 0 is the IP, column 1 is the port)
                elite_https_proxies.append(i[0].text + ':' + i[1].text)
        except:
            continue
        
    df = pd.DataFrame(elite_https_proxies, columns=["proxy_ip"])
    proxy_filepath = os.path.normpath('app/outputs/free_proxies.csv')

    df.to_csv(proxy_filepath, index_label='id')
    return elite_https_proxies

def get_poster_image_path(imdb_id, proxy):
    print("Imdb :",imdb_id, "Proxy :", proxy)
    ua = UserAgent()
    user_agent = ua.random
    ua_header = {'User-Agent': user_agent}
    page = requests.get("https://www.imdb.com/title/"+imdb_id.strip(), headers = ua_header, proxies={"https":"https://"+proxy, "http":"http://"+proxy})

    '''
    page.content is the whole html content.
    BeautifulSoup helps parsing the html content.
    '''
    bsoup = BeautifulSoup(page.content, 'html.parser')
    
    '''
    as there are 16 elements which have exactly this class but, the first one has the poster path of the movie concerned
    '''
    poster_img_element = bsoup.select('.ipc-poster--baseAlt .ipc-media--poster img.ipc-image')[0]

    poster_path_url =  poster_img_element.get('src')
    print("URL: ", poster_path_url)
    return poster_path_url

def get_poster_path_urls(imdb_id_list):
    # get the list of proxies
    proxy_filepath = os.path.normpath('app/outputs/free_proxies.csv')

    if not os.path.exists(proxy_filepath):
        get_free_proxies()

    proxy_df = pd.read_csv(proxy_filepath, index_col='id')
    proxy_list = proxy_df['proxy_ip'].tolist()
    
    MAX_THREADS = 100
    threads = min(MAX_THREADS, len(imdb_id_list))
    poster_urls = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        result_iterator = executor.map(get_poster_image_path, imdb_id_list, proxy_list)
    
        for future in concurrent.futures.as_completed(result_iterator):
            imdb_id_temp = result_iterator[future]
            try:
                poster_urls.append((imdb_id_temp, imdb_id_temp.result()))
            except Exception as exc:
                print('%r generated an exception: %s' % (imdb_id_temp, exc))

    return poster_urls

if __name__ == "__main__":
    print("----Web Scraping Poster Path Generator----")
    # imdb_id = input("Enter the movie's imdb id: ").strip()

    # print("\nPoster path url for the given imdb id is :\n\n",get_poster_image_path(imdb_id=imdb_id))
    
    df = pd.read_csv("app/outputs/metadata_smd_small.csv", index_col="Id")

    print("Started method execution..")
    t0 = time.time()
    
    poster_urls = get_poster_path_urls(df["imdb_id"].tolist())
    t1 = time.time()
    print(f"{t1-t0} seconds to execute thread version on small dataset of approx. 9k entries...")

    poster_url_imdb_mapping = {
        "imdb_id": [i[0] for i in poster_urls],
        "poster_path": [i[1] for i in poster_urls]
    }
    df = pd.DataFrame(poster_url_imdb_mapping, columns=["imdb_id", "poster_path"])

    print('Saving the urls to csv file..')
    poster_urls_filepath = os.path.normpath('app/outputs/poster_path_urls.csv')

    df.to_csv(poster_urls_filepath, index_label="imdb_id")
