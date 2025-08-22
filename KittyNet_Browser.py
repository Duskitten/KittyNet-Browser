import blessed
import time
import requests
import signal
import os
import sys
launch_arguments = sys.argv

term = blessed.Terminal()
boarder_char = "█"
boarder_color = [255,255,255]
foreground_color = [255,255,255]
background_color = [0,0,0]

blink_char = "█"
blink_alt = " "
blink_on = False
blink = " "
counter = 0
version = "0.0.2"
webpage_limits = [2,6,term.width-4,term.height-7]
current_webpage_formatted = []
current_webpage_offset = 0
textbox_url = "$Local_Sites/Boot_Readme"
locked_url = "$Local_Sites/Boot_Readme"
editing_textbox = False
original_site_response = """"""
viewing_source = False

base_ui_text = [] #This is for the base of the UI
full_ui_text = []

interaction_points = []


rendered_ui_text = []
parsed_site_text = []
original_site_text = []
console_text = []
current_console_offset = 0
in_console = False



def update_ui(OffsetY, LineTotal):
    global full_ui_text
    for i in range(LineTotal):
        print(term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(foreground_color[0],foreground_color[1],foreground_color[2])+term.move_xy(0,OffsetY+i)+full_ui_text[OffsetY+i])
        #draw_text(0,OffsetY+i,rendered_ui_text[OffsetY+i],[0,0,0],[255,255,255])
    

#This is how we output text with some customizing!
def draw_text(PosX, PosY, Text):
    global full_ui_text
    cloned = full_ui_text[PosY]

    for i in range(len(Text)):
        text = cloned[:PosX + i] + Text[i] + cloned[PosX + i + 1:]
        full_ui_text[PosY] = text
        cloned = text

##This is how we draw straight lines, no diagonals
def draw_line(StartX,StartY,Size, Horizontal, Color, ColorText, Text):
        if Horizontal:
            Face_String = Text * Size
            draw_text(StartX,StartY,Face_String,Color,ColorText)
        else:
            for Point in range(Size):
                draw_text(StartX,StartY+Point,Text,Color,ColorText)

##This is how we draw boxes, we can fill them too
def draw_box(PosX,PosY,SizeX,SizeY, Filled, Color, ColorText, Text, init):
    global base_ui_text
    global full_ui_text
    cloned = base_ui_text
    if init:
        base_ui_text = []
        full_ui_text = []

    for y in range(SizeY):
        y += PosY
        Face_String = ""
        if y == PosY or y == PosY + SizeY - 1:
            Face_String += Text * SizeX
        else:
            Face_String += Text+(" " * (SizeX-2))+Text

        if init:
            base_ui_text.append(Face_String)
            full_ui_text.append(Face_String)
        else:
            for i in range(SizeX):
                cloned[y] = cloned[y][:PosX + i] + Face_String[i] + cloned[y][PosX + i + 1:]
                full_ui_text[y] = cloned[y]

def gen_line():
    line = ""
    for x in range(webpage_limits[2]):
        line += " "

    return line

def reparse_text(text):
    global current_webpage_formatted

    original_text = text
    real_text = text
    edited_line = " "*webpage_limits[2]
    edited_points = []
    skip_amount = 0
    enterpoint_count = 0
    linecounter = 0
    last_modifier = []
    
    for basechar in range(len(text)):
        if skip_amount == 0:
            if text[basechar] == "[" and text[basechar-1] != "/":
                secondchar_ending = 0
                for secondchar in range(len(text[basechar:])):
                    if text[basechar:][secondchar] == "]":
                        count_text = text[basechar:basechar+secondchar_ending+1]
                        if "c_line" in count_text:
                            linecounter += 1
                        textline = "{Enter_"+str(enterpoint_count)+"}"
                        original_text = original_text.replace(count_text,textline,1)
                        real_text = real_text.replace(count_text,"",1)
                        enterpoint_count += 1
                        edited_points.append([textline,basechar,secondchar_ending+basechar,count_text,""])
                        skip_amount = (basechar+secondchar_ending)-basechar
                        break
                    secondchar_ending += 1
            elif text[basechar] == "[" and text[basechar-1] == "/":
                original_text = original_text.replace("/","",1)
        else:
            skip_amount -= 1

    edited_line = edited_line[len(real_text):]

    if linecounter > 0:
        edited_line = " " * int(len(edited_line)/linecounter)

    for i in range(len(edited_points)):
        split = edited_points[i][3][1:len(edited_points[i][3])-1].split(" ")
        for splitdata in split:
            match splitdata:
                case "c_line":
                    edited_points[i][4] += edited_line
                    if term.width % 2 != 0:
                        edited_line += " "
                case "c_bold":
                    edited_points[i][4] += term.bold
                case "c_color_reset":
                    edited_points[i][4] += term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
                case "c_reset":
                    edited_points[i][4] += term.normal + term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
                case _:
                    if splitdata.endswith(")"):
                        if splitdata.startswith("c_on_color("):
                            data = splitdata[len("c_on_color("):len(splitdata)-1].split(",")
                            edited_points[i][4] += term.on_color_rgb(data[0],data[1],data[2])
                        elif splitdata.startswith("c_color("):
                            data = splitdata[len("c_color("):len(splitdata)-1].split(",")
                            edited_points[i][4] += term.color_rgb(data[0],data[1],data[2])

    for i in range(enterpoint_count):
        textline = "{Enter_"+str(i)+"}"
        original_text = original_text.replace(textline, edited_points[i][4])

    original_text+= term.normal + term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
    current_webpage_formatted.append(original_text)

