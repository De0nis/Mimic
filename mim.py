import datetime
import os
import time
import mouse
import pynput
import re
import pyautogui
test_list=[]
command_list = []
scenario_path_g = None
full_scene_file_name =None
test_file_name =None
screenshot_no = 0
scenario_path = os.path.join(os.getcwd(), (time.strftime('%d%m%H%M', time.localtime())))
if not os.path.exists(scenario_path):
        os.mkdir(scenario_path)
        os.mkdir(os.path.join(scenario_path, 'screenshots'))
scene_file_name = time.strftime('%d%m%H%M', time.localtime()) + ".py"
full_scene_file_name = os.path.join(scenario_path, scene_file_name)
scenario_path_g=scenario_path
test_file_name = time.strftime('%d%m%H%M', time.localtime()) + "_test.py"
test_file_name=os.path.join(scenario_path, test_file_name)

with open(os.path.abspath(scenario_path)+"/requirements.txt", 'w') as r:
    r.write("keyboard~=0.13.5\npynput~=1.7.7\nPyAutoGUI~=0.9.54\nmouse~=0.7.1\npsutil~=5.9.8\nPyGetWindow~=0.0.9\nPillow~=9.5.0\n")

with open(full_scene_file_name, 'w',encoding='utf-8') as f:
     f.write("import pyautogui\nimport mouse\nimport time\nimport keyboard\nfrom comparator import make_screenshot\n\n")

def stop():
    keyboard_listener.stop()
    mouse_listener.stop()
prev_time=None


def open_scenario(command_list):
    f = open(full_scene_file_name, 'a')
    for comm in command_list:
        f.write(comm)
    command_list.clear()
    f.close()

def open_testlist(command_list):
    f = open(test_file_name, 'a')
    for comm in command_list:
        f.write(comm)
    command_list.clear()
    f.close()

def record(act_str):
    global command_list
    act_split_timestamp = act_str.split("@")
    act = act_split_timestamp[1].split(",")
    if (re.search(r'press', act_split_timestamp[1]) != None):
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        key = act[0][6:]
        if "Key." in key:
            fixed_key=key.split(".")[-1]
            command_list.append(f"keyboard.press('{fixed_key}')\n")
        else:
            command_list.append(f"keyboard.press({key})\n")
    elif (re.search(r'rels', act_split_timestamp[1]) != None):
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        key = act[0][5:]
        if "Key." in key:
            fixed_key = key.split(".")[-1]
            command_list.append(f"keyboard.release('{fixed_key}')\n")
        else:
            command_list.append(f"keyboard.release({key})\n")
    elif (re.search(r'\d+,\d+,scroll', act_split_timestamp[1]) != None):
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.2)\n")
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
    elif (re.search(r'\d+,\d+,left', act_split_timestamp[1])) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.2)\n")
        command_list.append("mouse.click()\n")
    elif (re.search(r'\d+,\d+,right', act_split_timestamp[1])) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.2)\n")
        command_list.append("mouse.right_click()\n")
    elif (re.search(r'\d+,\d+,middle', act_split_timestamp[1])) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.2)\n")
        command_list.append(f"make_screenshot({screenshot_no},{act[0]},{act[1]})\n")
    elif (re.search(r'stop', act_split_timestamp[1])) != None:
        stop()
    open_scenario(command_list)

def act_builder(massege):
    global prev_time
    if prev_time == None:
        prev_time = datetime.datetime.now()
    time_act = datetime.datetime.now()
    delta = (time_act-prev_time).total_seconds()
    act_str = str(delta)+"@"+ str(massege)
    prev_time = time_act
    record(act_str)
    tes(act_str)
def keyboard_act_prress(key):

    if key == pynput.keyboard.Key.esc:
        act_builder("stop")
        stop()
    if str(key).isupper():
        act = ("press "+str(key).lower())
    else:
        act = ("press "+str(key))
    act_builder(act)

def keyboard_act_relase(key):
    act = ("rels "+str(key))
    if str(key).isupper():
        act = ("press "+str(key).lower())
    else:
        act = ("press "+str(key))
    act_builder(act)
def make_screenshot(x, y):
        global screenshot_no
        screenshot = pyautogui.screenshot(region=(x-50, y-50, x+50,y+50))
        screenshot_no+=1
        screenshot.save(f"{scenario_path_g}/screenshots/{screenshot_no}.png")
def mouse_act(x, y, button, pressed):
    if pressed:
        if button == pynput.mouse.Button.middle:
            make_screenshot(x, y)
        massege = f"{x},{y},{str(button)[7:]}"
        act_builder(massege)
def mouse_scroll(x, y, dx, dy):
    massege = (f"{x},{y},scroll {dy}")
    act_builder(massege)

keyboard_listener = pynput.keyboard.Listener(on_press=keyboard_act_prress,on_release=keyboard_act_relase)
mouse_listener = pynput.mouse.Listener(on_click=mouse_act, on_scroll=mouse_scroll)
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()
