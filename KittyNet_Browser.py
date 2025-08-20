import blessed
import time
import requests
import signal
import os
import sys
launch_arguments = sys.argv

term = blessed.Terminal()

version = "0.0.1"
webpage_limits = [2,6,term.width-4,term.height-7]
current_webpage_formatted = []
current_webpage_offset = 0
textbox_url = "$Local_Sites/Boot_Readme"
locked_url = "$Local_Sites/Boot_Readme"
editing_textbox = False
original_site_response = """"""
viewing_source = False
console_text = []
current_console_offset = 0
in_console = False

if "--website" in launch_arguments:
    position = launch_arguments.index("--website")
    if position + 1 <= len(launch_arguments):
        textbox_url = launch_arguments[position + 1]
        locked_url = launch_arguments[position + 1]


if not os.path.exists("./Websites"):
    os.makedirs("./Websites")

#This is how we output text with some customizing!
def draw_text(PosX, PosY, Text, ColorOn, ColorText):
    #time.sleep(.01)
    print(term.on_color_rgb(ColorOn[0],ColorOn[1],ColorOn[2])+term.color_rgb(ColorText[0],ColorText[1],ColorText[2])+term.move_xy(PosX, PosY) + Text + term.normal)


##This is how we draw straight lines, no diagonals
def draw_line(StartX,StartY,Size, Horizontal, Color, ColorText, Text):
        if Horizontal:
            Face_String = Text * Size
            draw_text(StartX,StartY,Face_String,Color,ColorText)
        else:
            for Point in range(Size):
                draw_text(StartX,StartY+Point,Text,Color,ColorText)

##This is how we draw boxes, we can fill them too
def draw_box(PosX,PosY,SizeX,SizeY, Filled, Color, ColorText, Text):

    for y in range(SizeY):
        Face_String = ""
        if y == PosY or y == PosY + SizeY - 1:
            Face_String = Text * SizeX
        else:
            Face_String = Text+(" " * (SizeX-2))+Text

        draw_text(PosX,PosY+y,Face_String,Color,ColorText)



        #y = y + PosY
        #for x in range(SizeX):
            #x = x + PosX

            #if not Filled:
                #if x == PosX or x == PosX + SizeX - 1:
                    #if y == PosY or y == PosY + SizeY - 1:
                        #draw_line(PosX,y,term.width,True,Color,ColorText,Text)
                        #continue
                   # else:
                        #draw_text(x,y,Text,Color,ColorText)
                        #continue
                #if y == PosY or y == PosY + SizeY - 1:
                    #draw_text(x,y,Text,Color,ColorText)
                    #continue
            #else:
                #draw_text(x,y,Text,Color,ColorText)

def gen_line():
    line = ""
    for x in range(webpage_limits[2]):
        line += " "

    return line

def reparse_text(text):
    tokenized = []
    splittext = text.split(" ")
    unmodified_text = text
    text = ""
    is_centered = False
    r_fill = False
    l_fill = False
    for token in range(len(splittext)):
        if splittext[token].startswith("c_"):
            match splittext[token]:
                case "c_line":
                    tokenized.append(True)
                    splittext[token] = gen_line()
                case "c_center":
                    tokenized.append(True)
                    is_centered = True
                    splittext[token] = "{CenterPost}"
                case "c_color_reset":
                    tokenized.append(True)
                    splittext[token] = term.color_rgb(255,255,255)+term.on_color_rgb(0,0,0)
                case "c_bold":
                    tokenized.append(True)
                    splittext[token] = term.bold
                case "c_reset":
                    tokenized.append(True)
                    splittext[token] = term.normal + term.color_rgb(255,255,255)+term.on_color_rgb(0,0,0)
                case "c_underline":
                    tokenized.append(True)
                    splittext[token] = term.normal
                case "c_r_fill":
                    tokenized.append(True)
                    r_fill = True
                    splittext[token] = "{RightPost}"
                case "c_l_fill":
                    tokenized.append(True)
                    l_fill = True
                    splittext[token] = "{LeftPost}"
                case "c_space":
                    tokenized.append(True)
                    splittext[token] = " "
                case _:
                    if splittext[token].endswith(")"):
                        parse_text = splittext[token][:-1]
                        case_parse = parse_text.split(",")
                        if case_parse[0].startswith("c_on_color") and len(case_parse) == 3:
                            tokenized.append(True)
                            case_parse[0] = case_parse[0].removeprefix("c_on_color(")
                            splittext[token] = term.on_color_rgb(int(case_parse[0]),int(case_parse[1]),int(case_parse[2]))
                        elif case_parse[0].startswith("c_color") and len(case_parse) == 3:
                            tokenized.append(True)
                            case_parse[0] = case_parse[0].removeprefix("c_color(")
                            splittext[token] = term.color_rgb(int(case_parse[0]),int(case_parse[1]),int(case_parse[2]))
                        else:
                            tokenized.append(False)
                    else:
                        tokenized.append(False)


        elif splittext[token].startswith("\\c_"):
            splittext[token] = splittext[token][1:]
            tokenized.append(False)
        else:
            tokenized.append(False)

    #print(tokenized)
    clean_text = ""

    for token in range(len(splittext)):
        if token > 0:
            text += splittext[token]
        else:
            text += splittext[token]

        if not tokenized[token]:
            if token + 1 <= len(splittext)-1:
                if tokenized[token+1]:
                    pass
                else:
                    text += " "


    for token in range(len(splittext)):
        if not tokenized[token]:
            if token > 0:
                clean_text += splittext[token]
            else:
                clean_text += splittext[token]

            if not tokenized[token]:
                if token + 1 <= len(splittext)-1:
                    if tokenized[token+1]:
                        pass
                    else:
                        clean_text += " "
    if is_centered:
        text = text.format(CenterPost = gen_line()[:-(int(webpage_limits[2]/2)+int(len(clean_text)/2)+1)])
        if term.width % 2 == 0:
            text = text + " "
    if r_fill:
        text = text.format(RightPost = gen_line()[:-int(len(clean_text))])
    if l_fill:
        text = text.format(LeftPost = gen_line()[:-int(len(clean_text))])


    current_webpage_formatted.append(text)

