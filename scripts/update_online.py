"""this file gets all the domains in each list, and adds the online ones to a file"""
#import the needed modules - os and socket
import socket
import os
#move out of the scripts dir so we can access all the files
#this is just cd ..
os.chdir("..")

#all of the lists
lists = ["porn.txt","abuse.txt","ads.txt","basic.txt","crypto.txt","drugs.txt","everything.txt","facebook.txt","fraud.txt","gambling.txt","malware.txt","phishing.txt","piracy.txt","ransomware.txt","redirect.txt","scam.txt","smart-tv.txt","tiktok.txt","torrent.txt","tracking.txt","whatsapp.txt","youtube.txt"]
#loop thought the lists
for list in lists:
  #read the list
    file = open(list)
    #create the online-domains-only file for that list
    alt = open(list.split(".")[0] + "_lite.txt","w")
    #get all the lines in that file
    lines = file.read().split("\n")
    #look through the lines
    for line in lines:
      #if it is a comment, just write it to the file and continue
        if line.startswith("#"):
            alt.write("{}\n".format(line))
            continue
        try:
        #if it is a domain, split the line in two pieces (127.0.0.1 and the domain) and get the second part (the domain)
             domain = line.split(" ")[1]
        except:
          #if there was something unexpected, prevent the program from crashing
          domain = ""
        try:
          #try to get the domain's ip
            socket.gethostbyname(domain)#we don't need the ip, we just need to know there is an ip that the host resolves to an ip
        except:
          #if the DNS does not resolve, ignore that domain
            pass
        else:
          #if the dns does resolve, add the domain 
          alt.write("127.0.0.1 {}".format(domain)) #re-add the 127.0.0.1, which we removed before testing the domain
    #save changes to the file
    alt.close()