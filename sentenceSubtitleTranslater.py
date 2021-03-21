from os import system, name
from collections import Counter
from pysubparser import parser
from string import digits
from unidecode import unidecode
from csv import reader, writer, DictReader
from difflib import SequenceMatcher

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

# subtitleList=[["","","",""]]
# for subtitle in parser.parse(inputSRTFileName):
#     aL=[str(subtitle.index+1),adjustDate(subtitle.start),adjustDate(subtitle.end),str(subtitle.text)];
#     subtitleList.append(aL);

# saveSubtitleListToCSV(subtitleList,untranslatedCSVFile);
translatedSubtitle=csvToList(translatedCSVFile);
newSubtitle=""
# for ts in len(translatedSubtitle:
#     newSubtitle+=ts[0]+"\n"+\
#         ts[1]+" --> "+ts[2]+"\n"+\
#                 ts[3]+"\n"+\
#                     ts[4]+"\n\n"
for i in range(len(translatedSubtitle)-1):
    newSubtitle+=translatedSubtitle[i][0]+"\n"+\
        translatedSubtitle[i][1]+" --> "+str(translatedSubtitle[i+1][1])[:-3]+"000"+"\n"+\
                translatedSubtitle[i][3]+"\n"+\
                    translatedSubtitle[i][4]+"\n\n"
writeStringToFile(newSubtitle,outputSRTFileName)