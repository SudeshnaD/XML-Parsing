try:
    # For Python 3.0 and later
    #from urllib.request import *
    import urllib
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import time
#import urllib2
import datetime
#from itertools import ifilter
#from future_builtins import filter
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
#import bibtexparser


#def harvest(arxiv="eess:hep-ex"):
def harvest(arxiv="cs"):
    df = pd.DataFrame(columns=("title", "abstract", "categories", "created", "id", "doi"))
    base_url = "http://export.arxiv.org/oai2?verb=ListRecords&"
    url = (base_url +
           "from=2016-01-01&until=2016-12-30&" +
           "metadataPrefix=arXiv&set=%s"%arxiv)
    
    while True:
        print("fetching", url)
        try:
            #response = urllib2.urlopen(url)
            response = urllib.request.urlopen(url)
            
        #except urllib2.HTTPError as e:
        except urllib.error.HTTPError as e:
          if e.code == 503:
                  to = int(e.hdrs.get("retry-after", 30))
                  print("Got 503. Retrying after {0:d} seconds.".format(to))

                  time.sleep(to)
                  continue

          else:
              raise
            
        xml = response.read()
        print(xml)
        
        root = ET.fromstring(xml)
        
        for record in root.find(OAI+'ListRecords').findall(OAI+"record"):
          arxiv_id = record.find(OAI+'header').find(OAI+'identifier')
          meta = record.find(OAI+'metadata')
          info = meta.find(ARXIV+"arXiv")
          
          if "cs.CL" in info.find(ARXIV+"categories").text and all(x in info.find(ARXIV+"abstract").text for x in ["social","media","sentiment"]):
          #if "cs.CL" in info.find(ARXIV+"categories").text and "sentiment" in info.find(ARXIV+"abstract").text.strip():
            created = info.find(ARXIV+"created").text
            created = datetime.datetime.strptime(created, "%Y-%m-%d")
            categories = info.find(ARXIV+"categories").text

            # if there is more than one DOI use the first one
            # often the second one (if it exists at all) refers
            # to an eratum or similar
            doi = info.find(ARXIV+"doi")
            if doi is not None:
                doi = doi.text.split()[0]

            contents = {'title': info.find(ARXIV+"title").text,
                        'id': info.find(ARXIV+"id").text,#arxiv_id.text[4:],
                        'abstract': info.find(ARXIV+"abstract").text.strip(),
                        'created': created,
                        'categories': categories.split(),
                        'doi': doi,
                        }

            df = df.append(contents, ignore_index=True)

        # The list of articles returned by the API comes in chunks of
        # 1000 articles. The presence of a resumptionToken tells us that
        # there is more to be fetched.
        token = root.find(OAI+'ListRecords').find(OAI+"resumptionToken")
        if token is None or token.text is None:
            break

        else:
            url = base_url + "resumptionToken=%s"%(token.text)
            
    return df

    if __name__=='__main__':
        
        pd.set_option('mode.chained_assignment','warn')

        OAI = "{http://www.openarchives.org/OAI/2.0/}"
        ARXIV = "{http://arxiv.org/OAI/arXiv/}"
        res=harvest()
        res.to_excel('dataset.xlsx')
    #print(res.info())