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
    
    "dark-gray":[77,77,77],
    "dark-red":[163,15,1],
    "dark-red-orange":[155, 57, 2],
    "dark-orange":[151,92,1],
    "dark-yellow-orange":[165,130,2],
    "dark-yellow":[182,182,1],
    "dark-yellow-green":[109,133,26],
    "dark-green":[61,106,30],
    "dark-blue-green":[31,74,91],
    "dark-blue":[1,41,153],
    "dark-blue-purple":[42,22,128],
    "dark-purple":[82,1,105],
    "dark-red-purple":[116,12,56],
    
    "gray":[128,128,128],
    "red":[254, 39, 18],
    "red-orange":[252, 96, 10],
    "orange":[251, 153, 2],
    "yellow-orange":[252, 204, 26],
    "yellow":[254, 254, 51],
    "yellow-green":[178, 215, 50],
    "green":[102, 176, 50],
    "blue-green":[52, 124, 152],
    "blue":[2, 71, 254],
    "blue-purple":[68, 36, 214],
    "purple":[134, 1, 175],
    "red-purple":[194, 20, 96],
    
    "pastel-gray":[179,179,179],
    "pastel-red":[254,125,113],
    "pastel-red-orange":[253,160,108],
    "pastel-orange":[254,194,102],
    "pastel-yellow-orange":[253,225,118],
    "pastel-yellow":[254,254,133],
    "pastel-yellow-green":[208,231,132],
    "pastel-green":[161,217,122],
    "pastel-blue-green":[118,182,208],
    "pastel-blue":[103,143,254],
    "pastel-blue-purple":[143,121,233],
    "pastel-purple":[210,56,254],
    "pastel-red-purple":[238,94,155],
    }

command_tags = [
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

    "default_webpage_color":"default",
    "default_webpage_background_color":"default",
    
    "default_link_foreground":"blue",
    "default_link_background":"default",
    "default_hover_link_foreground":"default",
    "default_hover_link_background":"blue",
    
    "default_input_foreground":"white",
    "default_input_background":"default",
    "default_hover_input_foreground":"white",
    "default_hover_input_background":"dark-gray",


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
    "key_toggle_next_element":">",
    "key_toggle_prev_element":"<",

    #Bootup
    "homepage":"$Local_Sites/Boot_Readme"
    }

##Website Stuff
current_url = ""
url_history = []
current_site = ""
current_parsed_page = []
scroll_offset = 0
interaction_point = 0
interaction_points = []
scroll_points = []
link_colors = []
input_colors = []
input_hovered = False
current_page_foreground = ""
current_page_background = ""

##Source
current_source = []
source_scroll_offset = 0

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
default_web_colors = ""

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
    global current_page_background
    global current_page_foreground

    if (not input_color in [*RYB_Colors]) and input_color != "default" and input_color != "page-color":
        return("")

    match color_type:
        case "color":
            if input_color == "default":
                return term.color_rgb(RYB_Colors[config_data["default_foreground_color"]][0],RYB_Colors[config_data["default_foreground_color"]][1],RYB_Colors[config_data["default_foreground_color"]][2])
            elif input_color == "web-default":
                return term.color_rgb(RYB_Colors[config_data["default_webpage_color"]][0],RYB_Colors[config_data["default_webpage_color"]][1],RYB_Colors[config_data["default_webpage_color"]][2])
            elif input_color == "page-color":
                return current_page_foreground
            else:
                return term.color_rgb(RYB_Colors[input_color][0],RYB_Colors[input_color][1],RYB_Colors[input_color][2])
        case "oncolor":
            if input_color == "default":
                return term.on_color_rgb(RYB_Colors[config_data["default_background_color"]][0],RYB_Colors[config_data["default_background_color"]][1],RYB_Colors[config_data["default_background_color"]][2])
            elif input_color == "web-default":
                return term.on_color_rgb(RYB_Colors[config_data["default_webpage_background_color"]][0],RYB_Colors[config_data["default_webpage_background_color"]][1],RYB_Colors[config_data["default_webpage_background_color"]][2])
            elif input_color == "page-color":
                return current_page_background
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
    global url_text
    global current_url
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
        
    compiled_line += term.move_xy(len(kitty_text)+2,2)+"  URL:"+current_url
    
    #compiled_line+=color_test()
    
    print(compiled_line)
    
