from enum import Enum
from array import array
import blessed
import time
import requests
import signal
import os
import sys

launch_arguments = sys.argv
term = blessed.Terminal()
version = "0.1.0"
script_directory = os.path.dirname(os.path.abspath(__file__))

RYB_Colors = {
    "black":[0,0,0],
    "white":[255,255,255],
    
    "dark_gray":[77,77,77],
    "dark_red":[163,15,1],
    "dark_red_orange":[155, 57, 2],
    "dark_orange":[151,92,1],
    "dark_yellow_orange":[165,130,2],
    "dark_yellow":[182,182,1],
    "dark_yellow_green":[109,133,26],
    "dark_green":[61,106,30],
    "dark_blue_green":[31,74,91],
    "dark_blue":[1,41,153],
    "dark_blue_purple":[42,22,128],
    "dark_purple":[82,1,105],
    "dark_red_purple":[116,12,56],
    
    "gray":[128,128,128],
    "red":[254, 39, 18],
    "red_orange":[252, 96, 10],
    "orange":[251, 153, 2],
    "yellow_orange":[252, 204, 26],
    "yellow":[254, 254, 51],
    "yellow_green":[178, 215, 50],
    "green":[102, 176, 50],
    "blue_green":[52, 124, 152],
    "blue":[2, 71, 254],
    "blue_purple":[68, 36, 214],
    "purple":[134, 1, 175],
    "red_purple":[194, 20, 96],
    
    "pastel_gray":[179,179,179],
    "pastel_red":[254,125,113],
    "pastel_red_orange":[253,160,108],
    "pastel_orange":[254,194,102],
    "pastel_yellow_orange":[253,225,118],
    "pastel_yellow":[254,254,133],
    "pastel_yellow_green":[208,231,132],
    "pastel_green":[161,217,122],
    "pastel_blue_green":[118,182,208],
    "pastel_blue":[103,143,254],
    "pastel_blue_purple":[143,121,233],
    "pastel_purple":[210,56,254],
    "pastel_red_purple":[238,94,155],
    }

command_tags = [
    "no_align",
    "right",
    "left",
    "center",
    "color",
    "oncolor",
    "scroll",
    "link",
    "input",
    "underline",
    "bold",
    "blink",
    "background",
    "foreground"

]

config_data = {
    #Colors
    "default_background_color":"black",
    "default_foreground_color":"white",

    "default_link_foreground":"blue",
    "default_link_background":"default",
    "default_hover_link_foreground":"default",
    "default_hover_link_background":"blue",


    #UI
    "use_panels":False,
    "use_custom_char":"█",

    #Navigation
    "key_scroll_up":"up",
    "key_scroll_down":"down",
    "key_toggle_urlbar":"f1",
    "key_toggle_source":"f2",
    "key_toggle_console":"f3",
    "key_toggle_back":"f4",
    "key_toggle_reload":"f5",
    "key_interact=enter":"enter",

    #Bootup
    "homepage":"$Local_Sites/Boot_Readme"
    }

##Website Stuff
current_url = ""
url_history = []
current_site = ""
current_parsed_page = []
scroll_offset = 0

##Prebuilt variables
url_text = "  URL:"+current_url
kitty_text = ""
edge_text =  ""
keybinds_text = ""
full_line = ""
sectioned_line = ""
kitty_line = ""
fill_line = ""
default_colors = ""

viewport_size = [3,6]

class viewport(Enum):
    default = 0
    url = 1
    source = 2
    console = 3
    
viewport_mode = 0

def on_resize(sig, action):
    redraw()

signal.signal(signal.SIGWINCH, on_resize)

def color_test():
    values = list(RYB_Colors)
    compiled_string = ""
    for y in range(len(values)):
        if y == 2:
            compiled_string += term.move_xy(3,8)
        elif y == 15:
            compiled_string += term.move_xy(3,10)
        elif y == 28:
            compiled_string += term.move_xy(3,12)
        compiled_string += str(compile_color(str(values[y]),"oncolor_"))+"  "
        
        
    return str(term.move_xy(2,6) + compiled_string +term.normal)

def compile_color(input_color,color_type):
    global command_tags

    if not input_color in [*RYB_Colors] and input_color != "default":
        return("")

    match color_type:
        case "color":
            if input_color == "default":
                return term.color_rgb(RYB_Colors[config_data["default_foreground_color"]][0],RYB_Colors[config_data["default_foreground_color"]][1],RYB_Colors[config_data["default_foreground_color"]][2])
            else:
                return term.color_rgb(RYB_Colors[input_color][0],RYB_Colors[input_color][1],RYB_Colors[input_color][2])
        case "oncolor":
            if input_color == "default":
                return term.on_color_rgb(RYB_Colors[config_data["default_background_color"]][0],RYB_Colors[config_data["default_background_color"]][1],RYB_Colors[config_data["default_background_color"]][2])
            else:
                return term.on_color_rgb(RYB_Colors[input_color][0],RYB_Colors[input_color][1],RYB_Colors[input_color][2])

