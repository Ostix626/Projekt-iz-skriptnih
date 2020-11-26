import pdfplumber as pp
import re
import sys
import io

PDFpath = "racuni/zelengrad2.pdf"
zelengrad_re = re.compile(r'(\d+)/ 40[\s*\d/]*, (.*?)\s\s [\s]+([\d.]+\,\d{1}) (KOM|MET|KG|M\*2|PAK)[\s]+([\d.]+\,\d+)\s\s')
tablica = False
prvi_red = False

file = open("tab.csv", "a",  encoding = 'utf-8') 
file.truncate(0)

with pp.open(PDFpath) as pdf:
    pages = pdf.pages
    
    for i,pg in enumerate(pages):
        text = pages[i].extract_text()
        
        for row in text.split("\n"):
            if row.startswith("Šifra"):
                tablica = True
                continue;
                
            if row.startswith("/6 POVRAT ROBE:"):
                tablica = False
                break;
                
            if row.startswith("Copyright Aura Soft 2001."):
                tablica = False
                continue;
            
            if tablica and (row.startswith("*/ 40") != 1):
                m = zelengrad_re.search(row)
                file.write(m.group(1) + "@" + m.group(2) + "@" + m.group(3) + "@" + m.group(4) + "@" + m.group(5) + "\n")
                continue;
            
            if row.startswith("ZELENGRAD d.o.o. PAZIN") and prvi_red == False:
                file.write("ZELENGRAD d.o.o.@" + row.split()[-1] + "@") 
            elif (row.find('Datum:') != -1) and prvi_red == False:
                file.write(row.split()[-2] + "\n") 
                prvi_red = True
                
                    
file.close()
         


