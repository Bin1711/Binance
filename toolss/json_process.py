import json
import os
def printj(text): 
    """
    Print beautiful json file
    """
    tmpText = json.loads(text)
    tmpText1 = json.dumps(tmpText,indent = 2)
    print(tmpText1)
    return tmpText1



def createNewJsonDataFile(name):
    """
    :param name: The name of new json file
    """
    with open("./data/"+ name + ".json",'w') as fp: 
        pass



def transferDataToJsonFile(data,file):
    """
    The file is stored in `./data/file.json`
    :param name: The name of object containing data
    :param file: The name of file conveying data
    """
    # tmpText = json.loads(data)
    # tmpText1 = json.dumps(tmpText,indent = 2)
    with open("./data/"+file + ".json",'a') as fp:
        fp.write(data)
    pass



def clearDataInJsonFile(file):
    """
    :param file: The name of file conveying data
    """
    open("./data/"+file+".json", "w").close()


def deleteLastCharacterInJsonFile(file):
    """
    Delete the last character in a Json File
    :param file: The name of file
    """
    with open("./data/"+file + ".json", 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    pass