def redraw():
    global keybinds_text
    global kitty_text
    global edge_text
    global full_line 
    global sectioned_line
    global kitty_line
    global fill_line
    global config_data
    
    compiled_line = default_colors
    
    
    if config_data["use_panels"]:
        keybinds_text = "┤ F1:URL Bar | F2:Toggle Source | F3:Toggle Console | F4:Back Page | F5:Reload Page ├"
        kitty_text = "  KittyNet "+version+"  │"  
        edge_text =  " " * (len(kitty_text)-1) +"│"
        full_line = "─" * (term.width)
        sectioned_line = "│" + (" " * (term.width -2))+"│"
        kitty_line = "│"+kitty_text + (" " * (term.width -2 -len(kitty_text)))+"│"
        fill_line = "│"+edge_text + (" " * (term.width -2 -len(edge_text)))+"│"
    else:
        keybinds_text = config_data["use_custom_char"]+" F1:URL Bar | F2:Toggle Source | F3:Toggle Console | F4:Back Page | F5:Reload Page "+config_data["use_custom_char"]
        kitty_text = "  KittyNet "+version+"  "+config_data["use_custom_char"]
        edge_text =  " " * (len(kitty_text)-1) +config_data["use_custom_char"]
        full_line = config_data["use_custom_char"] * term.width
        sectioned_line = config_data["use_custom_char"]+ (" " * (term.width -2))+config_data["use_custom_char"]
        kitty_line = config_data["use_custom_char"]+kitty_text + (" " * (term.width -2 -len(kitty_text)))+config_data["use_custom_char"]
        fill_line = config_data["use_custom_char"]+edge_text + (" " * (term.width -2 -len(edge_text)))+config_data["use_custom_char"]
    
    for Y in range(term.height):
        if Y == 0 or Y == term.height-1 or Y == 4:
            compiled_line += term.move_xy(0,Y)+full_line
        elif Y == 2:
            compiled_line += term.move_xy(0,Y) + kitty_line
        elif Y == 1 or Y == 3:
            compiled_line += term.move_xy(0,Y)+fill_line
        else:
            compiled_line += sectioned_line
            
    compiled_line += term.move_xy(3,term.height-1)+keybinds_text
    # ┐└ ┘ ┌ ┴ ┬ │ ─ ┼ ┤ ├
    if config_data["use_panels"]:
        compiled_line += term.move_xy(0,0)+"┌"
        compiled_line += term.move_xy(0,4)+"├"
        compiled_line += term.move_xy(term.width-1,0)+"┐"
        compiled_line += term.move_xy(len(kitty_text),0)+"┬"
        compiled_line += term.move_xy(len(kitty_text),4)+"┴"
        compiled_line += term.move_xy(0,term.height-1)+"└"
        compiled_line += term.move_xy(term.width-1,4)+"┤"
        compiled_line += term.move_xy(term.width-1,term.height-1)+"┘"
        
    compiled_line += term.move_xy(len(kitty_text)+2,2)+url_text
    
    #compiled_line+=color_test()
    
    print(compiled_line)
    
def initial_setup():
    global default_colors
    if os.path.exists(script_directory+"/KittyNet.config"):
        with open(script_directory+"/KittyNet.config") as f:
            thisfile = f.read()
            splitfile = thisfile.splitlines()
            for x in splitfile:
                if (not (x.startswith("#") or x.startswith("@"))) and len(x) > 0:
                    data = x.split("=")
                    if data[1].lower() == "true":
                        config_data[data[0]] = True
                        print(data[1])
                    elif data[1].lower() == "false":
                        config_data[data[0]] = False
                        
                    else:
                        config_data[data[0]] = data[1]

    default_colors = compile_color("default",command_tags[4])+compile_color("default",command_tags[5])

def parse_url():
    global current_url

    if current_url.startswith("$"):
        new_text = current_url.replace("$","./")
        if os.path.isfile(new_text):
            with open(new_text) as f:
                parse_manager(f.read())

    elif url_text.startswith("--"):
        ###Command URL
        pass
    elif url_text.startswith("!"):
        ###Config URL
        pass
    else:
        ###Regular Url
        pass

def parse_manager(currentpage):
    for x in currentpage.splitlines():
        parse_by_line(x)

    parse_display()


def parse_display():
    global current_parsed_page
    global scroll_offset

    total_line = term.move_xy(3,5)+default_colors
    parse_offset = 0
    current_text = ""
    for x in range(len(current_parsed_page)):
        x += scroll_offset
        if x < len(current_parsed_page):
            current_text =  current_parsed_page[x]["empty_text"]
            if parse_offset+6 > term.height - 3:
                break
        else:
            total_line += term.move_xy(3,6+parse_offset)+  (" " * ((term.width - 6)))
            break

        patch_left = ""
        patch_right = ""
        match current_parsed_page[x]["alignment"]:
            case "left":
                patch_right = " " * ((term.width - 6) - len(current_text))
            case "right":
                patch_left = " " * ((term.width - 6) - len(current_text))
            case "center":
                patch_right = " " * int(((term.width - 6) - len(current_text))/2)
                if term.width % 2 != 0 or len(current_text) % 2 != 0:
                    patch_left = " " * int(((term.width - 6) - len(current_text))/2) + " "
                else:
                    patch_left = " " * int(((term.width - 6) - len(current_text))/2)

        #print(current_parsed_page[x]["alignment"])
        total_line += term.move_xy(3,6+parse_offset) + current_parsed_page[x]["stripped_text"].replace("{left_point}",patch_left).replace("{right_point}",patch_right)+ default_colors
        parse_offset += 1

    #total_line += term.move_xy(3,6+parse_offset)+  (" " * ((term.width - 6)))
    #print(current_parsed_page[x]["stripped_text"])
    print(total_line)


