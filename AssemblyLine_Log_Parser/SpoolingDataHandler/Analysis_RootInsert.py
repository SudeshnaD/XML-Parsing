from xml.dom import minidom
import glob
import io,os,sys

#import SpoolingData


def root_insertion():
        os.chdir("SpoolingData")#move up one directory and access subdirectory
        ErrorInfo_files=glob.glob('Logfile.xml')
        for f in ErrorInfo_files:
                with open(f,"r",encoding="utf-8") as inXML:
                        xml_object ="<root>"+ '\n'+ inXML.read()+ '\n'+"</root>"
                        outputfile=io.open('Output{}'.format(f),'w', encoding='utf-8')#io module used to overcome unicodeencodeerror while writing the input utf-8 file
                        outputfile.write(xml_object)
                        outputfile.close()
        print(glob.glob('Output*')[0])
        os.chdir("..")
        return glob.glob('Output*')


""" def parse_file(f):
        doc=minidom.parse(f)
        _parent_node=doc.getElementsByTagName('IndividualGUID')
        for i in _parent_node:
                 """

 
"""if __name__=='__main__':
        try:
                #if not os.path.exists(r'SpoolingData\OutputLogfile.xml'):
                #        root_insertion()
                root_insertion()
        except Exception as e:
                print('Error in line {}'.format(sys.exc_info()[-1].tb_lineno)) 
        """