def draw_ui():
    draw_box(0,0,term.width,term.height-1, False,[0,0,0],[255,255,255],"█")
    #draw_box(0,0,term.width,5, False,[0,0,0],[255,255,255],"█")
    #draw_box(0,0,20,5, False,[0,0,0],[255,255,255],"█")

    draw_text(2,term.height-2,"| F1:URL Bar | F2:Show Page Source | F3:Hide/Show Console |",[0,0,0],[255,255,255])
    draw_text(3,2,"KittyNet "+ version,[0,0,0],[255,255,255])
    draw_line(0, 4, term.width, True,[0,0,0],[255,255,255],"█")
    draw_line(19, 1, 3, False,[0,0,0],[255,255,255],"█")
    draw_text(22,2,"URL:",[0,0,0],[255,255,255])
    draw_text(26,2,textbox_url,[0,0,0],[255,255,255])

def draw_console():
    draw_ui()
    y_offset = 0
    for text in range(len(console_text)):
        text += current_console_offset
        if text < len(console_text) and y_offset < webpage_limits[3]-2:
            try:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text].format(term = term),[0,0,0],[255,255,255])
            except:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,console_text[text],[0,0,0],[255,255,255])
            y_offset += 1

def draw_webpage():
    draw_ui()
    y_offset = 0
    for text in range(len(current_webpage_formatted)):
        text += current_webpage_offset
        if text < len(current_webpage_formatted) and y_offset < webpage_limits[3]-2:

            try:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text].format(term = term),[0,0,0],[255,255,255])
            except:
                draw_text(webpage_limits[0],webpage_limits[1]+y_offset,current_webpage_formatted[text],[0,0,0],[255,255,255])
            y_offset += 1


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

    if URL.startswith("$"):
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
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: ./"+ URL,[0,0,0],[255,255,255])

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
            draw_text(webpage_limits[0],webpage_limits[1],"Error Connecting to: "+ URL,[0,0,0],[255,255,255])
        except requests.exceptions.HTTPError:
            print("Failed")



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
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: ./"+ URL,[0,0,0],[255,255,255])
    else:
        if os.path.isfile("./Websites/"+locked_url):
            with open("./Websites/"+locked_url) as f:
                if viewing_source:
                    reload_source_from_memory(f.read())
                else:
                    reload_webpage_from_memory(f.read())
        else:
            draw_ui()
            draw_text(webpage_limits[0],webpage_limits[1],"Error Path Invalid: http://"+ locked_url,[0,0,0],[255,255,255])

def console_print(Text):
    console_text.append(Text)

with term.fullscreen(), term.hidden_cursor(), term.cbreak():

    console_print("!!!KittyNet Console!!!")
    console_print("---")
    console_print("KittyNet Version "+ version)
    console_print("Copyright Duskitten 2025")
    console_print("Distributed under MIT License")
    console_print("---")

    signal.signal(signal.SIGWINCH, on_resize)
    tested = False
    x = 0

    load_webpage(textbox_url)

    while True:
        val = ''
        val = term.inkey()

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
                        draw_text(26+len(textbox_url),2," ",[0,0,0],[255,255,255])
                        draw_text(26,2,textbox_url,[0,0,0],[255,255,255])
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
                draw_text(26,2,textbox_url,[0,0,0],[255,255,255])
            else:
                pass