def parse_by_line(textline):
    global current_parsed_page
    return_text = ""
    modded_text = textline
    stripped_text = textline
    empty_text = textline
    codes = []
    ModPoint = 0
    has_set_adjustment = False
    alignment = "left"

    for x in range(len(modded_text)):
        char = modded_text[x]
        if char == "[" and modded_text[x-1] != "\\":
            position = 0
            for i in range(len(modded_text)-x):
                i+=1
                if modded_text[x + i] == "]":
                    position = i+1
                    key = "{Key_"+str(ModPoint)+"}"
                    codes.append([ModPoint,x,modded_text[x:x + position],key,""])
                    if ModPoint != 0:
                        stripped_text = stripped_text.replace(modded_text[x:x + position],key,1)
                    else:
                        stripped_text = stripped_text.replace(modded_text[x:x + position],key+"{left_point}",1)
                    empty_text = empty_text.replace(modded_text[x:x+position],"",1)
                    ModPoint += 1
                    #return_text += str(modded_text[x:x + position]) +"\n"
                    #print(default_colors+modded_text[x + i])
                    break


    if empty_text == "":
        stripped_text += " "*(term.width - 6)

    if ModPoint == 0:
        stripped_text = "{left_point}"+stripped_text





    for i in range(len(codes)):
        current_code = codes[i][2].replace("[","").replace("]","").lower().split(" ")
        for x in current_code:
            x = x.split("_")
            match x[0]:
                case "left":
                    if not has_set_adjustment:
                        #print("hai!")
                        has_set_adjustment = True
                        alignment = x[0]
                case "right":
                    if not has_set_adjustment:
                        #print("hai!")
                        has_set_adjustment = True
                        alignment = x[0]
                case "center":
                    if not has_set_adjustment:
                        #print("hai!")
                        has_set_adjustment = True
                        alignment = x[0]
                case "color":
                    codes[i][4] += compile_color(x[1],x[0])
                case "oncolor":
                    codes[i][4] += compile_color(x[1],x[0])

        stripped_text = stripped_text.replace(codes[i][3],codes[i][4])


    if empty_text.replace(" ","") == "":
        empty_text = " " * (term.width -6)

    current_parsed_page.append({
        "original":textline,
        "codes":codes,
        "stripped_text": stripped_text+"{right_point}",
        "empty_text":empty_text,
        "alignment":alignment
        })

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def input_check(value):
    global scroll_offset
    global viewport_mode
    global current_url
    
    if viewport_mode == viewport.url:
        if value == config_data["key_interact"]:
            viewport_mode = viewport.default
            current_parsed_page.clear()
            parse_url()
            return
        elif value == "backspace":
            current_url = current_url[:-1]
            url_text = "  URL:"+current_url+" "
        else:
            if len(value) == 1:
                current_url += value
                url_text = "  URL:"+current_url
            else:
                return
        

        print(compiled_line)
        return
        
    
    
    
    
    if value == config_data["key_scroll_up"]:
        if viewport_mode == viewport.default:
            if scroll_offset > 0:
                scroll_offset = clamp(scroll_offset - 1,0,999999999)
                parse_display()
        #print(value)
    elif value == config_data["key_scroll_down"]:
        if viewport_mode == viewport.default:
            if len(current_parsed_page) >= term.height - 8:
                scroll_offset = clamp(scroll_offset + 1,0,len(current_parsed_page))
                parse_display()
        #print(value)
    elif value == config_data["key_toggle_urlbar"]:
        if viewport_mode != viewport.url:
            viewport_mode = viewport.url
    elif value == config_data["key_toggle_source"]:
        pass
        #print(value)
    elif value == config_data["key_toggle_console"]:
        pass
        #print(value)
    elif value == config_data["key_toggle_back"]:
        pass
        #print(value)
    elif value == config_data["key_toggle_reload"]:
        pass
        #print(value)

with term.cbreak(), term.hidden_cursor(), term.fullscreen():
    initial_setup()

    viewport_mode = viewport.default
    current_url = config_data["homepage"]
    url_text = "  URL:"+current_url+" "
    redraw()
    parse_url()
    while True:
        value = ""
        keyval = term.inkey(timeout=.1)
        if keyval:
            if keyval.is_sequence:
                value = keyval.name.replace("KEY_","").lower()
            else:
                value = keyval
           
            input_check(value)
                
            
            
