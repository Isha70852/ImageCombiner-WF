import PySimpleGUI as sg
import io
import os
from PIL import Image
import json
import webbrowser

 

# 變數

# 原始檔案路徑
folder = "" #開啟的資料夾
filelist = [] #儲存檔案路徑(用來開啟的)

# FileList
filename = [] #檔案的名字
filename_choose = "" #在listbox選擇第幾個

#素材
assetname = [] #素材的名字(等於檔案的名字)
assetDict = {} #包含素材訊息的字典 (素材名字: [位置, 圖像])

# 畫布
canvasWidth = 1
canvasHeight = 1
column = 1
row = 1
cellsizeColumn = canvasWidth / column #直行cellsize
cellsizeRow = canvasHeight / row #橫列row size

#圖片方向
#Graph 座標(左下為(0,0))
DIRECTIONS = {'left':(-1,0),'right':(1,0),'up':(0,1),'down':(0,-1)}
#Pillow座標(左上為(0,0))
DIRECTIONS2 = {'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}
direction = DIRECTIONS['up']
direction2 = DIRECTIONS2['up']

graph = sg.Graph(
        canvas_size= (canvasWidth,canvasHeight),
        graph_bottom_left=(0, 0),
        graph_top_right=(canvasWidth,canvasHeight),
        pad=(0,0),
        change_submits=True,
        background_color='lightblue',
        key= 'graph')

# 模板
template_list_static = {
                "" : [0,0,1,1],
                "臉圖 576x288  4行2列" :[576,288,4,2],
                "人物行走圖(1個人): 144x144  3行4列":[144,144,3,4],
                "人物行走圖(8個人): 576x384  12行 8列" : [144,144,3,4],
                "人物戰鬥圖(1組動作) 192x64  3行1列" :[576,384,12,8],
                "人物戰鬥圖(所有動作) 576x384  9行6列":[576,384,9,6]
}

#空的template 要用來操作用
template_list = {}
#要用來顯示用
template_show = []

#儲存template的位置
user_template_path = "UserTemplate/UserTemplate.json"

# 載入原始資料
for key in template_list_static:
    template_list[key] = template_list_static[key]

#開啟自訂模板
with open(user_template_path, 'r') as data:
    try:
        user_data = json.load(data)
        for key in user_data:
            template_list[key] = user_data[key]
        
    except Exception:
        pass
        

def CreateMainWindow():
    menu_layout = [
        ['檔案', ['創建新畫布','開啟素材資料夾', '另存新檔']],
        ['關於',['關於']]]
    

    Column1_layout = sg.Column(layout = [
        [sg.Text("", key = '-CURRENTFOLDER-')],
        [sg.Frame("檔案" , layout = [
            [sg.Listbox([], size = (50,10) ,enable_events=True, key = '-FILELIST-' )],
            [sg.Push(),sg.Button('加入畫布',key = '-ADD-')]] , size = (220,250))],
            [sg.Frame("預覽", layout =[
                [sg.Image(size = (200,200), key = '-PREVIEWIMAGE-')]] , size = (220,220))]
        ], size = (250,550))

        
    Column2_layout = sg.Column(layout= [[]],key = '-COLUMNGRAPH-' )
        
    

    Column3_layout = sg.Column(layout= [
        [sg.Frame('素材', layout = [
            [sg.Listbox([], size = (50,10) ,enable_events=True, key = '-ASSETLIST-')],
            [sg.Push(), sg.Button('刪除',key = '-DELETE-') ]], size = (200,250))],
            [sg.Frame("操作", layout = [[sg.Push(), sg.Button("上", key = '-UP-'), sg.Push()],
            [sg.Button("左", key = '-LEFT-'),sg.Button("下", key = '-DOWN-'), sg.Button("右", key = '-RIGHT-')]])]] )
    

    layout = [
    [sg.Menu(menu_layout)],
    [Column1_layout,sg.Push(),Column2_layout, sg.Push(), Column3_layout],
    [sg.VPush()],
    [sg.Column(layout = [[sg.Text("畫布尺寸" , key=  '-CANVASSIZE-'), sg.Push(), sg.Text("",key = '-INFO-')]], background_color= 'black', expand_x= True)]
    
    ]
    return sg.Window('ImageCombiner-WF', layout , size = (1200,620), resizable= True, finalize=True, return_keyboard_events= True)

def CreateWindow2():
    global template_list
    global template_show

    for key in template_list:
        template_show.append(key)

    layout2 = [
    [sg.Frame("範本: ", layout = [[sg.Combo(template_show,default_value=template_show[0], expand_x= True,  readonly= True ,enable_events= True,  key = '-TEMPLATE-')],
                                    [sg.Input("", size=(30,10), key = '-TEMPLATENAME-'), sg.Button("創建範本", key = '-CREATENEWTEMPLATE-'), sg.Button("刪除範本", key = '-DELETETEMPLATE-')]], expand_x= True)],
    [sg.Frame("畫布大小: " , layout= [[sg.Text("寬: ") ,sg.Input("", size = (30,10), key = '-CANVASWIDTH-')],
                                      [sg.Text("高: ") ,sg.Input("", size = (30,10), key = '-CANVASHEIGHT-')]])],
    [sg.Frame("分割: ", layout = [[sg.Text("行: "), sg.Input("", size = (30,10), key = '-COLUMN-')],
                                  [sg.Text("列: "), sg.Input("", size = (30,10), key = '-ROW-')]])],
    [sg.Push(), sg.Button("確認", key = "-CONFIRM-" , ), sg.Button("取消", key = "-CANCEL-"), sg.Push()]
    ]
    return sg.Window('建立新畫布', layout= layout2, size = (400,300), finalize=True, disable_close= True)

#選擇模板後將數據填上
def ShowTemplate():
    global template_list
    template =  values['-TEMPLATE-']
    

    template_value =  template_list.get(template)
    #將數據填上
    window2['-CANVASWIDTH-'].update(template_value[0])
    window2['-CANVASHEIGHT-'].update(template_value[1])
    window2['-COLUMN-'].update(template_value[2])
    window2['-ROW-'].update(template_value[3])
    window2['-TEMPLATENAME-'].update(template)  
    

#儲存模板
def SaveNewTemplate():
    global template_list
    global template_show
    global window2
    userData = {}
    if (values['-TEMPLATENAME-'] != "" and
            isinstance(int(values['-CANVASWIDTH-']), int) and
            isinstance(int(values['-CANVASHEIGHT-']), int) and
            isinstance(int(values['-COLUMN-']), int) and isinstance(int(values['-ROW-']), int)):
        if(values['-TEMPLATENAME-'] in template_list):
            sg.popup("該名稱已存在")
        else:
            with open(user_template_path, 'r') as path:
                #嘗試讀取
                try:
                    userData =  json.load(path)
                except:
                    pass
                print("這是userdata: ", userData)
                userData[values['-TEMPLATENAME-']] = [int(values['-CANVASWIDTH-']), int(values['-CANVASHEIGHT-']), int(values['-COLUMN-']),int(values['-ROW-'])]
                print("這是userdata後: ", userData)
                #將新值寫入
                with open(user_template_path, 'w') as data:
                    json.dump(userData, data)
                    sg.popup("已創建新模板")
            #更新template_list和template_show
            with open(user_template_path, 'r') as new_data:
                NewuserData =  json.load(new_data)
                template_list = {}
                template_show = []
                for key in template_list_static:
                    template_list[key] = template_list_static[key]
                for key in NewuserData:
                    template_list[key] = NewuserData[key]
                window2.close()
                window2 = CreateWindow2()
    else:
        sg.popup("輸入的資訊有誤")
    
#刪除模板
def DeleteTemplate():
    global template_list 
    global template_show
    global window2
    userData = {}
    
    with open(user_template_path, 'r') as path:
        #嘗試讀取
        try:
            userData =  json.load(path)
            if values['-TEMPLATENAME-'] in userData: 
                del userData[values['-TEMPLATENAME-']]
                #將新值寫入
                with open(user_template_path, 'w') as data:
                    json.dump(userData, data)
                    sg.popup("已刪除模板")
                #更新template_list和template_show
                with open(user_template_path, 'r') as new_data:
                    NewuserData =  json.load(new_data)
                    template_list = {}
                    template_show = []
                    for key in template_list_static:
                        template_list[key] = template_list_static[key]
                    for key in NewuserData:
                        template_list[key] = NewuserData[key]
                    window2.close()
                    window2 = CreateWindow2()
            else:
                pass 

        except:
            pass

def CreateBlankImage():
    global graph
    global cellsizeColumn
    global cellsizeRow
    global canvasWidth
    global canvasHeight
    global column
    global row
    global window1
    global window2
    global folder
    global filename
    global assetname
    global assetDict

    # 取得使用者輸入的值
    canvasWidth = int(values['-CANVASWIDTH-'])
    canvasHeight = int(values['-CANVASHEIGHT-']) 
    column = int(values['-COLUMN-']) 
    row = int(values['-ROW-'])

    # 設定需要的數值
    cellsizeColumn = canvasWidth / column
    cellsizeRow = canvasHeight / row
    

    #更新畫布
    graph = sg.Graph(
        canvas_size= (canvasWidth,canvasHeight),
        graph_bottom_left=(0, 0),
        graph_top_right=(canvasWidth,canvasHeight),
        pad=(0,0),
        change_submits=True,
        background_color= "white",
        key= 'graph'
    )

    #更新螢幕
    window1.close()
    window2.hide()
    window1 = CreateMainWindow()
    window1.extend_layout(window1['-COLUMNGRAPH-'], [[graph]])
    window1.visibility_changed()

    #更新資訊
    window1['-CANVASSIZE-'].update(f'畫布尺寸: ({canvasWidth},{canvasHeight})')
    window1['-INFO-'].update("建立新畫布")
    window1['-CURRENTFOLDER-'].update(folder)
    window1['-FILELIST-'].update(filename)

    #清空數據
    window2['-CANVASWIDTH-'].update("")
    window2['-CANVASHEIGHT-'].update("")
    window2['-COLUMN-'].update("")
    window2['-ROW-'].update("")
    window2['-TEMPLATENAME-'].update("")
    assetname = []
    assetDict.clear()


def open_folder():
    global folder
    global filelist
    global filename

    folder = sg.popup_get_folder("選擇資料夾", no_window= True)
    print("打開的: " ,folder)
    if not folder:
        return
    filelist = []
    filename = []
    for f in os.listdir(folder):
        if f.lower().endswith((".jpg", ".png")):
            filelist.append(os.path.join(folder, f)) #.replace("/","\\"))
            filename.append(f)

# 顯示預覽圖:
def ShowPreviewImage():
    # 如果為空則返回，否則會錯誤
    if values['-FILELIST-'] == []:
        return
    
    #找到原始路徑
    filename_index = os.path.join(folder, values['-FILELIST-'][0])
    #找到該路徑在filelist裡面的索引
    filename_choose = filelist.index(filename_index)
    #顯示預覽圖
    window1['-PREVIEWIMAGE-'].update(Convert_to_btye(filelist[filename_choose], resize= (200,200)))
        

# 更新素材list
def UpdateAssetList():
    global assetname
    global graph
    global assetDict
    global row
    # 如果為空則返回，否則會錯誤
    if values['-FILELIST-'] == [] or values['-FILELIST-'][0] == None:
        return

    #檢查該素材名稱是否存在    
    checkassetName = values['-FILELIST-'][0]
    while checkassetName in assetname:
        checkassetName =   checkassetName + "(1)"
        print("已存在，更新為", checkassetName)

    #將素材名稱加入assetname(window1['-ASSETLIST-']使用的list)
    assetname.append(checkassetName)
    window1['-ASSETLIST-'].update(assetname)
    window1['-ASSETLIST-'].update(set_to_index = [len(assetname) - 1])
    print("現在的key: ",checkassetName)


    #--- 將選取的素材畫到畫布上---
    
    # 將素材畫到畫布上
    filename_path = os.path.join(folder, values['-FILELIST-'][0])
    assetImagePath = Image.open(filename_path)
    assetimage = Convert_to_btye(filename_path)
    assetLocation = [0,1]
    assetLocationforSave  = [0,  row- 1]
    img_id =  graph.draw_image(data = assetimage, location=(0,cellsizeRow))

    #添加素材到素材字典
    assetDict[checkassetName] = [assetLocation, assetimage,  assetImagePath , assetLocationforSave]
    

# 將圖片轉成Tkinter能讀取的形式
def Convert_to_btye(file_or_bytes, resize=None, fill=False):
    img = None
    if isinstance(file_or_bytes, str):
        img = Image.open(file_or_bytes)

        cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height / cur_height, new_width / cur_width)
        img = img.resize((int(cur_width * scale), int(cur_height * scale)), Image.ANTIALIAS)
    
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()
    

