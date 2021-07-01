const dns = require("dns")
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

for(var t = 0;t < lists.length;t++){
  fs.readFile("../" + lists[t],function(err,data){
    console.log(data)
  })
}
