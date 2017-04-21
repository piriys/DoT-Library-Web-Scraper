from lxml import html
import os
import requests
import urllib
import re

#TO DO: Add/implement Selenium to grab library page with all expanded dynatree nodes instead of running js and save html manually

#Set download path
downloadPath = 'D:/DOTWebScraper/AdvisoryCirculars'
if not os.path.exists(downloadPath):
	os.makedirs(downloadPath)
folderTitleXPath = './/span[contains(@class, "dynatree-folder")]/span[contains(@class, "dynatree-title")]'
fileCount = 0;

#Open saved dynatree page with all nodes expanded 
with open(r'DoT_AC.html', 'r') as file:
	indexPage = file.read()
indexTree = html.fromstring(indexPage)
folders = indexTree.xpath('.//ul[contains(@class, "dynatree-container")]/li')
folderTitles = indexTree.xpath(folderTitleXPath + '/text()')

#Loop through folders
for fldt in folderTitles:		
	fullPath = downloadPath + '/' + fldt
	if not os.path.exists(fullPath):
		os.makedirs(fullPath)	
	currentFolderPath = folderTitleXPath + '[contains(text(), "' + fldt + '")]/./../following-sibling::ul[1]/li'
	fileTitles = indexTree.xpath(currentFolderPath + '/span/span[contains(@class, "dynatree-title")]/a/span[contains(@class, "toc-col-1")]/text()')
	fileDates = indexTree.xpath(currentFolderPath + '/span/span[contains(@class, "dynatree-title")]/a/span[contains(@class, "toc-col-2")]/text()')	
	filePageUrls = indexTree.xpath(currentFolderPath + '/span/span[contains(@class, "dynatree-title")]/a/@href')
	print 'FOLDER: ' + fldt
	
	#Loop through each file in folder
	for i, flt in enumerate(fileTitles):
		title = flt
		date = fileDates[i]
		url = filePageUrls[i]
		
		#Convert unsafe character in in title into safe filename
		filename = '[' + date + '] ' + title
		filename = filename.replace('/', '-').replace(':', '').replace('.', '_')	
		keepcharacters = (' ','','_', '-', '[', ']')
		safeFilename = "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip() + '.pdf'
		print 'FILENAME: ' + safeFilename
		print 'DOCUMENT PAGE URL: ' + url
		
		#Connect to document url
		print 'Connecting to URL...'
		docsPage = requests.get(url)
		docsRawHtml = docsPage.content
		
		#Download URL Pattern: 
		#http://specialcollection.dotlibrary.dot.gov/file?db=DOT-ADVISORY&filename=r%3A%2Fdot%2Facs%2Fwebsearch%2F  <FILE ID>  .pdf
		#Get file ID from script in header
		try:
			docsFileId = docsRawHtml.split('file_attachments: ["r:/dot/acs/websearch/', 1)[1].split('.pdf"],', 1)[0]
			docsFileUrl = 'http://specialcollection.dotlibrary.dot.gov/file?db=DOT-ADVISORY&filename=r%3A%2Fdot%2Facs%2Fwebsearch%2F' + docsFileId + '.pdf'
			print docsFileUrl
			fullFilename = os.path.join(fullPath, safeFilename)		
			urllib.urlretrieve(docsFileUrl, fullFilename)	
			print('Download completed.')	
		except IndexError: 
			print('No file available.')			
		print '#############################################'
		fileCount = fileCount + 1	
print fileCount
raw_input('Press enter to continue...')