def initial_setup():
    global config_data
    global default_colors
    global link_colors
    global default_web_colors   
    global input_colors
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

    default_colors = compile_color("default",command_tags[3])+compile_color("default",command_tags[4])
    default_web_colors = compile_color(config_data["default_webpage_color"],command_tags[3])+compile_color(config_data["default_webpage_background_color"],command_tags[4])
    link_colors = [
        compile_color(config_data["default_link_foreground"],command_tags[3]),
        compile_color(config_data["default_link_background"],command_tags[4]),
        compile_color(config_data["default_hover_link_foreground"],command_tags[3]),
        compile_color(config_data["default_hover_link_background"],command_tags[4])
        ] 

    input_colors = [
        compile_color(config_data["default_input_foreground"],command_tags[3]),
        compile_color(config_data["default_input_background"],command_tags[4]),
        compile_color(config_data["default_hover_input_foreground"],command_tags[3]),
        compile_color(config_data["default_hover_input_background"],command_tags[4])
        ] 
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
        
        try:
            r = requests.get('http://'+current_url, timeout=2)
            parse_manager(r.text)
            #print(r.text)
        except:
            print("Ack!")

def parse_manager(currentpage):
    global scroll_points
    global interaction_points
    global current_parsed_page
    global current_page_foreground
    global current_page_background
    global interaction_point
    global scroll_offset
    redraw()
    scroll_offset = 0
    interaction_point = 0
    scroll_points.clear()
    current_source.clear()
    interaction_points.clear()
    current_parsed_page.clear()
    current_page_foreground = ""
    current_page_background = ""
    
    for x in currentpage.splitlines():
        parse_by_line(x)

    parse_display()


def parse_display():
    global current_parsed_page
    global scroll_offset
    global scroll_points
    global link_points
    global link_colors
    global default_web_colors
    global current_page_foreground
    global current_page_foreground
    global input_colors
    global viewport_mode
    
    if viewport_mode == viewport.default:
    
        selected_color = default_web_colors + current_page_foreground + current_page_background

        total_line = term.move_xy(3,5)+selected_color
        parse_offset = 0
        current_text = ""
        
        
        
        for x in range(len(current_parsed_page)):
            x += scroll_offset
            if x < len(current_parsed_page):
                current_text =  current_parsed_page[x]["empty_text"]
                if parse_offset+6 > term.height - 3:
                    break
            else:
                #total_line += term.move_xy(3,6+parse_offset)+  (" " * ((term.width - 6)))
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
            total_line += term.move_xy(3,6+parse_offset) + current_parsed_page[x]["stripped_text"].replace("{left_point}",patch_left).replace("{right_point}",patch_right)+ selected_color
            
            for y in range(len(scroll_points)):
                if scroll_points[y][0]-1 == x:
                    point_a = scroll_points[y][0]-1
                    point_b = scroll_points[y][1]
                    scroll_object = current_parsed_page[point_a]["codes"][point_b]
                #print(len(current_parsed_page[point_a]["codes"][point_b]))
                    if "scrolled_text" in scroll_object[5]:
                    #print("Hai")
                        total_line += term.move_xy(len(patch_left)+3+scroll_object[5]["scroll_pos"][0] ,6+parse_offset) + scroll_object[4] +scroll_object[5]["scrolled_text"] +selected_color
            
            for y in range(len(interaction_points)):
                if interaction_points[y][0]-1 == x:
                    point_a = interaction_points[y][0]-1
                    point_b = interaction_points[y][1]
                    link_object = current_parsed_page[point_a]["codes"][point_b]
                    if "link_text" in link_object[5]:
                        if y == interaction_point:
                            total_line += term.move_xy(len(patch_left)+3+link_object[5]["link_pos"][0] ,6+parse_offset)+term.underline + link_colors[2] + link_colors[3] + link_object[4] + link_object[5]["link_text"] +selected_color+term.no_underline
                        else:
                            total_line += term.move_xy(len(patch_left)+3+link_object[5]["link_pos"][0] ,6+parse_offset)+term.underline + link_colors[0] + link_colors[1] + link_object[4] + link_object[5]["link_text"] +selected_color+term.no_underline
                    elif "input_text" in link_object[5]:
                        if y == interaction_point:
                            total_line += term.move_xy(len(patch_left)+3+link_object[5]["input_pos"][0] ,6+parse_offset)+term.underline + input_colors[2] + input_colors[3] + link_object[4] + link_object[5]["input_text"] +link_object[5]["input_typed"] +selected_color+term.no_underline
                        else:
                            total_line += term.move_xy(len(patch_left)+3+link_object[5]["input_pos"][0] ,6+parse_offset)+term.underline + input_colors[0] + input_colors[1] + link_object[4] + link_object[5]["input_text"] +link_object[5]["input_typed"] +selected_color+term.no_underline
                    
                
            parse_offset += 1
            
        if parse_offset < (term.height-8):
            original_offset = parse_offset
            patch_left = " " * ((term.width - 6))
            for x in range((term.height-8)-parse_offset):
                x += original_offset
                total_line += term.move_xy(3 ,6+x)+ patch_left +selected_color+term.no_underline
        #total_line += term.move_xy(3,6+parse_offset)+  (" " * ((term.width - 6)))
        #print(current_parsed_page[x]["stripped_text"])
        print(total_line)
    elif viewport_mode == viewport.source:
        total_line = default_colors
        for i in range(len(current_source)):
            x = i + scroll_offset
            if i < (term.height-8):
                total_line += term.move_xy(3 ,6+i)+ current_source[x] + (" " * ((term.width - 6) - len(current_source[x])))
            
        hold_text = (" " * (term.width - 6))
        if len(current_source) < term.height - 8:
            total_extra = (term.height-8)-len(current_source)
            for i in range(total_extra):
                total_line += term.move_xy(3 ,6+len(current_source)+i)+hold_text
            
        print(total_line)


