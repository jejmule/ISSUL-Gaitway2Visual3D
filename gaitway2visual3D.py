#kivy application to convert csv gaitway data to visual 3D ascii format
#import kivy app
from kivy.app import App
#import kivy  properties
from kivy.properties import ListProperty
from pathlib import Path
import pandas as pd

#read txt file and convert to visual 3D format
def convert_txt_file(file_path,host_path):
    #open the txt file
    df = pd.read_table(file_path, sep='\t', header=43,encoding='mbcs')
    #extract GRFx lateral (N), GRFy fore-aft (N), GRFz vertical (N), CoPx lateral (m), CoPy fore-aft (m), Mx (N.m), My (N.m), Mz (N.m) as FP1
    parameters = [
        'Time (s)','Speed (m/s)','Grade (%)',
        'GRFx lateral (N)', 'GRFy fore-aft (N)','GRFz vertical (N)','CoPx lateral (m)', 'CoPy fore-aft (m)','Mx (N.m)','My (N.m)','Mz (N.m)','Tz free moment (N.m)',
        'FxL(N)','FyL(N)','FzL(N)','CoPxL(m)','CoPyL(m)',
        'FxR(N)','FyR(N)','FzR(N)','CoPxR(m)','CoPyR(m)'
    ]
    datas = df[parameters]
    #c3d file path
    c3d_file = file_path.with_suffix('.c3d')
    c3d_file = host_path + c3d_file.name    #add \ if not present

    #write file header
    header = ""
    #first line is c3d file path for each daataframe in datas
    cols = len(datas.columns)
    for i in range(cols):
        header += '\t' + str(c3d_file)
    header += '\n'
    #second line is signal name
    params = []
    for parameter in parameters:
        #remove text after space
        params.append('Gaitway.' + parameter.split(' ')[0].split('(')[0])
    #join with tab parameter to header
    header += '\t'
    header += '\t'.join(params)
    header += '\n'
    #third line is signal type
    for i in range(cols):
        header += '\t' + 'ANALOG'
    header += '\n'
    #fourth line is signal folder
    for i in range(cols):
        header += '\t' + 'ORIGINAL'
    header += '\n'
    #fifth line is COMPONENT
    header += 'ITEM'
    for i in range(cols):
        header += '\tX'
    header += '\n'

    #export datas to string
    content = datas.to_csv(header=False,sep='\t')

    #write to file
    #print(header+content)
    #add _converted to filename
    with open(file_path.with_name(file_path.stem + '_converted.txt'), 'w') as f:
        f.write(header+content)
    return

class Gaitway2Visual3DApp(App):
    files_list = ListProperty([])

    def build(self):
        pass

    #recusively search for the txt file in the subdirectories matching the c3d file
    def check_dir(self,path):
        c3d_files = list(path.glob('*.c3d'))
        #if there is a c3d file in the directory search for the txt file with the same name
        if c3d_files:
            for c3d_file in c3d_files:
                txt_file = c3d_file.with_suffix('.txt')
                if txt_file.exists():
                    self.files_list.append(path/txt_file)
                else :
                    #warning no matching txt file
                    pass
        #else search for the txt file in the subdirectories
        else:
            if path.is_dir():
                for x in path.iterdir():
                    if x.is_dir():
                        self.check_dir(x)
    
    #list all file paths in the directory
    def list_files(self,path):
        self.root.ids.text_input.text = "SEARCHING FOR FILES IN " + str(path) + '\n'
        self.files_list= []
        p = Path(path)
        #iteration through all the directories
        self.check_dir(p)
        self.root.ids.text_input.text += '\n'.join(["\t"+str(file) for file in self.files_list]) + '\n'
    
    #convert the txt file to visual 3D format
    def process_files(self):
        self.root.ids.text_input.text += "START FILES CONVERSION\n"
        for file in self.files_list:
            self.root.ids.text_input.text += "\tConverting " + str(file) + '\n'
            convert_txt_file(file,self.root.ids.host_path.text)
        self.root.ids.text_input.text += "END FILES CONVERSION\n"

if __name__ == '__main__':
    Gaitway2Visual3DApp().run()