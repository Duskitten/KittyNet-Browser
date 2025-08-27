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
    "color_",
    "no_color",
    "oncolor_",
    "no_oncolor",
    "scroll",
    "no_scroll",
    "link",
    "no_link",
    "input",
    "no_input",
    "underline",
    "no_underline",
    "bold",
    "no_bold",
    "blink",
    "no_blink"
]

config_data = {
    #Colors
    "default_background_color":"black",
    "default_foreground_color":"white",

    #UI
    "use_panels":False,
    "use_custom_char":"█",

    #Navigation
    "scroll_up":"up",
    "scroll_down":"down",
    "toggle_urlbar":"f1",
    "toggle_source":"f2",
    "toggle_console":"f3",
    "toggle_back":"f4",
    "toggle_reload":"f5"
    
    }
def on_resize(sig, action):
    redraw()

signal.signal(signal.SIGWINCH, on_resize)

def color_test():
    values = list(RYB_Colors)
    compiled_string = ""
    for y in range(len(values)):
        if y == 2:
         compiled_string += term.move_xy(2,9)
        elif y == 15:
             compiled_string += term.move_xy(2,11)
        elif y == 28:
             compiled_string += term.move_xy(2,13)
        compiled_string += str(compile_color(str(values[y]),"oncolor_"))+"  "
        
        
    print(term.move_xy(2,7) + compiled_string)
        

def compile_color(input_color,color_type):
    global command_tags
    match color_type:
        case "color_":
            return term.color_rgb(RYB_Colors[input_color][0],RYB_Colors[input_color][1],RYB_Colors[input_color][2])
        case "oncolor_":
            return term.on_color_rgb(RYB_Colors[input_color][0],RYB_Colors[input_color][1],RYB_Colors[input_color][2])
        case "no_oncolor":
            return term.on_color_rgb(RYB_Colors[config_data["default_background_color"]][0],RYB_Colors[config_data["default_background_color"]][1],RYB_Colors[config_data["default_background_color"]][2])
        case "no_color":
            return term.color_rgb(RYB_Colors[config_data["default_foreground_color"]][0],RYB_Colors[config_data["default_foreground_color"]][1],RYB_Colors[config_data["default_foreground_color"]][2])

def redraw():
    default_colors = compile_color("",command_tags[5])+compile_color("",command_tags[7])
    compiled_line = default_colors
    kitty_text = ""
    edge_text =  ""
    keybinds_text = ""
    full_line = ""
    sectioned_line = ""
    kitty_line = ""
    fill_line = ""
    
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
    
    for Y in range(term.height-1):
        if Y == 0 or Y == term.height-2 or Y == 4:
            compiled_line += term.move_xy(0,Y)+full_line
        elif Y == 2:
            compiled_line += term.move_xy(0,Y)+kitty_line
        elif Y == 1 or Y == 3:
            compiled_line += term.move_xy(0,Y)+fill_line
        else:
            compiled_line += sectioned_line
            
    compiled_line += term.move_xy(3,term.height-2)+keybinds_text
    # ┐└ ┘ ┌ ┴ ┬ │ ─ ┼ ┤ ├
    if config_data["use_panels"]:
        compiled_line += term.move_xy(0,0)+"┌"
        compiled_line += term.move_xy(0,4)+"├"
        compiled_line += term.move_xy(term.width-1,0)+"┐"
        compiled_line += term.move_xy(len(kitty_text),0)+"┬"
        compiled_line += term.move_xy(len(kitty_text),4)+"┴"
        compiled_line += term.move_xy(0,term.height-2)+"└"
        compiled_line += term.move_xy(term.width-1,4)+"┤"
        compiled_line += term.move_xy(term.width-1,term.height-2)+"┘"
    
    
    print(compiled_line)
    
def initial_setup():
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

with term.cbreak(), term.hidden_cursor(), term.fullscreen():
    initial_setup()
    redraw()
    color_test()
    
    while True:
        term.inkey(timeout=.1)
        