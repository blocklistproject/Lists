const dns = require("dns")
const fs = require("fs")
const path = require("path")

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

console.log("Running...")

fs.writeFile("reports/offline.txt","",function(err){
	if(err){console.log("Error:",err)}
for(var t = 0;t < lists.length;t++){
  fs.readFile(path.join(__dirname, "..") + "/" +  lists[t] + ".txt",function(err,data){
    if(err){
	    console.log(err)
	    return;
    }
	  var lines = data.split("\n")
	  for(var lineid = 0; lineid < lines.length;lineid++){
		  if(lines[lineid].startsWith('#') || lines[lineid] === ''){
			  continue
		  }
		  var domain = lines[lineid].split(" ")[1]
		  
			  console.log(domain)
		  dns.resolve(domain, "A", function(err, records){
			  if(err){
				  console.log(err,domain," dead")
				  fs.appendFile("reports/offline.txt",domain + "\n",function(err){
					  console.log("Error:",err)
				  })
			  }
			  else{
				  
			  }
		  });
	  }
  })
}
})
