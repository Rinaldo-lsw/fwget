#!/usr/bin/python3

# Copyright 2024 Hewlett Packard Enterprise Development LP
#
# This program is free software; you can redistribute it and/or modify it 
# under the terms of version 2 of the GNU General Public License as published 
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
#
# You should have received a copy of the GNU General Public License along with 
# this program; if not, write to:
#
#  Free Software Foundation, Inc.
#  51 Franklin Street, Fifth Floor
#  Boston, MA 02110-1301, USA.


import json
import sys
import os.path
try:
    import requests
except ImportError:
    sys.exit("""
Fwget requries the 'requests' Python module.
Please install it with the appropriate command as root:

                RedHat:    yum     install python3-requests
                SUSE  :    zypper  install python3-requests
                Ubuntu:    apt-get install python3-requests
                others:    pip     install requests
                                         """)

##########
# search   substring search in filename and description, secretly sort output by date
def search(searchstring, json_index):
   output_list = []
   for fw in json_index:
       if searchstring.lower() in fw.lower():
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"], json_index[fw]["target"], json_index[fw]["deviceclass"] ) )
       elif searchstring.lower() in json_index[fw]["description"].lower():
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"], json_index[fw]["target"], json_index[fw]["deviceclass"] ) )
       elif searchstring.lower() in json_index[fw]["target"]:
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"], json_index[fw]["target"], json_index[fw]["deviceclass"] ) )
       elif searchstring.lower() in json_index[fw]["deviceclass"].lower():
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"], json_index[fw]["target"], json_index[fw]["deviceclass"] ) )
   output_list_sorted_by_date = sorted(output_list, key=lambda tup: tup[0], reverse=True) 
   for tuple in output_list_sorted_by_date:
       print (str(tuple[1]).ljust(66) + "   " + tuple[2].encode('ascii','ignore').decode() ) # unicode, works in python2&3
   return(0)


##########
# locate   substring search in filename and description, output urls secretly sorted by date
def locate(searchstring, json_index, content_url):
   output_list = []
   for fw in json_index:
       if searchstring.lower() in fw.lower():
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"]) )
       elif searchstring.lower() in json_index[fw]["description"].lower():
           output_list.append(  (json_index[fw]["date"], fw, json_index[fw]["description"]) )
   output_list_sorted_by_date = sorted(output_list, key=lambda tup: tup[0], reverse=True) 
   for tuple in output_list_sorted_by_date:
       print (content_url + "/" + tuple[1])
   return(0)


##########
# download download file supplied on command name, no wildcards
def download(file, content_url):
  url = content_url + "/" + file
  print("./" + file)
  try:
      html_request = requests.get(url) 
      if html_request.status_code != 200:
         raise Exception(html_request.status_code)
      else:
          with open(file, 'wb') as firmware_file:
               firmware_file.write(html_request.content)
  except Exception as error:
      if str(error) == '404':
         print("Unable to download firmware (404 not found):")
         print("   " + url) 
         quit(1)
      elif str(error) == '401':
         print("Unable to download firmware (401 not authorized).")
         print("")
         print("A valid warranty or support contract is required to access HPE firmware.")
         print("Please visit http://downloads.linux.hpe.com/SDR/project/fwpp/ to ")
         print("generate an access token then add it to ~/.fwget.conf .")
         quit(1)
      else:
         print("Unable to download.")
         print(str(error))
         quit(1)

  return(0)


##########
# list     everything, sorted by filename
def list(json_index):
   output_list = []
   for fw in json_index:
       #print (fw.ljust(33) + " " +  json_index[fw]["description"])
       output_list.append( (fw, json_index[fw]["description"]) )
   output_list_sorted_by_filename = sorted(output_list, key=lambda tup: tup[0], reverse=True) 
   for tuple in output_list_sorted_by_filename:
       #print (tuple[0].encode('ascii','ignore').ljust(33).decode() + "   " + tuple[1].encode('ascii','ignore').decode() ) # unicode, works in python2&3
       print (str(tuple[0]).ljust(33) + "   " + tuple[1].encode('ascii','ignore').decode() ) # unicode, works in python2&3
   return(0)


###########
# parse     command line, setup config file if it doens't exist, prompt for token
def parse_config():
   config_file = os.path.expanduser("~") + "/.fwget.conf"
   if os.path.isfile(config_file):
      try:
         with open(config_file, 'r') as json_config_file:
             json_config = json.load(json_config_file)
             token = json_config["token"]
             url   = json_config["url"]  
      except:
         print("Unable to open/parse " + config_file)
         quit(1)
   else: 
         with open(config_file, "w+") as config_file_handle:
            config_file_handle.write('{ \n')
            config_file_handle.write('"_comment": "For Gen9 and earlier, generate token at: http://downloads.linux.hpe.com/SDR/project/fwpp/fwget.html",  \n')
            config_file_handle.write('"_comment": "Replace fwpp-gen11 with fwpp-gen10/fwpp-gen9/fwpp-gen8 as appropriate.",  \n\n')
            config_file_handle.write('   "token": "na",  \n')
            config_file_handle.write('   "url"  : "https://downloads.linux.hpe.com/SDR/repo/fwpp-gen11/current"  \n\n')
            config_file_handle.write('} \n')
            config_file_handle.close()
            print("Using default fwpp-gen11 firmware repository.  Please edit ~/.fwget.conf to change if needed.")
            url = "https://downloads.linux.hpe.com/SDR/repo/fwpp-gen11/current"
            token = "null"
  
   return(token, url)

 

if __name__ == "__main__":

  argcount = len(sys.argv)
  arglist  = sys.argv

  token, url = parse_config()

  baseurl = url.replace('https://', '')  
  baseurl = baseurl.replace('http://', '')  

  index_url   = "https://" + token + ":null@" + baseurl + "/fwrepodata/fwrepo.json"
  content_url = "https://" + token + ":null@" + baseurl 

  try:
      index = requests.get(index_url)
      if index.status_code != 200:
         raise Exception(index.status_code)
      else:
         json_index_filename = os.path.expanduser("~") + "/.fwget.json"
         with open(json_index_filename, 'w') as json_index_file:
               json_index_file.write(index.text)
  except Exception as error:
      if str(error) == '404':
         print("Unable to download firmware index (404 not found):")
         print("   " + index_url) 
         quit(1)
      elif str(error) == '401':
         print("Unable to download firmware index (401 not authorized).")
         print("")
         print("Token:  " + token)
         print("")
         print("A valid warranty or support contract is required to access HPE firmware.")
         print("Please visit http://downloads.linux.hpe.com/SDR/project/fwpp-postprod to ")
         print("generate an access token then add it to ~/.fwget.conf.")
         quit(1)
      else:
         print("Unable to download")
         print("   " + index_url) 
         print("   to ~/fwrepo.json")
         print(str(error))
         quit(1)

  try:
      with open(json_index_filename, 'r') as json_index_file:
          json_index = json.load(json_index_file)
  except:
      print("Unable to open cached copy of index ~/fwrepo.json")
      quit(1)



  if argcount <= 1:
      print("Usage:  fwget.py  < search | locate | download >   [ search term ]\n")

  elif "search" in arglist[1].lower():
      if argcount == 3:
          search(arglist[2], json_index)
      else:
         print("Usage:  fwget.py search [ search term ]")

  elif "locate" in arglist[1].lower():
      locate(arglist[2], json_index, content_url)

  elif "download" in arglist[1].lower():
      download(arglist[2], content_url)
  
  elif "list" in arglist[1].lower():
      list(json_index)

  else:
      print("Usage:  fwget.py  < search | locate | download | list >   [ search term ]")