# 儲存為新圖片
def Save(fileName):
    global canvasWidth
    global canvasHeight
    global assetDict
    
    # 建立新畫布(RGBA)
    blankCanvas = Image.new(mode = "RGBA", size = (canvasWidth, canvasHeight), color = (255, 255, 255,255))
    for i in assetDict:
        blankCanvas.paste(assetDict[i][2] , (convert_pos_to_pixel(assetDict[i][3])))

    #blankCanvas.show()
    if fileName.endswith(".jpg"):
        saveBlankImage = Image.new(mode="RGB",size=blankCanvas.size, color = (255,255,255))
        #將自己當作模板 黑色的地方代表透明度為0
        saveBlankImage.paste(blankCanvas, (0,0), blankCanvas)
        saveBlankImage.save(fileName)
        window1['-INFO-'].update("已儲存")
    elif fileName.endswith(".png"):
        blankCanvas.save(fileName)
        window1['-INFO-'].update("已儲存")
    else:
        sg.popup("不支援的格式")

def convert_pos_to_pixel(cell) :
    tl = (int(cell[0] * cellsizeColumn), int(cell[1] * cellsizeRow))
    #br = (tl[0] + cellsize ,tl[1] + cellsize)
    return tl


# 移動選定的image
def moveImage():
    global move
    global graph
    global canvasWidth
    global canvasHeight
    global assetDict
    if move  and values['-ASSETLIST-'] != [] and values['-ASSETLIST-'][0] in assetDict:
        move = False
        
        #設定新位置
        newPos = [assetDict[values['-ASSETLIST-'][0]][0][0] + direction[0],assetDict[values['-ASSETLIST-'][0]][0][1] + direction[1]]
        newposForSave = [assetDict[values['-ASSETLIST-'][0]][3][0] + direction2[0],assetDict[values['-ASSETLIST-'][0]][3][1] + direction2[1]]

        print(assetDict[values['-ASSETLIST-'][0]][3])
        print(newposForSave)
        print(assetDict[values['-ASSETLIST-'][0]][0])
        #確認沒有超過
        tl = convert_pos_to_pixel(newPos)
        if(tl[0] > canvasWidth - cellsizeColumn  or  tl[1] > canvasHeight +1 or tl[0] < 0 or tl[1] <  cellsizeRow):
            return
        
        #更新位置
        assetDict[values['-ASSETLIST-'][0]][0] = newPos
        assetDict[values['-ASSETLIST-'][0]][3] = newposForSave

        
        graph.erase()
        for img in assetDict:
            graph.draw_image(data = assetDict[img][1], location= convert_pos_to_pixel(assetDict[img][0]))

        

