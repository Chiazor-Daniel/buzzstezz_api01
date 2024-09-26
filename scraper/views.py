from django.shortcuts import render
from django.http import HttpResponseRedirect
from . forms import Search
import mechanize
import requests
import urllib
import re
import mechanize
from bs4 import BeautifulSoup





'''
sessions for history
scraping of the next and previous buttons

'''


br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
from django.http import HttpResponse


#Exceptions error 500 , 503 , Backend Error

def home (request):
    all_texts = ''
    perf_links = ''
    session_texts =''
    image = ''
    image_var_list = ''
    pagination_links =''
    pagination_texts =''

    if request.method == "POST":
        searchword = request.POST.get('searchword')
        br.open("https://www.fzmovies.net/")
        #initialize form i think
        br.select_form(nr=0)
        #this picks the forms search valur and fills it in Fzmovies search form
        br.form['searchname'] = str(searchword)

        #submitting form
        br.submit()

        # saves page source
        orders_html = br.response().read()

        #initializing bs4 for scraping
        soup = BeautifulSoup(orders_html,'html.parser')


        #picking the closest div to the link we want to pick by class name
        divs = soup.find_all("div", {"class": "mainbox"})


        

        #this empty array would be used to store all thhe texts in that mainbox div
        all_texts = []

        #this empty array would be used to store all the a tags in the mainbox div
        links = []

        image_var_list = []
        image = []

        #iterating through all available divs produces by the search
        for div in divs:

            #reavealing the href property in other get links
            a_tags = div.find_all('a', href=True)

            picstp_1 = div.find_all('img')

            #  = image_var_list.append()

            #this for loop appends all the links in mainbox div into the links array
            for row in a_tags:
                links.append(row['href'])
            #this for loop appends all the texts in mainbox div into the all_texts array
            for texts in divs:
                all_texts.append(texts.find_all(text=True))

            for pics in picstp_1:
                image_var_list.append('https://fzmovies.net'+pics['src'])

        '''
        there would be two of each link in the links array so this eliminates all double links in the list
        '''
        all_links = list(dict.fromkeys(links))

        '''
        there would be some unwanted strings in the links array called movie tags
        so we initialized an empty array to delete them and save the main links to a perfect array called perf_array
        '''

        new = []


        #this deletes the empty strings and any movie tag link in the list of links and appends the remaining to a new array
        for i in all_links:
            if i=='' or 'movietags' in i:
                del i
            else:
                new.append(i)
        
        perf_links = []
        for i in new:
            perf_links.append('https://fzmovies.net/'+i.replace(" ","%20"))


        mainbox2 = soup.find_all("div", {"class": "mainbox2"})
        
        print(perf_links)
        
        if len(mainbox2) == 4:
            wanted_mainbox2 = mainbox2[3]

            pagination_links = []
            pagination_texts = []
            for pag in wanted_mainbox2.find_all('a', href=True):
                pagination_links.append(pag['href'])
                
                pagination_texts.append(pag.text)

            pagination_links = list(dict.fromkeys(pagination_links))
            
            print (pagination_links)
            print (pagination_texts)               

        searchword = Search()

    else:

        searchword = Search()
         
        #the zip function is used to loop over each list and make thier values appear right ontop of each other and data would be used as a key in the template
    return render(request, 'index.html', {'data':zip(all_texts, perf_links, image_var_list), 'pagination':zip(pagination_links, pagination_texts),  'searchword':searchword})