def draw_ui():
    draw_box(0,0,term.width,term.height-1, False,background_color,boarder_color,boarder_char, True)
    draw_box(0,0,term.width,5, False,background_color,boarder_color,boarder_char, False)
    draw_box(0,0,20,5, False,background_color,boarder_color,boarder_char,False)
    draw_text(2,term.height-2,"| F1:URL Bar | F2:Toggle Source | F3:Toggle Console |")
    draw_text(3,2,"KittyNet "+ version)
    draw_text(22,2,"URL:")
    draw_text(26,2,textbox_url)
    update_ui(0,term.height-1)

def draw_console():
    draw_ui()
    y_offset = 0
    for text in range(len(console_text)):
        text += current_console_offset
        if text < len(console_text) and y_offset < webpage_limits[3]-2:
            try:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text].format(term = term))
            except:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text])
            y_offset += 1
    update_ui(webpage_limits[1],y_offset)

def draw_webpage():
    global webpage_limits
    draw_ui()
    y_offset = 0
    for text in range(len(current_webpage_formatted)):
        text += current_webpage_offset
        if text < len(current_webpage_formatted) and y_offset < webpage_limits[3]-2:
            try:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text].format(term = term))
            except:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text])
            y_offset += 1

    update_ui(webpage_limits[1],y_offset)


def reload_webpage_from_memory(Webpage):
    current_webpage_formatted.clear()
    for text in Webpage.splitlines():
        reparse_text(text)
    #draw_ui()
    draw_webpage()

def reload_source_from_memory(Webpage):
    current_webpage_formatted.clear()
    for text in Webpage.splitlines():
        current_webpage_formatted.append(text)
    #draw_ui()
    draw_webpage()

def load_webpage(URL):
    global locked_url
    global textbox_url
    if URL.startswith("--"):
        match URL.lower():
            case "--reload":
                reload_config()
                textbox_url = locked_url
                draw_text(26,2,textbox_url)
                load_webpage(textbox_url)
    elif URL.startswith("$"):
        locked_url = URL
        URL = URL[1:]
        try:
            console_print("Attempting to Access: " + "./"+URL)
            if os.path.isfile("./"+URL):
                with open("./"+URL) as f:
                    console_print("File Found Successfully")
                    reload_webpage_from_memory(f.read())
            else:
                raise Exception("")
        except:
            draw_ui()
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: ./"+ URL)

    else:
        urlfull = "http://"+URL
        console_print("Attempting to Connect to: " + urlfull)
        try:
            response = requests.get(urlfull,timeout=1)
            response.raise_for_status()
            if response.text:
                console_print("Connection Successful")
                locked_url = URL
                with open("./Websites/"+URL, "w") as f:
                    f.write(response.text)
                reload_webpage_from_memory(response.text)
        except requests.exceptions.RequestException:
            draw_text(webpage_limits[0],webpage_limits[1],"Error Connecting to: "+ URL)
        except requests.exceptions.HTTPError:
            draw_text(webpage_limits[0],webpage_limits[1],"Error Connecting to: "+ URL)