def DeleteAsset():
    global assetname
    global assetDict
    global graph

    if values['-ASSETLIST-'] == [] or values['-ASSETLIST-'][0] == None:
        return

    deleteassetName = values['-ASSETLIST-'][0]
    assetname.remove(deleteassetName)
    del assetDict[deleteassetName]

    #更新畫面
    window1['-ASSETLIST-'].update(assetname)
    graph.erase()
    for img in assetDict:
        graph.draw_image(data = assetDict[img][1], location= convert_pos_to_pixel(assetDict[img][0]))

def About(window1):
    layout =[[sg.Text("ImageCombiner-WF",)],
            [sg.Text("ImageCombiner-WF is a free, lightweight app for combining images.\n\nPowered by PySimpleGUI and Pillow.")],
            [sg.Text("WizardForest."), sg.Text("Learn more.",text_color= 'lightblue', enable_events= True, key = '-ABOUT-')],
            [sg.Push(),sg.Button("確認"), sg.Push()]]

    win = sg.Window("關於", layout, enable_close_attempted_event=True)
    event, value = win.read()
    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
        event = "CANCEL"
    win.close()
    window1.write_event_value(event, None)
    print(event)


sg.theme("Dark")

window1 = CreateMainWindow()

window2 = CreateWindow2()

window2.hide()