def generate_download_link(request):
    # Assume br (browser) is already initialized
    download_url = request.POST.get('movie_to_download')
    detail = urllib.parse.unquote(str(download_url))
    
    # Open the detail page
    r = br.open(detail)
    
    # Read and parse the page
    orders_html = r.read()
    soup = BeautifulSoup(orders_html, 'html.parser')
    
    # Find all ul elements with class "moviesfiles"
    moviesfiles_uls = soup.find_all("ul", {"class": "moviesfiles"})
    
    # Initialize an empty list for the 720p link
    download_link_720p = []
    
    # Search for the 720p link
    for ul in moviesfiles_uls:
        links = ul.find_all('a', href=True)
        for link in links:
            if '720p' in link.text:
                full_url = 'https://fzmovies.net/' + link['href']
                download_link_720p.append(full_url)
                break  # Found the 720p link, stop searching
        if download_link_720p:
            break  # Exit the outer loop if we found the link
    
    if not download_link_720p:
        return render(request, 'error.html', {'message': 'No 720p download link found'})
    
    # Open the 720p download page
    r = br.open(download_link_720p[0])
    orders_html = r.read()
    soup = BeautifulSoup(orders_html, 'html.parser')
    
    # Find the download link on this page
    download_link = soup.find("a", {"id": "downloadlink"})
    if not download_link:
        return render(request, 'error.html', {'message': 'Download link not found on the page'})
    
    # Construct the URL for the final download page
    down_page_2 = 'https://fzmovies.net/' + download_link['href']
    
    # Open the final download page
    r = br.open(down_page_2)
    orders_html = r.read()
    soup = BeautifulSoup(orders_html, 'html.parser')
    
    # Find the final download link
    down_link = soup.find("input", {"name": "download1"})
    if not down_link:
        return render(request, 'error.html', {'message': 'Final download link not found'})
    
    # Get the value of the download link
    final_link = down_link['value']
    
    # Return the final download link
    return render(request, 'generated.html', {'data': [final_link]})






def next_or_previous(request):
    download_url = request.POST.get('pagination')
    detail = urllib.parse.unquote(str(download_url))

    #for opening detail page
    r = br.open(detail)

    #to read and save the page
    orders_html = br.response().read()

    soup = BeautifulSoup(orders_html,'html.parser')

    #picking the closest div to the link we want to pick by class name
    divs = soup.find_all("div", {"class": "mainbox"})


    

    #this empty array would be used to store all thhe texts in that mainbox div
    all_texts = []

    #this empty array would be used to store all the a tags in the mainbox div
    links = []

    image_var_list = []
    image = []

    #iterating through all available divs produces by the search
    for div in divs:

        #reavealing the href property in other get links
        a_tags = div.find_all('a', href=True)

        picstp_1 = div.find_all('img')

        #  = image_var_list.append()

        #this for loop appends all the links in mainbox div into the links array
        for row in a_tags:
            links.append(row['href'])
        #this for loop appends all the texts in mainbox div into the all_texts array
        for texts in divs:
            all_texts.append(texts.find_all(text=True))

        for pics in picstp_1:
            image_var_list.append('https://fzmovies.net'+pics['src'])

    '''
    there would be two of each link in the links array so this eliminates all double links in the list
    '''
    all_links = list(dict.fromkeys(links))

    '''
    there would be some unwanted strings in the links array called movie tags
    so we initialized an empty array to delete them and save the main links to a perfect array called perf_array
    '''

    new = []


    #this deletes the empty strings and any movie tag link in the list of links and appends the remaining to a new array
    for i in all_links:
        if i=='' or 'movietags' in i:
            del i
        else:
            new.append(i)
    
    perf_links = []
    for i in new:
        perf_links.append('https://fzmovies.net/'+i.replace(" ","%20"))
        


    mainbox2 = soup.find_all("div", {"class": "mainbox2"})
    
    
    if len(mainbox2) == 4:
        wanted_mainbox2 = mainbox2[3]

        pagination_links = []
        pagination_texts = []
        for pag in wanted_mainbox2.find_all('a', href=True):
            pagination_links.append(pag['href'])
            
            pagination_texts.append(pag.text)

        pagination_links = list(dict.fromkeys(pagination_links)) 
        print(pagination_links)
        print(pagination_texts)              


    
         
        #the zip function is used to loop over each list and make thier values appear right ontop of each other and data would be used as a key in the template
    return render(request, 'paginated_page.html', {'data':zip(all_texts, perf_links, image_var_list), 'pagination':zip(pagination_links, pagination_texts)})



def about(request):
    return render(request,'about.html')    