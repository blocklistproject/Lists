const dns = require('dns');
const fs = require("fs")
const lists = [
	"abuse",
	"ads",
	"crypto",
	"drugs",
	"facebook",
	"fraud",
	"gambling",
	"malware",
	"phishing",
	"piracy",
	"porn",
	"ransomware",
	"redirect",
	"scam",
	"tiktok",
	"torrent",
	"tracking",

	// The following lists are in beta and therefore not included in the everything list:

	// "smart-tv",
	// "basic",
	// "whatsapp"
];
var c = {}
for(var t = 0;t < lists.length;t++){
  fs.readFile(lists[t],function(err,data){
    if(err){return;}
    c.endlist = ''
    var lines = data.split("\n")
    for(var t2 = 0;t2 < lines;t2++){
      if(lines[t2].startsWith("#")){
        c.endlist += lines[t2] + "\n"
        continue
      }
      //check the dns
      dns.resolve(lines[t2].split(" ")[1], "A", (err, records)
         => {
        //if there is an error, ignore the domain
        if(err){return;}
        if(records){
          c.endlist += "127.0.0.1 " + lines[t2].split(" ")[1] +  "\n"
        }
      });
      
      
    }
    
    fs.writeFile(lists[t].split(".")[0] + "_lite.txt", c.endlist,function(err){})
  })
}
