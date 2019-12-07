import lxml.etree as etree
import dicttoxml,json,xmltodict

def createXML(filename):
    
    with open(filename,'r') as f:
        schema=json.load(f)

    xml=dicttoxml.dicttoxml(schema)
    return xml

def createJSON(filename):
    xml=etree.parse(filename)
    #xmlstring=etree.tostring(xmll)
    #jsonfile=json.loads(xmlstring)
    dict=xmltodict.parse(etree.tostring(xml))
    return json.dumps(dict) 



