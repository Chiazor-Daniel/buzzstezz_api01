from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . forms import Search
import mechanize
import requests
import urllib
import re
import mechanize
from bs4 import BeautifulSoup
from rest_framework.response import Response
from .models import *


br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
from django.http import HttpResponse


#Exceptions error 500 , 503 , Backend Error
@api_view(['POST'])
def search_and_get_links(request):
    searchword = request.data.get('searchword')
    if not searchword:
        return Response({"message": "Error", "data": "Searchword is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # First, search for the movie
        br.open("https://www.fzmovies.net/")
        br.select_form(nr=0)
        br.form['searchname'] = str(searchword)
        br.submit()

        # Get search results
        orders_html = br.response().read()
        soup = BeautifulSoup(orders_html, 'html.parser')
        divs = soup.find_all("div", {"class": "mainbox"})

        if not divs:
            return Response({"message": "Error", "data": "No results found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the first movie link
        first_movie_div = divs[0]
        movie_links = first_movie_div.find_all('a', href=True)
        if not movie_links:
            return Response({"message": "Error", "data": "No movie links found"}, status=status.HTTP_404_NOT_FOUND)

        movie_url = 'https://fzmovies.net/' + movie_links[0]['href']

        # Get download links from the movie page
        br.open(movie_url)
        orders_html = br.response().read()
        soup = BeautifulSoup(orders_html, 'html.parser')

        # Find the moviesfiles section
        moviesfiles_uls = soup.find_all("ul", {"class": "moviesfiles"})
        download_links = []

        # Search for 720p links
        for ul in moviesfiles_uls:
            links = ul.find_all('a', href=True)
            for link in links:
                if '720p' in link.text.lower():
                    download_links.append('https://fzmovies.net/' + link['href'])
                    break
            if download_links:
                break

        if not download_links:
            return Response({"message": "Error", "data": "No download links found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": "Success!",
            "data": {
                "movie_url": movie_url,
                "download_links": download_links
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": "Error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_download_link(request):
    download_url = request.data.get('movie_to_download')
    detail = urllib.parse.unquote(str(download_url))

    # User device tracking logic (unchanged)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    device_type = ""
    browser_type = ""
    browser_version = ""
    os_type = ""
    os_version = ""
    if request.user_agent.is_mobile:
        device_type = "Mobile"
    if request.user_agent.is_tablet:
        device_type = "Tablet"
    if request.user_agent.is_pc:
        device_type = "PC"
    
    browser_type = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_type = request.user_agent.os.family
    os_version = request.user_agent.os.version_string

    user_device, created = UserDevice.objects.get_or_create(
        ip = ip,
        device_type = device_type,
        browser_type = browser_type,
        browser_version = browser_version,
        os_type = os_type,
        os_version = os_version,
    )

    downloaded_movie = Downloaded.objects.create(
        movie_name = download_url,
        user_device = user_device,
    )

    # Updated scraping logic
    try:
        # Open the detail page
        r = br.open(detail)
        orders_html = r.read()
        soup = BeautifulSoup(orders_html, 'html.parser')

        # Find all ul elements with class "moviesfiles"
        moviesfiles_uls = soup.find_all("ul", {"class": "moviesfiles"})

        # Search for the 720p link
        download_link_720p = None
        for ul in moviesfiles_uls:
            links = ul.find_all('a', href=True)
            for link in links:
                if '720p' in link.text:
                    download_link_720p = 'https://fzmovies.net/' + link['href']
                    break
            if download_link_720p:
                break

        if not download_link_720p:
            return Response({"message": "Error", "data": "No 720p download link found"}, status=status.HTTP_404_NOT_FOUND)

        # Open the 720p download page
        r = br.open(download_link_720p)
        orders_html = r.read()
        soup = BeautifulSoup(orders_html, 'html.parser')

        # Find the download link on this page
        download_link = soup.find("a", {"id": "downloadlink"})
        if not download_link:
            return Response({"message": "Error", "data": "Download link not found on the page"}, status=status.HTTP_404_NOT_FOUND)

        # Construct the URL for the final download page
        down_page_2 = 'https://fzmovies.net/' + download_link['href']

        # Open the final download page
        r = br.open(down_page_2)
        orders_html = r.read()
        soup = BeautifulSoup(orders_html, 'html.parser')

        # Find all the final download links
        down_links = soup.find_all("input", {"name": "download1"})
        if not down_links:
            return Response({"message": "Error", "data": "Final download links not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the values of the download links
        real_links = [link['value'] for link in down_links]

        return Response({"message": "Success!", "data": real_links}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": "Error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    download_url = request.data.get('movie_to_download')
    detail = urllib.parse.unquote(str(download_url))

    # new stuff 
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    device_type = ""
    browser_type = ""
    browser_version = ""
    os_type = ""
    os_version = ""
    if request.user_agent.is_mobile:
        device_type = "Mobile"
    if request.user_agent.is_tablet:
        device_type = "Tablet"
    if request.user_agent.is_pc:
        device_type = "PC"
    
    browser_type = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_type = request.user_agent.os.family
    os_version = request.user_agent.os.version_string

    user_device, created = UserDevice.objects.get_or_create(
        ip = ip,
        device_type = device_type,
        browser_type = browser_type,
        browser_version = browser_version,
        os_type = os_type,
        os_version = os_version,
    )


    downloaded_movie = Downloaded.objects.create(
        movie_name = download_url,
        user_device = user_device,
    )

    # new stuff 

    #for opening detail page
    r = br.open(detail)

    #to read and save the page
    orders_html = br.response().read()

    soup = BeautifulSoup(orders_html,'html.parser')

    #filltering ul
    divs = soup.find_all("ul", {"class": "moviesfiles"})

    #initializing an empty array
    li = []

    #  this for loop is for filltering all a tags in the ul tag fillltered before and appending the results to a new array
    for d in divs:
        ul = d.find_all('a', href=True)
        for u in ul:
            li.append(u['href'])

    #initializing a new array
    down_page = []


    #this for loop is to remove the media.php in the link array and form the download page link
    for i in li:
        if 'mediainfo.php' in i:
            del i
        else:
            down_page.append('fzmovies.net/'+str(i))

    #raw url for download page1
    down_conf = down_page[1]
    #action to open url for downoad page 1, with http appended to it
    r = br.open('https://'+down_conf)

    orders_html = br.response().read()

    soup = BeautifulSoup(orders_html,'html.parser')

    divs = soup.find_all("a", {"id": "downloadlink"})

    nexts = []
    for d in divs:
        nexts.append(d['href'])
        maybe = d['href']
        down_page_2 = 'https://fzmovies.net/'+maybe


    ######Entering the last Download page#####

    #opening the page
    r = br.open(down_page_2)

    #reading the page
    orders_html = br.response().read()


    soup = BeautifulSoup(orders_html,'html.parser')

    down_link = soup.find_all("input", {"name": "download1"})
    real_links = []

    #download links generated

    label = ['link 1', 'link 2', 'link 3', 'link 4', 'link 5']

    for i in down_link:
        real_links.append(i['value'])

    data = real_links

    return Response({"message": "Success!", "data": data}, status=status.HTTP_200_OK )