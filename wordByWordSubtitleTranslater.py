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
wordLength=4

def writeListToCSV(aList, aFile):
    with open(aFile, 'w', newline='') as f:
        write = writer(f)
        write.writerows(aList)


def readFromCSVToDictList(aFile):
    with open(aFile, 'r') as fp:
        return list(DictReader(fp))

def cleanString(string):
    string = string\
        .replace('\'', ' ')\
        .replace('>', ' ')\
        .replace('-', ' ')\
        .replace('<', ' ')\
        .replace('"', ' ')\
        .replace('.', ' ')\
        .replace('!', ' ')\
        .replace('?', ' ')\
        .replace(',', ' ')
    string = " ".join(string.split())
    remove_digits = str.maketrans('', '', digits)
    string = string.translate(remove_digits)
    string = string.lower()
    return string

def createCSVFromSRT(aSRTFile, outputCSVFile):
    def stringToWordlist(string):
        def unAccent(string):
            return unidecode(string)
        words = string.split()
        newWords = []
        for word in words:
            if(len(word) >= wordLength):
                newWords.append(word)
        return [(wL[0], unAccent(wL[0])) for wL in Counter(newWords).most_common()]
    
    def getSubtitleString(aSubtitleFile):
        subtitles = parser.parse(aSubtitleFile)
        onlySub = ""
        for subtitle in subtitles:
            onlySub = onlySub + str(subtitle.text)
        return onlySub
    wordList = stringToWordlist(cleanString(getSubtitleString(aSRTFile)))
    writeListToCSV(wordList, outputCSVFile)


def translateWholeSubtitle():
    translatedDictionary = readFromCSVToDictList(translatedCSVFile) 
    def convertOneSubtitleLine(subtitle):#
        def adjustDate(stringDate):
            return str(stringDate).replace("000", "").replace('.', ',')

        def convertSubtitleText(subtitleText):
            def areWordsSimilar(a,b):
                return SequenceMatcher(None, a, b).ratio()>0.8
            newSubtitleText = subtitleText
            for text in cleanString(subtitleText).split():
                if len(text)>=wordLength:
                    for word in translatedDictionary:
                        if(unidecode(word["French"]).lower() == unidecode(text).lower()):#if the words are same
                            if(not areWordsSimilar(word["French"],word["English"])):
                                newText=text+"->"+word["English"].upper()
                                newSubtitleText=newSubtitleText.replace(text,newText)
                                break                
            return newSubtitleText
        converted = ""
        converted += str(subtitle.index+1)+"\n"
        converted += adjustDate(subtitle.start)+" --> " + \
            adjustDate(subtitle.end)+"\n"
        converted += convertSubtitleText(subtitle.text)+"\n\n"
        return converted

    def writeStringToFile(stringToWrite, fileToWrite):#
        text_file = open(fileToWrite, "w")
        text_file.write(stringToWrite)
        text_file.close()

    subtitles = parser.parse(inputSRTFileName)
    newSubtitle = ""
    for subtitle in subtitles:
        newSubtitle += convertOneSubtitleLine(subtitle)
    writeStringToFile(newSubtitle, outputSRTFileName)

system('cls')
#createCSVFromSRT(inputSRTFileName,untranslatedCSVFile)
translateWholeSubtitle()