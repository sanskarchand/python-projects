#!/usr/bin/env python

import bs4, sys
import subprocess
import os

# Downloads from mangakakalot.com | sanskarchand
# use sparingly; conserver bandwidth 
# this is a throw-away script
# Dependencies: beautifulsoup4
# usage: ./script [manganame] [foldername]
# the manganame is the name appearing in the url(e.g. boku_wa_ne)
# sample usaeg: ./mangaklot_dl.py 

DEBUG = False
phrases =  ['blogspot', 'mpcdn', 'mkklcdn']

mname = sys.argv[1]

def main():
    base_url = "mangakakalot.com/manga/"
    foldername = sys.argv[2]

    try:
        os.mkdir(foldername)
    except:
        pass

    os.chdir(foldername)
    # current directory is now the new folder

    #Download main page
    subprocess.call(['wget', '-O', mname + ".html", base_url + mname])
    with open(mname + ".html", "r") as f:
        dat = f.read()

    soup = bs4.BeautifulSoup(dat, "html.parser")
    chap_li = list()
    divTag = soup.findAll('div', {'class': 'chapter-list'})[0] #only one

    links = divTag.findAll('a')
    for link in links:
        chap_li.append(link)

    chap_li.reverse()

    print("Select chapter range(inclusive):")
    for i, each in enumerate(chap_li):
        #print ("{} :-> {}".format(i, each["title"]))
        ostrl = [i, ":->", each["title"]]
        print(ostrl)
    start = input(">> Start: ")
    stop = input(">> Stop: ")

    for i in range(start, stop+1):
        ch = chap_li[i]
        downloadChapter(ch)

def downloadChapter(chapter_tag):

    chapter_name = chapter_tag.get_text()
    chapter_name = chapter_name.replace("/", "*SL*")
    chapter_name = chapter_name.replace(":", "_colon_")

    try:
        os.mkdir(chapter_name)
    except:
        pass


    os.chdir(chapter_name)

    subprocess.call(["wget", chapter_tag["href"], "-O", "file.html"])

    with open("file.html", "r") as f:
        page = f.read()

    soup = bs4.BeautifulSoup(page, "html.parser")

    tags = soup.findAll('img')

    i = 0
    for tag in tags:
        if DEBUG:
            print (tag['src'])

        #IDENTIY a link pointing to a manga image
        if any([x in tag['src'] for x in phrases]):
            if mname in tag['src']:
                subprocess.call(["wget", "-O", str(i) + ".jpg", tag['src']])
                i += 1

    os.chdir("..")

if __name__ == '__main__':
    main()
