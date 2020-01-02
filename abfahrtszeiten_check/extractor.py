import io
import re
 
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import urllib.request

 
def controller():
    # seem to be the most important lines
    lines = [1,5,8,10,11,12,13];
    fahrplan_array = dict()

    # lets get the fresh files for fresh data
    for ln in lines:
        download_files("https://www.h3nv.de/fileadmin/pdf/fahrplan/"+str(ln)+".pdf", "./lines/"+str(ln)+".pdf")

        # look into each file
        text_data = extract_text_from_pdf("./lines/"+str(1)+".pdf")

        regex = r"(\D+)(\d+)"

        matches = re.finditer(regex, text_data, re.MULTILINE)

        ln_key = "Line " + str(ln)
        fahrplan_array[ln_key] = dict()

        for matchNum, match in enumerate(matches, start=1): 

            key = ''.join(e for e in match.group(1) if e.isalnum())

            if(check_if_ok(key)):
                line = match.group(2)
                fahrplan_array[ln_key][key] = []
                n = 2
                
                fahrplan_array[ln_key][key] = [line[i:i+n] for i in range(0, len(line), n)]

    # result of all minutes of each station per line are structured in a dict for further usage
    print(fahrplan_array)

    # todo:
    # check with provided data to see if pdf are accurate


# 
# HELPERS
# 
def download_files(url, file_name):
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)

def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
 
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
 
        text = fake_file_handle.getvalue()
 
    # close open handles
    converter.close()
    fake_file_handle.close()
 
    if text:
        return text

def check_if_ok(key):
    # too long texts are untrue, too small as well
    if(len(key) > 50 or len(key) < 5):
        return False;

    # remove useless entry that slipped through
    Word_db = ["Gültigab","StadtwerkeHeilbronnVerkehrsbetriebeTel", "VERKEHRSHINWEIS", "Sonntagim", "hältnurzumAus", "nurbeiBedarf"]
    for word in Word_db:
        if key.find(word) != -1:
            return False

    #should be good enough candidate
    return True
 
if __name__ == '__main__':
    controller()
