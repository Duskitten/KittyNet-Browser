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
last_url = "$Local_Sites/Boot_Readme"
editing_textbox = False
original_site_response = """"""
viewing_source = False

base_ui_text = [] #This is for the base of the UI
full_ui_text = []
current_source_formatted = []
interaction_points = []
selected_interaction_point = -1

rendered_ui_text = []
parsed_site_text = []
original_site_text = []
console_text = []
current_console_offset = 0
current_source_offset = 0
scroll_counter = 0
in_console = False



def update_ui(OffsetY, LineTotal):
    global full_ui_text
    global current_console_offset
    global webpage_limits
    
    
    for i in range(LineTotal):
        print(term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(foreground_color[0],foreground_color[1],foreground_color[2])+term.move_xy(0,OffsetY+i)+full_ui_text[OffsetY+i])
    if not viewing_source:
        update_interactive_layer()

def update_interactive_layer():
    global current_console_offset
    global webpage_limits
    if not in_console and not viewing_source:
        for i in range(len(interaction_points)):
            if interaction_points[i][0]+(-1*current_webpage_offset)+6 < webpage_limits[3]+4 and interaction_points[i][0]+(-1*current_webpage_offset)+6 > webpage_limits[1]-1:
                if interaction_points[i][1] == "Link":
                    normal_color = interaction_points[i][2][1].split(",")
                    normal_on_color = interaction_points[i][2][2].split(",")
                    selected_color = interaction_points[i][2][3].split(",")
                    selected_on_color = interaction_points[i][2][4].split(",")
                    match interaction_points[i][5]:
                        case False:
                            print(term.underline(term.on_color_rgb(normal_on_color[0],normal_on_color[1],normal_on_color[2])+term.color_rgb(normal_color[0],normal_color[1],normal_color[2])+term.move_xy(interaction_points[i][4],interaction_points[i][0]+(-1*current_webpage_offset)+6)+interaction_points[i][2][0]))
                        case True:
                            print(term.underline(term.on_color_rgb(selected_on_color[0],selected_on_color[1],selected_on_color[2])+term.color_rgb(selected_color[0],selected_color[1],selected_color[2])+term.move_xy(interaction_points[i][4],interaction_points[i][0]+(-1*current_webpage_offset)+6)+interaction_points[i][2][0]))
                elif interaction_points[i][1] == "Input":
                    normal_color = interaction_points[i][2][1].split(",")
                    normal_on_color = interaction_points[i][2][2].split(",")
                    selected_color = interaction_points[i][2][3].split(",")
                    selected_on_color = interaction_points[i][2][4].split(",")
                    text_color = interaction_points[i][2][5].split(",")
                    text_on_color = interaction_points[i][2][6].split(",")
                    match interaction_points[i][5]:
                        case False:
                            print(term.on_color_rgb(normal_on_color[0],normal_on_color[1],normal_on_color[2])+term.color_rgb(normal_color[0],normal_color[1],normal_color[2])+term.move_xy(interaction_points[i][4],interaction_points[i][0]+(-1*current_webpage_offset)+6)+interaction_points[i][2][0]+interaction_points[i][6])
                        case True:
                            print(term.on_color_rgb(selected_on_color[0],selected_on_color[1],selected_on_color[2])+term.color_rgb(selected_color[0],selected_color[1],selected_color[2])+term.move_xy(interaction_points[i][4],interaction_points[i][0]+(-1*current_webpage_offset)+6)+interaction_points[i][2][0]+interaction_points[i][6])
                elif interaction_points[i][1] == "Scroll":
                    normal_color = interaction_points[i][2][1].split(",")
                    normal_on_color = interaction_points[i][2][2].split(",")
                    print(term.on_color_rgb(normal_on_color[0],normal_on_color[1],normal_on_color[2])+term.color_rgb(normal_color[0],normal_color[1],normal_color[2])+term.move_xy(interaction_points[i][4],interaction_points[i][0]+(-1*current_webpage_offset)+6)+interaction_points[i][2][0])


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