def on_resize(sig, action):
    webpage_limits[2] = term.width-4
    webpage_limits[3] = term.height-7

    if locked_url.startswith("$"):
        URL = locked_url[1:]
        try:
            if os.path.isfile("./"+URL):
                with open("./"+URL) as f:
                    if viewing_source:
                        reload_source_from_memory(f.read())
                    else:
                        reload_webpage_from_memory(f.read())
            else:
                raise Exception("")
        except:
            draw_ui()
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: ./"+ URL)
    else:
        if os.path.isfile("./Websites/"+locked_url):
            with open("./Websites/"+locked_url) as f:
                if viewing_source:
                    reload_source_from_memory(f.read())
                else:
                    reload_webpage_from_memory(f.read())
        else:
            draw_ui()
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: http://"+ locked_url)

def console_print(Text):
    console_text.append(Text)
    
def reload_config():
    global foreground_color
    global background_color
    global boarder_char
    
    
    if os.path.isfile("./KittyNet.config"):
        console_print("Config File Found Successfully")
        with open("./KittyNet.config") as f:
            for i in f.read().splitlines():
                current = i.split(" ")
                match current[0]:
                    case "foreground_color":
                        foreground_color = current[1].split(",")
                    case "background_color":
                        background_color = current[1].split(",")
                    case "boarder_character":
                        boarder_char = current[1]

with term.fullscreen(), term.hidden_cursor(), term.cbreak():

    console_print("!!!KittyNet Console!!!")
    console_print("---")
    console_print("KittyNet Version "+ version)
    console_print("Copyright Duskitten 2025")
    console_print("Distributed under MIT License")
    console_print("---")
    
    if "--website" in launch_arguments:
        position = launch_arguments.index("--website")
        if position + 1 <= len(launch_arguments):
            textbox_url = launch_arguments[position + 1]
            locked_url = launch_arguments[position + 1]


    if not os.path.exists("./Websites"):
        os.makedirs("./Websites")
    else:
        console_print("Websites Folder Found Successfully")
    
    if not "--ignoreconfig" in launch_arguments: 
        reload_config()
                
    #draw_ui()

    signal.signal(signal.SIGWINCH, on_resize)
    tested = False
    x = 0

    load_webpage(textbox_url)

    while True:
        
        if editing_textbox:
            counter += 1
            if counter % 20000 == 0:
                counter = 0
                
                blink_on =  not blink_on
                if blink_on:
                    blink = blink_char
                else:
                    blink = blink_alt

                draw_text(26+len(textbox_url),2,blink)
                update_ui(2,1)
            
            
        val = ''
        val = term.inkey(0)
            
         


        if val.is_sequence:
            match val.name:
                case "KEY_ENTER":
                    if editing_textbox:
                        editing_textbox = False
                        in_console = False
                        viewing_source = False
                        load_webpage(textbox_url)
                case "KEY_BACKSPACE":
                    if not editing_textbox:
                        pass
                    else:
                        textbox_url = textbox_url[:-1]
                        draw_text(26+len(textbox_url)+1,2," ")
                        draw_text(26+len(textbox_url),2,blink_char)
                        draw_text(26,2,textbox_url)
                        update_ui(2,1)
                case "KEY_DOWN":
                    if not editing_textbox:
                        if current_webpage_offset < len(current_webpage_formatted):
                            current_webpage_offset += 1
                            draw_webpage()
                case "KEY_UP":
                    if not editing_textbox:
                        if current_webpage_offset != 0:
                            current_webpage_offset -= 1
                            draw_webpage()
                case "KEY_TAB":
                    pass
                case "KEY_F1":
                    if not editing_textbox:
                        editing_textbox = True
                    else:
                        editing_textbox = False
                        in_console = False
                        viewing_source = False
                        load_webpage(textbox_url)

                case "KEY_F2":
                   if not editing_textbox:
                        if viewing_source:
                            viewing_source = False
                            on_resize(1,1)
                        else:
                            viewing_source = True
                            on_resize(1,1)
                case "KEY_F3":
                   if not editing_textbox:
                        if in_console:
                            in_console = False
                            on_resize(1,1)
                        else:
                            in_console = True
                            #draw_ui()
                            draw_console()
        elif val:
            match val:
                case "`":
                    pass

            if editing_textbox:
                textbox_url += val
                draw_text(26,2,textbox_url)
                draw_text(26+len(textbox_url),2,blink_char)
                update_ui(2,1)
            else:
                pass
            
        