while True:
    window, event, values = sg.read_all_windows(timeout= 10)
    
    if event == sg.WIN_CLOSED:
        break
    if event == '開啟素材資料夾':
        open_folder()
        window['-CURRENTFOLDER-'].update(folder)
        window['-FILELIST-'].update(filename)
        window.refresh()
    
    if event == '創建新畫布':
        window2.un_hide()
        

    if event == '-FILELIST-':
        ShowPreviewImage()
    
    if event == '-ADD-':   
        UpdateAssetList()
        
    if event =='另存新檔':
        filenameOutput = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to',default_extension='.png',file_types=(("PNG",".png"),("JPG",".jpg")),  save_as=True, no_window= True)
        print(filenameOutput)
        if filenameOutput != "":
            Save(filenameOutput)
        

    if event in ['Left:37', '-LEFT-']:
        direction = DIRECTIONS['left']
        direction2 = DIRECTIONS2['left']
        move = True
        moveImage()
    if event in ['Up:38', '-UP-']:
        direction = DIRECTIONS['up']
        direction2 = DIRECTIONS2['up']
        move = True
        moveImage()
    if event in ['Right:39', '-RIGHT-']:
        direction = DIRECTIONS['right']
        direction2 = DIRECTIONS2['right']
        move = True
        moveImage()
    if event in ['Down:40', '-DOWN-'] :
        direction = DIRECTIONS['down']
        direction2 = DIRECTIONS2['down']
        move = True
        moveImage()
    
    if event == '-CONFIRM-':
        CreateBlankImage()
        
        
    if event == '-CANCEL-':
        window2.hide()

    
    if event == '-TEMPLATE-':
        ShowTemplate()

    if event =='-CREATENEWTEMPLATE-':
        SaveNewTemplate()

    if event == '-DELETETEMPLATE-':
        DeleteTemplate()
    
    if event =='-DELETE-':
        DeleteAsset()

    if event == '關於':
        About(window1)

    if event == '-ABOUT-':
        webbrowser.open("https://home.gamer.com.tw/artwork.php?sn=5448028")

window1.close()
window2.close()
