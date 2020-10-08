import glob, os

# Set cwd to file location
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Get every .txt file in folder (except output file)
txt_files = [f for f in glob.glob("*.txt")]
txt_files.remove("everything.txt")

# For non-duplicates lines + count + write
read_lines = set()

# Info text to go on top, formattable at "Total number of network filters"
info_text = "\n#------------------------------------[UPDATE]--------------------------------------\n# Title: The Block List Project\n# Expires: 1 day\n# Homepage: https://blocklist.site\n# Help: https://github.com/blocklistproject/lists/wiki/\n# License: https://unlicense.org\n# Total number of network filters: {}\n#------------------------------------[SUPPORT]-------------------------------------\n# You can support by:\n# - reporting false positives\n# - making a donation: https://paypal.me/blocklistproject\n#-------------------------------------[INFO]---------------------------------------\n#\n# Summed list\n#------------------------------------[FILTERS]-------------------------------------\n"

# Read all .txt-files and save non-duplicate lines
for input_file in txt_files:
    for line in open(input_file, "r"):
        read_lines.add(line)

# Count, format and sum text
no_of_lines = len(read_lines)
info_text = info_text.format(no_of_lines - 16)
summed_lines = "".join(read_lines)

with open("everything.txt", "w") as output_file:
    output_file.write(info_text)
    output_file.write(summed_lines)