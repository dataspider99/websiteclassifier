import requests
from lxml import html
import re
from tld import get_tld
from urllib.parse import urljoin
import string
from nltk.stem.wordnet import WordNetLemmatizer

site_url = "https://hiverhq.com/"

lemma = WordNetLemmatizer()
exclude_words = set(string.punctuation)
text_xpath = "//text()[not(parent::style) and not(parent::script)]"   
urls_xpath = '//a[@href!="" and not(contains(@href,"javascript:")) and not(starts-with(@href,"#"))]/@href|//iframe/@src|//frame/@src'
url_pattern = re.compile("^(?:https?:\/\/)?(?:www\.)?([^\/]+)")
text_pattern = re.compile("(@[A-Za-z0-9]+)|([^A-Za-z \t])|(\w+:\/\/\S+)")

def domain_finder(url):
    """
    @doc: find domain name from url
    """
    try:
        domain = get_tld(url)
    except:
        try:
            domain = url_pattern.findall(url,re.I)[0]
        except:
            return None
    return domain

def domain_maped_urls(urls):    
    links ={}
    for url in urls:
        url = urljoin(site_url, url)
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

    punc_free = ' '.join(word for word in text.split() if word not in exclude_words)
    text = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    text = ' '.join(text_pattern.sub(" ", text).split())
    return text

def main(site_url):
    response = requests.get(site_url)
    html_obj = html.fromstring(response.text)
    page_text = " ".join( text.strip() for text in html_obj.xpath(text_xpath) if text.strip())
    cleaned_text = clean(page_text.lower())
    all_urls = domain_maped_urls(html_obj.xpath(urls_xpath))