def reparse_text(text,line):
    global current_webpage_formatted
    global interaction_points

    original_text = text
    real_text = text
    edited_line = " "*webpage_limits[2]
    edited_points = []
    skip_amount = 0
    enterpoint_count = 0
    linecounter = 0
    last_modifier = []
    normal_char = 0
    last_normal_char = []
    
    
    for basechar in range(len(text)):
        if skip_amount == 0:
            if text[basechar] == "[" and text[basechar-1] != "/":
                secondchar_ending = 0
                for secondchar in range(len(text[basechar:])):
                    if text[basechar:][secondchar] == "]":
                        last_normal_char.append(basechar)
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
                normal_char += 1
        else:
            skip_amount -= 1
    
    #console_print(str(last_normal_char))
    
    edited_line = edited_line[len(real_text):]

    if linecounter > 0:
        edited_line = " " * int(len(edited_line)/linecounter)
    
    edited_line_grouped = ""
    
    current_line = 0
    for i in range(len(edited_points)):
        split = edited_points[i][3][1:len(edited_points[i][3])-1].split(" ")
        for splitdata in range(len(split)):
            match split[splitdata]:
                case "c_line":
                    current_line += 1
                    
                    if term.width % 2 != 0 and linecounter > 1:
                        if current_line == linecounter:
                            edited_points[i][4] += edited_line + " "
                            edited_line_grouped += edited_line + " "
                        else:
                            edited_points[i][4] += edited_line
                            edited_line_grouped += edited_line
                            
                    else:
                        edited_points[i][4] += edited_line
                        edited_line_grouped += edited_line

                case "c_bold":
                    edited_points[i][4] += term.bold
                case "c_color_reset":
                    edited_points[i][4] += term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
                case "c_reset":
                    edited_points[i][4] += term.normal + term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
                case _:
                    if split[splitdata].endswith(")"):
                        if split[splitdata].startswith("c_on_color("):
                            data = split[splitdata][len("c_on_color("):len(split[splitdata])-1].split(",")
                            edited_points[i][4] += term.on_color_rgb(data[0],data[1],data[2])
                        elif split[splitdata].startswith("c_color("):
                            data = split[splitdata][len("c_color("):len(split[splitdata])-1].split(",")
                            edited_points[i][4] += term.color_rgb(data[0],data[1],data[2])
                        elif split[splitdata].startswith("c_link("):
                            data = split[splitdata][len("c_link("):len(split[splitdata])-1].replace("(","").replace(")","").split("|")
                            if term.width % 2 != 0:
                                if linecounter == 0:
                                    interaction_points.append([line,"Link",data,edited_points[i][0],last_normal_char[i]+2,False])
                                else:
                                    interaction_points.append([line,"Link",data,edited_points[i][0],len(" "+edited_line_grouped)+last_normal_char[i]-7,False])
                            else:
                                if linecounter == 0:
                                    interaction_points.append([line,"Link",data,edited_points[i][0],last_normal_char[i]+2,False])
                                else:
                                    interaction_points.append([line,"Link",data,edited_points[i][0],len(edited_line_grouped)+last_normal_char[i]-6,False])
                        elif split[splitdata].startswith("c_input("):
                            data = split[splitdata][len("c_input("):len(split[splitdata])-1].replace("(","").replace(")","").split("|")
                            #console_print(data)
                            if term.width % 2 != 0:
                                if linecounter == 0:
                                    interaction_points.append([line,"Input",data,edited_points[i][0],last_normal_char[i]+2,False,""])
                                else:
                                    interaction_points.append([line,"Input",data,edited_points[i][0],len(" "+edited_line_grouped)+last_normal_char[i]-7,False,""])
                            else:
                                if linecounter == 0:
                                    interaction_points.append([line,"Input",data,edited_points[i][0],last_normal_char[i]+2,False,""])
                                else:
                                    interaction_points.append([line,"Input",data,edited_points[i][0],len(edited_line_grouped)+last_normal_char[i]-6,False,""])
                        elif split[splitdata].startswith("c_scroll("):
                            data = split[splitdata][len("c_scroll("):len(split[splitdata])-1].replace("(","").replace(")","").split("|")
                            data[0] = data[0].replace("%s"," ")
                            if term.width % 2 != 0:
                                if linecounter == 0:
                                    interaction_points.append([line,"Scroll",data,edited_points[i][0],last_normal_char[i]+2,False])
                                else:
                                    interaction_points.append([line,"Scroll",data,edited_points[i][0],len(" "+edited_line_grouped)+last_normal_char[i]-7,False])
                            else:
                                if linecounter == 0:
                                    interaction_points.append([line,"Scroll",data,edited_points[i][0],last_normal_char[i]+2,False,0])
                                else:
                                    interaction_points.append([line,"Scroll",data,edited_points[i][0],len(edited_line_grouped)+last_normal_char[i]-6,False])

    for i in range(enterpoint_count):
        textline = "{Enter_"+str(i)+"}"
        original_text = original_text.replace(textline, edited_points[i][4])

    #print(interaction_points)
    #print(original_text)
    original_text += term.normal + term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])
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
    

