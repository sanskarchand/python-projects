#!/usr/bin/env python

import requests, sys, os
import bs4
import re

ERR_STRING = "CHAPTER_ERROR"

#values
CHAP_FORM = 3
VOL_CHAP_FORM = 4

FORMAT = 0
DEBUG = True

VOL_WEIGHT = 1000
INF = 88888888

#pattern: /c, followed by digits or periods or digits
chap_pat = re.compile("/c\d*.*\d*/")
#pattern: /v, followed by digits
vol_pat = re.compile("/v\d*/")

manga_name = sys.argv[1]
manga_foldername = sys.argv[2]

mp_url_base = "https://www.mangahere.co/manga/"

mp_url = mp_url_base + manga_name
mp_fname = manga_name + ".html"


def setChapterFormat(chap_string):
    """
    If the link has the pattern /vxxx/, we assume that the manga
    is split into volumes. If so, we need to add the volume name to 
    the folder.
    This sets FORMAT according to the format of the string.
    NOTE: It is not necessary to check this every chapter
    """
    global FORMAT
    vol_check = vol_pat.search(chap_string)

    if vol_check is None:
        FORMAT = CHAP_FORM
    else:
        FORMAT = VOL_CHAP_FORM

def extractChapterCode(chap_string):
    try:
        x = chap_pat.search(chap_string)
        st = x.group()
        if (DEBUG): print("CODE: ", st[1:-1])
        return st[1:-1] # return excluding bounding /'s
    except:
        return ERR_STRING

def extractVolumeCode(chap_string):
    try:
        x = vol_pat.search(chap_string)
        st = x.group()
        return st[1:-1] # reuturn v[num]
    except:
        return ERR_STRING

def downloadSingleChapter(c_link):
    
    # phase one : check format and make dir
    setChapterFormat(c_link)

    if DEBUG:
        print("FORMAT: ", FORMAT)

    chap_code = extractChapterCode(c_link)
    vol_code = ''

    if (FORMAT == VOL_CHAP_FORM):
        vol_code = extractVolumeCode(c_link) + '_'

    foldername = vol_code + chap_code
    
    if (foldername == ERR_STRING):
        return

    full_p = os.path.join(manga_foldername, foldername)

    try:
        os.mkdir(full_p)
    except:
        pass

    #phase 2: download pages
    #increment page number until you get 404
    pnum = 1

    while True:
        
        #p_link = "https:" + c_link + str(pnum) + ".html"
        p_link = c_link + str(pnum) + ".html"
        r = requests.get(p_link, verify=False)
        
        if DEBUG:
            print("RINKO : {}".format(p_link))

        # exit when pages are exhausted
        '''
        if r.status_code != 200:
            print("Chapter completed.")
            break
        '''
        if 'error_404' in r.text:
            print('Chapter completed.')
            break



        # write page's html file
        html_path = os.path.join(full_p, str(pnum) + ".html")
        with open(html_path, 'wb') as f:
            f.write(r.content)

        f = open(html_path, 'r')
        soup = bs4.BeautifulSoup(f.read())
        f.close()

        # get image
        img_link  = ''
        for img in soup.find_all('img'):
            #if img.has_attr('onload') and img['onload'] == ['loadImg(this)']:
            if img.has_attr('onload'):
                img_link = img['src']
                if DEBUG:
                    print("IMAGE: {}".format(img_link))

        # download the image
        ir = requests.get(img_link, verify=False)
        assert ir.status_code == 200

        #NOTE: have assumed jpeg
        img_path = os.path.join(full_p, str(pnum) + ".jpg")
        with open(img_path, 'wb') as f:
            f.write(ir.content)

        # remove html
        os.remove(html_path)

        pnum += 1


def downloadChapters(chap_li, suru, khatam):
    
    for ind in range(suru, khatam+1):
        
        chapter_link = chap_li[ind]
        print("Downloading chapter {}".format(ind))
        downloadSingleChapter(chapter_link)

def sortChapKey(chap):
    """
    Given a string for a chapter URL, it returns the numeric value of
    the chapter num c***
    """
    #NOTE: Maybe add regexp to handle manga with >1000 chaps
    ccode = extractChapterCode(chap)

    if ccode is not ERR_STRING:
        return float(ccode[1:])
    else:
        return INF

def sortVolChapKey(chap):
    """
    number from vol
    """

    volcode = extractVolumeCode(chap)
    ccode = extractChapterCode(chap)
    if volcode is not ERR_STRING and ccode is not ERR_STRING:
        return VOL_WEIGHT * float(volcode[1:]) + float(ccode[1:])
    else:
        return INF

def main():
    
    global FORMAT

    # make dir
    try:
        os.mkdir(manga_foldername)
    except:
        pass

    # Download main page
    print("MP-URL: ", mp_url)
    
    #head = {'Accept-Encoding':'deflate', 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    head = {'Accept-Encoding':'deflate'}
    r = requests.get(mp_url, verify=False, headers=head)
    assert r.status_code == 200

    with open(mp_fname, 'wb') as f:
        f.write(r.content)

    # Read page and create bs4 object
    f = open(mp_fname, 'r')
    soup = bs4.BeautifulSoup(f.read(), "html.parser")
    f.close()

    # obtain list of chapter urls
    chap_li = []
    for a in soup.find_all('a'):
        if a.has_attr('href') and manga_name in a['href']:
            # filter out comments and main page
            if 'comments' not in a['href'] and 'm.mangahere' not in a['href']:

                li = a['href']
                #chap_li.append(a['href'])
                #add schema if needed
                if 'http' not in li:
                    li = 'https:' + a['href']

                chap_li.append(li)


    # set format acc to tha of the first chap
    setChapterFormat(chap_li[0])

    # sort by chapter
    if FORMAT ==  VOL_CHAP_FORM: # FORMAT OF LAST
        chap_li.sort(key=sortVolChapKey) # Sorts by chapter number
    else:
        chap_li.sort(key=sortChapKey)

    print('Chapter list: ')
    for idx, each in enumerate(chap_li):
        print("#{}: {}".format(idx, each))

    print('Total number of chapters: {}'.format(len(chap_li)))

    dl_start = int(input(">>Enter DL start list index: "))
    dl_stop = int(input(">>Enter DL stop list index: "))

    downloadChapters(chap_li, dl_start, dl_stop)

if __name__ == '__main__':
    main()
