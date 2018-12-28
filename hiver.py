import requests
from lxml import html
import re
from urllib.parse import urljoin
import string
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import os,sys
import nltk

path = os.path.dirname(os.path.realpath(sys.argv[0]))
nltk.data.path.append(path+'/nltk_data')

site_url = "https://hiverhq.com/"

lemma = WordNetLemmatizer()
exclude_words = set(string.punctuation)
stop_words = stopwords.words('english')
text_xpath = "//text()[not(parent::style) and not(parent::script)]"   
urls_xpath = '//a[@href!="" and not(contains(@href,"javascript:")) and not(starts-with(@href,"#"))]/@href|//iframe/@src|//frame/@src'
text_pattern = re.compile("(@[A-Za-z0-9]+)|([^A-Za-z \t])|(\w+:\/\/\S+)")

def domain_finder(url):
    """
    @doc: find domain name from url
    """
    try:
        domain = re.findall(r"^(?:https?:\/\/)?(?:www\.)?([^\/]+)",url,re.I)[0]
    except:
        return None
    return domain

def domain_maped_urls(urls,site_url):    
    links ={}
    for url in urls:
        url = urljoin(site_url,url)
        domain = domain_finder(url)
        if domain not in links.keys():
            links[domain] = []
        links[domain].append(url)
    return links

def clean(text):
    
    """
    This function return normalized text
    @param doc: Input string
    @return: Normalized text string
    """

    punc_free = (word for word in text.split() if word not in exclude_words)
    stop_free = (word for word in punc_free if word not in stop_words)
    text = " ".join(lemma.lemmatize(word) for word in stop_free)
    text = text_pattern.sub(" ", text)
    return text

def process_request(site_url):
    print("processing url: {}".format(site_url))
    response = requests.get(site_url)
    html_obj = html.fromstring(response.text)
    page_text = " ".join( text.strip() for text in html_obj.xpath(text_xpath) if text.strip())
    cleaned_text = clean(page_text.lower())
    return cleaned_text,html_obj

def main(site_url):
    word_count = {}
    domain = domain_finder(site_url)
    _, html_obj = process_request(site_url)
    all_urls = domain_maped_urls(html_obj.xpath(urls_xpath),site_url)
    for url in set(all_urls[domain]):
        text,_ = process_request(url)
        for word in text.split():
            if word.strip():
                if word_count.get(word, None):
                    word_count[word]+=1
                else:
                    word_count[word] = 1
    return word_count
                

if __name__ == "__main__":
    if len(sys.argv) == 2:
        site_url = sys.argv[1]
    word_count = main(site_url)
    inverted_dict = {value:key for key,value in word_count.items()}
    word_frequency = list(inverted_dict.keys())
    word_frequency.sort(reverse=True)
    top_ten_keywords = word_frequency[:10]
    print ("Top ten mentioned(descending order) words on website are:\n")
    for frequency in top_ten_keywords:
        print(inverted_dict[frequency]+"\n")