def draw_webpage():
    global webpage_limits
    draw_ui()
    y_offset = 0
    
    if in_console:
        for text in range(len(console_text)):
            text += current_console_offset
            if text < len(console_text) and y_offset < webpage_limits[3]-2:
                try:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text].format(term = term))
                except:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text])
                y_offset += 1
    elif viewing_source:
        for text in range(len(current_source_formatted)):
            text += current_source_offset
            if text < len(current_source_formatted) and y_offset < webpage_limits[3]-2:
                try:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_source_formatted[text].format(term = term))
                except:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_source_formatted[text])
                y_offset += 1
    else:
        for text in range(len(current_webpage_formatted)):
            text += current_webpage_offset
            if text < len(current_webpage_formatted) and y_offset < webpage_limits[3]-2:
                try:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text].format(term = term))
                except:
                    draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text])
                y_offset += 1
    

    update_ui(webpage_limits[1],y_offset)
    
def draw_source():
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
    global interaction_points
    global current_webpage_formatted
    
    interaction_points_copy = interaction_points.copy()
    current_source_formatted.clear()
    interaction_points.clear()
    current_webpage_formatted.clear()
    
    page = Webpage.splitlines()
    for text in range(len(page)):
        reparse_text(page[text],text)
        current_source_formatted.append(page[text])
        
    #console_print(str(interaction_points_copy))

    if last_url == Webpage:
        for x in range(len(interaction_points)):
            interaction_points[x][5] = interaction_points_copy[x][5]
            match interaction_points[x][1]:
                case "Input":
                    interaction_points[x][6] = interaction_points_copy[x][6]
                    interaction_points[x][1][0] = interaction_points_copy[x][1][0]
        
    #draw_ui()
    draw_webpage()

def load_webpage(URL):
    global interaction_points
    global locked_url
    global textbox_url
    global last_url
    core_url = URL
    if URL.startswith("--"):
        match URL.lower():
            case "--reload":
                reload_config()
                textbox_url = locked_url
                draw_text(26,2,textbox_url)
                load_webpage(textbox_url)
            case "--back":
                textbox_url = last_url
                draw_text(26,2,textbox_url)
                load_webpage(textbox_url)
                draw_webpage()
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
                with open("./Websites/"+URL.replace("/","@"), "w") as f:
                    f.write(response.text)
                reload_webpage_from_memory(response.text)
        except requests.exceptions.RequestException:
            draw_text(webpage_limits[0],webpage_limits[1],"Error Connecting to: "+ URL)
        except requests.exceptions.HTTPError:
            draw_text(webpage_limits[0],webpage_limits[1],"Error Connecting to: "+ URL)



def on_resize(sig, action):
    webpage_limits[2] = term.width-4
    webpage_limits[3] = term.height-7
    print(term.clear())

    if locked_url.startswith("$"):
        URL = locked_url[1:]
        try:
            if os.path.isfile("./"+URL):
                with open("./"+URL) as f:
                    reload_webpage_from_memory(f.read())
            else:
                raise Exception("")
        except:
            draw_ui()
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: ./"+ URL)
    else:
        if os.path.isfile("./Websites/"+locked_url.replace("/","@")):
            with open("./Websites/"+locked_url.replace("/","@")) as f:
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
                        
