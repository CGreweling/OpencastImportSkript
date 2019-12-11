import xml.etree.ElementTree as ET
import xml.etree as ETREE


def doit():
    tree = ET.parse('Mediapackage_example.xml')
    root = tree.getroot()
    #root = ET.fromstring(country_data_as_string)


    # for i in root.findall('{http://mediapackage.opencastproject.org}media/{http://mediapackage.opencastproject.org}track/{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
    #    print(i.tag,i.attrib,i.text)
    #
    #
    # for tracks in root.findall('{http://mediapackage.opencastproject.org}media/{http://mediapackage.opencastproject.org}track'):
    #      print(tracks.get('id'))
    #      for tags in tracks.findall('{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
    tags = []
    for catalog in root.findall('{http://mediapackage.opencastproject.org}metadata/{http://mediapackage.opencastproject.org}catalog'):
        print(catalog.get('id'))
        url = catalog.find('{http://mediapackage.opencastproject.org}url').text
        print(url)
        for tag in catalog.findall('{http://mediapackage.opencastproject.org}tags/{http://mediapackage.opencastproject.org}tag'):
            print(tag.text)
            tags.append(tag.text)

    tags = ",".join(tags)
    print(tags)
#
    # print("hello")
    # for child in root:
    #    print(child.tag, child.attrib)
    #    for child2 in child:
    #      print(child2.tag, child2.attrib)


def main():
    doit()



if __name__ == "__main__":
    main()