def parse_by_line(textline):
    global current_source
    global scroll_points
    global current_parsed_page
    global current_page_foreground
    global current_page_background
    
    current_source.append(textline)
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
                if len(modded_text) > x+i:
                    if modded_text[x + i] == "]":
                        position = i+1
                        key = "{Key_"+str(ModPoint)+"}"
                        
                        if ModPoint != 0:
                            stripped_text = stripped_text.replace(modded_text[x:x + position],key,1)
                        else:
                            stripped_text = stripped_text.replace(modded_text[x:x + position],key+"{left_point}",1)
                            
                        y = empty_text.find(modded_text[x:x+position])
                        empty_text = empty_text.replace(modded_text[x:x+position],"",1)
                        codes.append([ModPoint,x,modded_text[x:x + position],key,"",{},y])
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
                case "scroll":
                    codes[i][5]["scroll_pos"] = []
                    if len(codes) > i+1:
                        codes[i][5]["scroll_pos"] = [codes[i][6], codes[i+1][6]]
                    else:
                        codes[i][5]["scroll_pos"] = [codes[i][6], codes[i][6]+len(empty_text[codes[i][6]:])]
                    
                    codes[i][5]["scrolled_text"] = empty_text[codes[i][5]["scroll_pos"][0]:codes[i][5]["scroll_pos"][1]]
                    scroll_points.append([len(current_parsed_page)+1,i])
                case "link":
                    codes[i][5]["link_pos"] = []
                    if len(codes) > i+1:
                        codes[i][5]["link_pos"] = [codes[i][6], codes[i+1][6]]
                    else:
                        codes[i][5]["link_pos"] = [codes[i][6], codes[i][6]+len(empty_text[codes[i][6]:])]
                    
                    if len(x) > 1:
                        codes[i][5]["linked_tags"] = x[1].split(",")
                    codes[i][5]["link_text"] = empty_text[codes[i][5]["link_pos"][0]:codes[i][5]["link_pos"][1]]
                    interaction_points.append([len(current_parsed_page)+1,i])
                case "input":
                    codes[i][5]["input_pos"] = []
                    codes[i][5]["input_typed"] = ""
                    if len(codes) > i+1:
                        codes[i][5]["input_pos"] = [codes[i][6], codes[i+1][6]]
                    else:
                        codes[i][5]["input_pos"] = [codes[i][6], codes[i][6]+len(empty_text[codes[i][6]:])]
                        
                    if len(x) > 1:
                        codes[i][5]["input_tag"] = x[1].split(",")[0]
                        codes[i][5]["input_length"] = int(x[1].split(",")[1])
                        
                    codes[i][5]["input_text"] = empty_text[codes[i][5]["input_pos"][0]:codes[i][5]["input_pos"][1]]
                    interaction_points.append([len(current_parsed_page)+1,i])
                case "foreground":
                    if len(current_parsed_page) == 0:
                        current_page_foreground = compile_color(x[1],command_tags[3])
                case "background":
                    if len(current_parsed_page) == 0:
                        current_page_background = compile_color(x[1],command_tags[4])

        stripped_text = stripped_text.replace(codes[i][3],codes[i][4])


    if empty_text.replace(" ","") == "":
        empty_text = " " * (term.width -6)
    
    
    current_parsed_page.append({
        "original":textline,
        "codes":codes.copy(),
        "stripped_text": stripped_text+"{right_point}",
        "empty_text":empty_text,
        "alignment":alignment
        })

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def input_check(value):
    global scroll_offset
    global viewport_mode
    global current_url
    global link_points
    global interaction_point
    global default_colors
    
    
    is_input = False
    if len(interaction_points) > 0:
        point_a = interaction_points[interaction_point][0]-1
        point_b = interaction_points[interaction_point][1]
        link_point = current_parsed_page[point_a]["codes"][point_b]
        if "input_text" in link_point[5]:
            is_input = True
            

    if value == config_data["key_scroll_up"]:
        if scroll_offset > 0:
            scroll_offset = clamp(scroll_offset - 1,0,999999999)
            parse_display()
        #print(value)
    elif value == config_data["key_scroll_down"]:
        if len(current_parsed_page) >= term.height - 8 +1 + scroll_offset:
            scroll_offset = clamp(scroll_offset + 1,0,len(current_parsed_page))
            parse_display()
        #print(value)
    elif value == config_data["key_toggle_urlbar"]:
        if viewport_mode != viewport.url:
            viewport_mode = viewport.url
    elif value == config_data["key_toggle_source"]:
        if viewport_mode != viewport.source:
            viewport_mode = viewport.source
            parse_display()
        elif viewport_mode == viewport.source:
            viewport_mode = viewport.default
        #print(value)
    elif value == config_data["key_toggle_console"]:
        if viewport_mode != viewport.console:
            viewport_mode = viewport.console
        elif viewport_mode == viewport.console:
            viewport_mode = viewport.default
        #print(value)
    elif value == config_data["key_toggle_back"]:
        pass
        #print(value)
    elif value == config_data["key_toggle_reload"]:
        pass
    elif value == config_data["key_toggle_next_element"]:
        if viewport_mode == viewport.default:
            interaction_point += 1
            if interaction_point >= len(interaction_points):
                interaction_point = 0
            parse_display()
    elif value == config_data["key_toggle_prev_element"]:
        #print(value)
        if viewport_mode == viewport.default:
            interaction_point -= 1
            if interaction_point < 0:
                interaction_point = len(interaction_points)-1
            parse_display()
            
        #print(value)
    elif value == config_data["key_interact"]:
        if viewport_mode == viewport.default and len(interaction_points) > 0:
            point_a = interaction_points[interaction_point][0]-1
            point_b = interaction_points[interaction_point][1]
            link_object = current_parsed_page[point_a]["codes"][point_b]
            if "link_text" in link_object[5]:
                old_url_len = len(current_url)
                compile_params = ""
                
                if "linked_tags" in link_object[5]:
                    compile_params = "/"
                    for x in range(len(link_object[5]["linked_tags"])):
                        if x == 0:
                            compile_params += "?"
                        else:
                            compile_params += "&"
                        this_tag = link_object[5]["linked_tags"][x]+"="
                        compile_params += this_tag
                        for y in range(len(interaction_points)):
                            point_a_2 = interaction_points[y][0]-1
                            point_b_2 = interaction_points[y][1]
                            link_point_2 = current_parsed_page[point_a_2]["codes"][point_b_2]
                            if "input_text" in link_point_2[5] and "linked_tags" in link_point_2[5] and (link_object[5]["linked_tags"][x] in link_point_2[5]["linked_tags"]):
                                compile_params += link_point_2[5]["input_text"]+" "
                                    
                current_url = link_object[5]["link_text"]+compile_params
                url_text = default_colors+"  URL:"+(" " * clamp(old_url_len - len(current_url),0,9999999999999))
                #compiled_line = term.move_xy(len(kitty_text)+2,2)+url_text
                #print(compiled_line)
                parse_url()
        elif viewport_mode == viewport.url:
            viewport_mode = viewport.default
            #current_parsed_page.clear()
            parse_url()
            url_text = "  URL:"+current_url
            compiled_line = term.move_xy(len(kitty_text)+2,2)+default_colors+url_text
            print(compiled_line)
            return
    elif value == "backspace":
        if viewport_mode == viewport.url:
            current_url = current_url[:-1]
            url_text = "  URL:"+current_url+" "
            compiled_line = term.move_xy(len(kitty_text)+2,2)+default_colors+url_text
            print(compiled_line)
        elif viewport_mode == viewport.default:
            if is_input:
                link_point[5]["input_typed"] = link_point[5]["input_typed"][:-1]
                parse_display()
    else:
        if viewport_mode == viewport.url:
            if len(value) == 1:
                current_url += value
                url_text = "  URL:"+current_url
                compiled_line = term.move_xy(len(kitty_text)+2,2)+default_colors+url_text
                print(compiled_line)
        elif viewport_mode == viewport.default:
            if is_input and len(value) == 1:
                if len(link_point[5]["input_typed"]) < link_point[5]["input_length"]:
                    link_point[5]["input_typed"] += value
                    parse_display()
                
                        
            

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
                
        
        for x in range(len(scroll_points)):
            point_a = scroll_points[x][0]-1
            point_b = scroll_points[x][1]
            link_point = current_parsed_page[point_a]["codes"][point_b]
            #print(current_parsed_page[point_a])
            if "scrolled_text" in link_point[5]:
                link_point[5]["scrolled_text"] = link_point[5]["scrolled_text"][-1] + link_point[5]["scrolled_text"][:-1]
                    #print(current_parsed_page[x]["codes"][z][5]["scrolled_text"])
                    
        parse_display()