def link_clicked(URL):
    global editing_textbox
    global in_console
    global viewing_source
    
    editing_textbox = False
    in_console = False
    viewing_source = False
    
    load_webpage(URL)

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

    link_clicked(textbox_url)
    draw_webpage()

    while True:
        
        if editing_textbox:
            counter += 1
            if counter % 4 == 0:
                counter = 0
                
                blink_on =  not blink_on
                if blink_on:
                    blink = blink_char
                else:
                    blink = blink_alt

                draw_text(26+len(textbox_url),2,blink)
                update_ui(2,1)
                
        scroll_counter += 1
        if scroll_counter > 0:
            scroll_counter = 0
            for i in range(len(interaction_points)):
                if interaction_points[i][1] == "Scroll":
                    interaction_points[i][2][0] = interaction_points[i][2][0][-1:]+interaction_points[i][2][0][:-1]
               # interaction_points[i][2][0] = 
        update_interactive_layer()
            
        val = ''
        val = term.inkey(0.1)
        
        
        if val.is_sequence:
            match val.name:
                case "KEY_ENTER":
                    if editing_textbox:
                        current_webpage_offset = 0
                        selected_interaction_point = -1
                        link_clicked(textbox_url)
                    elif not editing_textbox and not in_console and not viewing_source and selected_interaction_point != -1:
                        match interaction_points[selected_interaction_point][1]:
                                case "Link":
                                    last_url = textbox_url
                                    current_webpage_offset = 0
                                    textbox_url = interaction_points[selected_interaction_point][2][0]
                                    draw_text(26,2,textbox_url)
                                    update_ui(2,1)
                                    link_clicked(textbox_url)
                        
                        
                case "KEY_BACKSPACE":
                    if not editing_textbox and not in_console and not viewing_source:
                        if len(interaction_points) > 0:
                            match interaction_points[selected_interaction_point][1]:
                                case "Input":
                                    interaction_points[selected_interaction_point][6] = (interaction_points[selected_interaction_point][6])[:-1]
                                    update_interactive_layer()
                                    print(term.on_color_rgb(background_color[0],background_color[1],background_color[2]) + term.color_rgb(background_color[0],background_color[1],background_color[2])+term.move_xy(interaction_points[selected_interaction_point][4]+len(interaction_points[selected_interaction_point][6])+4,interaction_points[selected_interaction_point][0]+(-1*current_webpage_offset)+6)+" ")
                    elif editing_textbox:
                        textbox_url = textbox_url[:-1]
                        draw_text(26+len(textbox_url)+1,2," ")
                        draw_text(26+len(textbox_url),2,blink_char)
                        draw_text(26,2,textbox_url)
                        update_ui(2,1)
                case "KEY_DOWN":
                    if not editing_textbox:
                        if viewing_source:
                            if current_source_offset < len(current_source_formatted):
                                current_source_offset += 1
                                draw_webpage()
                        elif in_console:
                            if current_console_offset < len(console_text):
                                current_console_offset += 1
                                draw_webpage()
                        else:
                            if current_webpage_offset < len(current_webpage_formatted):
                                current_webpage_offset += 1
                                draw_webpage()
                case "KEY_UP":
                    if not editing_textbox:
                        if viewing_source:
                            if current_source_offset != 0:
                                current_source_offset -= 1
                                draw_webpage()
                        elif in_console:
                             if current_console_offset != 0:
                                current_console_offset -= 1
                                draw_webpage()
                        else:
                            if current_webpage_offset != 0:
                                current_webpage_offset -= 1
                                draw_webpage()
                case "KEY_TAB":
                    if not editing_textbox and not in_console and not viewing_source and len(interaction_points) > 0:
                        last_interaction_point = selected_interaction_point
                        
                            
                        if last_interaction_point == -1:
                            last_interaction_point = 0
                            
                        selected_interaction_point += 1
                        
                        
                        if selected_interaction_point > len(interaction_points)-1:
                            selected_interaction_point = 0
                        
                        while interaction_points[selected_interaction_point][1] == "Scroll":
                            selected_interaction_point += 1
                        
                        if selected_interaction_point > len(interaction_points)-1:
                            selected_interaction_point = 0
                        
                        if len(interaction_points) > 1:
                            interaction_points[last_interaction_point][5] = False
                            interaction_points[selected_interaction_point][5] = True
                        elif len(interaction_points) == 1:
                            interaction_points[selected_interaction_point][5] = not interaction_points[selected_interaction_point][5]
                            #console_print(str(interaction_points[selected_interaction_point][5]))
                        
                        update_interactive_layer()
                case "KEY_F1":
                    if not editing_textbox:
                        editing_textbox = True
                    else:
                        link_clicked(textbox_url)

                case "KEY_F2":
                   if not editing_textbox:
                        viewing_source = not viewing_source
                        draw_webpage()
                case "KEY_F3":
                   if not editing_textbox:
                        in_console = not in_console
                        draw_webpage()
        elif val:
            match val:
                case "`":
                    pass

            if editing_textbox:
                textbox_url += str(val)
                draw_text(26,2,textbox_url)
                draw_text(26+len(textbox_url),2,blink_char)
                update_ui(2,1)
            
            if not in_console and not viewing_source:
                if selected_interaction_point != -1:
                    if len(interaction_points) > 0:
                        match interaction_points[selected_interaction_point][1]:
                            case "Input":
                                interaction_points[selected_interaction_point][6] += val
                                update_interactive_layer()
        