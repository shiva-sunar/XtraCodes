from os import system, name
from collections import Counter
from pysubparser import parser
from string import digits
from unidecode import unidecode
from csv import reader, writer, DictReader
from difflib import SequenceMatcher
# Some manual works need to be done to translate the SRT.
#IT cant be used off the shelf... few coding/modification is required
#This was made just for me so... :)
#How it works???
#(Foreign SRT file) ---> (CSV File with Foreign/Untranslated Subtile)
#(CSV File with Foreign/Untranslated Subtile)--> upload it to google sheet --> 
# Add new Column in the googlesheet --> Insert formula =GOOGLETRANSLATE(D2;"fr";"en") which will translate the subtitle
#Download the file as translated.csv
#Run the code...

inputSRTFileName = r"C:\Downloads\Amélie (2001) [BluRay] [1080p] [YTS.AM]\Amelie.srt"
outputSRTFileName = r"C:\Downloads\Amélie (2001) [BluRay] [1080p] [YTS.AM]\TranslatedAmelie.srt"
untranslatedCSVFile = r"C:\Users\Shiva\Desktop\unTranslated.csv"
translatedCSVFile = r"C:\Users\Shiva\Desktop\translated.csv"

def adjustDate(stringDate):
    return str(stringDate).replace("000", "").replace('.', ',')

def saveSubtitleListToCSV(aSubtitleList,aCSVFile):
    with open(aCSVFile, 'w', newline='') as f:
        write = writer(f)
        write.writerows(aSubtitleList)

def csvToList(aCSVFile):
    with open(aCSVFile, 'r') as fp:
        return list(reader(fp))

def writeStringToFile(stringToWrite, fileToWrite):#
        text_file = open(fileToWrite, "w")
        text_file.write(stringToWrite)
        text_file.close()

#This commented section is to create a CSV file from SRT File
#use google spreadsheet to translate the CSV with formula =GOOGLETRANSLATE(D2;"fr";"en")
# subtitleList=[["","","",""]]
# for subtitle in parser.parse(inputSRTFileName):
#     aL=[str(subtitle.index+1),adjustDate(subtitle.start),adjustDate(subtitle.end),str(subtitle.text)];
#     subtitleList.append(aL);

# saveSubtitleListToCSV(subtitleList,untranslatedCSVFile);

#This Section is to Create a SRT File from a Translated CSV file. 
#use google spreadsheet to translate the CSV with formula =GOOGLETRANSLATE(D2;"fr";"en")
translatedSubtitle=csvToList(translatedCSVFile);
newSubtitle=""
for i in range(len(translatedSubtitle)-1):
    newSubtitle+=translatedSubtitle[i][0]+"\n"+\
        translatedSubtitle[i][1]+" --> "+str(translatedSubtitle[i+1][1])[:-3]+"000"+"\n"+\
                translatedSubtitle[i][3]+"\n"+\
                    translatedSubtitle[i][4]+"\n\n"
writeStringToFile(newSubtitle,outputSRTFileName)
