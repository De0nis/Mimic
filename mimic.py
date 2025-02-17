import datetime
import os
import shutil
import subprocess
import pynput
import re
import pyautogui
import test_helpers

CONST = test_helpers.yaml_loader()
subprocess.Popen([CONST["CONNECTION_APP"], f"{os.path.join(os.getcwd(), CONST["CONNECTION_APP_ARGS"])}"])
command_list = test_list = []
test_file_name = full_scene_file_name = scenario_path_g = None
screenshot_no = mc = man = ms = panelcheck = 0
scenario_path = os.path.join(os.getcwd(), CONST["TEST_CASE_NAME"])
scene_file_name = f"{CONST["TEST_CASE_NAME"]}.py"

if not os.path.exists(scenario_path):
    os.mkdir(scenario_path)
    shutil.copy("test_helpers.py", scenario_path)
    shutil.copy("Const.yaml", scenario_path)
    shutil.copy("conftest.py", scenario_path)
    shutil.copy("Default.rdp", scenario_path)
    os.mkdir(os.path.join(scenario_path, 'screenshots'))
full_scene_file_name = os.path.join(scenario_path, scene_file_name)
scenario_path_g = scenario_path
test_file_name = f"{CONST["TEST_CASE_NAME"]}_test.py"
test_file_name = os.path.join(scenario_path, test_file_name)

with open(os.path.abspath(scenario_path) + "/requirements.txt", 'w') as r:
    r.write(
        "keyboard~=0.13.5\npynput~=1.7.7\nPyAutoGUI~=0.9.54\nmouse~=0.7.1\npsutil~=5.9.8\nPyGetWindow~=0.0.9\nPillow~=9.5.0\npygetwindow\nyaml\nrequests\npathlib\n\n")

with open(full_scene_file_name, 'w', encoding="Windows-1251") as f:
    f.write("import pyautogui\nimport mouse\nimport time\nimport keyboard\nimport test_helpers\n\n")

with open(test_file_name, 'w', encoding="Windows-1251") as f:
    f.write(
        "import pytest\nimport pygetwindow\nimport time\nimport mouse\nimport os\nimport keyboard\nimport test_helpers\n\ndef test_pause():\n\ttime.sleep(4)\n\n")

def stop():
    keyboard_listener.stop()
    mouse_listener.stop()

def open_scenario(command_list, file_name):
    f = open(file_name, 'a')
    for comm in command_list:
        f.write(comm)
    command_list.clear()
    f.close()

def record(act_str):
    global command_list, start_mouse_click_cp
    act_split_timestamp = act_str.split("@")
    act = act_split_timestamp[1].split(",")
    if re.search(r'press', act_split_timestamp[1]) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        key = act[0][6:]
        if "Key." in key:
            fixed_key = key.split(".")[-1]
            command_list.append(f"keyboard.press('{fixed_key}')\n")
        else:
            command_list.append(f"keyboard.press({key})\n")
    elif re.search(r'rels', act_split_timestamp[1]) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        key = act[0][5:]
        if "Key." in key:
            fixed_key = key.split(".")[-1]
            command_list.append(f"keyboard.release('{fixed_key}')\n")
        else:
            command_list.append(f"keyboard.release({key})\n")
    elif re.search(r'\d+,\d+,scroll', act_split_timestamp[1]) != None:
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.5)\n")
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
    elif re.search(r'\d+,\d+,left down', act_split_timestamp[1]) != None:
        start_mouse_click_cp = act
    elif re.search(r'\d+,\d+,left up', act_split_timestamp[1]) != None:
        if (start_mouse_click_cp[0] == act[0]) and (start_mouse_click_cp[1] == act[1]):
            command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
            command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.5)\n")
            command_list.append("mouse.click()\n")
        else:
            command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
            command_list.append(f"mouse.move({start_mouse_click_cp[0]},{start_mouse_click_cp[1]}, duration=0.5)\n")
            command_list.append(
                f"mouse.drag({start_mouse_click_cp[0]},{start_mouse_click_cp[1]}, {act[0]},{act[1]} ,absolute=True, duration=1)\n")
    elif re.search(r'\d+,\d+,right', act_split_timestamp[1]) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.5)\n")
        command_list.append("mouse.right_click()\n")
    elif re.search(r'\d+,\d+,middle up', act_split_timestamp[1]) != None:
        command_list.append(f"time.sleep({act_split_timestamp[0]})\n")
        command_list.append(f"mouse.move({act[0]},{act[1]}, duration=0.5)\n")
        command_list.append(f"make_screenshot({screenshot_no},{act[0]},{act[1]})\n")
    elif re.search(r'stop', act_split_timestamp[1]) != None:
        stop()
    open_scenario(command_list, full_scene_file_name)


def case_maker(act_str):
    global test_list, start_mouse_click_cp, prev_left_click_coords, man
    act_split_timestamp = act_str.split("@")
    act = act_split_timestamp[1].split(",")
    if re.search(r'\d+,\d+,left up', act_split_timestamp[1]) != None:
        prev_x = (int(start_mouse_click_cp[0]))
        prev_y = (int(start_mouse_click_cp[1]))
        if (int(act[0]) in range(prev_x - 2, prev_x + 2)) and (int(act[1]) in range(prev_y - 2, prev_y + 2)):
            man += 1
            test_list.append(f"def test_action{man}():\n")
            test_list.append(f"\ttime.sleep({act_split_timestamp[0]})\n")
            test_list.append(f"\tmouse.move({act[0]},{act[1]})\n")
            test_list.append(f"\tmouse.click()\n")
            test_list.append(f"\tassert {test_helpers.get_windowname()} == test_helpers.get_windowname()\n")
        else:
            man += 1
            test_list.append(f"def test_action{man}():\n")
            test_list.append(f"\ttime.sleep({act_split_timestamp[0]})\n")
            test_list.append(f"\tmouse.move({start_mouse_click_cp[0]},{start_mouse_click_cp[1]}, duration=0.5)\n")
            test_list.append(
                f"\tmouse.drag({start_mouse_click_cp[0]},{start_mouse_click_cp[1]},{act[0]} ,{act[1]} ,absolute=True, duration=1)\n")


    elif re.search(r'\d+,\d+,right up', act_split_timestamp[1]) != None:
        man += 1
        test_list.append(f"def test_action{man}():\n")
        test_list.append(f"\ttime.sleep({act_split_timestamp[0]})\n")
        test_list.append(f"\tmouse.move({act[0]},{act[1]}, duration=0.5)\n")
        test_list.append("\tmouse.right_click()\n")

    elif re.search(r'\d+,\d+,middle', act_split_timestamp[1]) != None:
        global mc
        mc += 1
        test_list.append(f"def test_screenshot{mc}():\n")
        test_list.append(f"\ttime.sleep({act_split_timestamp[0]})\n")
        test_list.append(f"\tmouse.move({act[0]},{act[1]})\n")
        test_list.append(
            f"\taverage= test_helpers.make_screenshot({screenshot_no},{act[0]},{act[1]}, os.path.dirname(os.path.abspath(__file__)))\n")
        test_list.append(f"\tassert(average < 100) \n")
    elif re.search(r'scroll', act_split_timestamp[1]) != None:
        man += 1
        test_list.append(f"def test_action{man}():\n")
        test_list.append(f"\tmouse.move({act[0]},{act[1]}, duration=0.5)\n")
        test_list.append(f"\tmouse.wheel({act[-1].split()[-1]})\n")
    elif re.search(r'press', act_split_timestamp[1]) != None:
        buttn_name = act[0].split()[1]
        if "Key" in buttn_name and ("255" not in buttn_name):
            buttn_name = f"'{buttn_name[4:]}'"
        man += 1
        test_list.append(f"def test_action{man}():\n")
        test_list.append(f"\tkeyboard.press({buttn_name})\n")
        test_list.append(f"\ttime.sleep(0.01)\n")

    elif re.search(r'relase', act_split_timestamp[1]) != None:
        buttn_name = act[0].split()[1]
        if "Key" in buttn_name and ("255" not in buttn_name):
            buttn_name = f"'{buttn_name[4:]}'"
        man += 1
        test_list.append(f"def test_action{man}():\n")
        test_list.append(f"\tkeyboard.release({buttn_name})\n")

    elif re.search(r'stop', act_split_timestamp[1]) != None:
        stop()
    open_scenario(test_list, test_file_name)


prev_time = None


def act_builder(massege):
    global prev_time
    if not prev_time:
        prev_time = datetime.datetime.now()
    delta = (datetime.datetime.now() - prev_time).total_seconds()
    act_str = str(delta) + "@" + str(massege)
    prev_time = datetime.datetime.now()
    record(act_str)
    case_maker(act_str)


def keyboard_act_prress(key):
    if key == pynput.keyboard.Key.esc:
        act_builder("stop")
        stop()
    if str(key) != "<255>":
        if str(key).isupper():
            act = ("press " + str(key).lower())
        else:
            act = ("press " + str(key))
        act_builder(act)


def keyboard_act_relase(key):
    if str(key) != "<255>":
        if str(key).isupper():
            if str(key).isupper():
                act = ("relase " + str(key).lower())
            else:
                act = ("relase " + str(key))
            act_builder(act)


def make_screenshot(x, y):
    global screenshot_no
    screenshot = pyautogui.screenshot(region=((x - 50), (y - 50), 100, 100))
    screenshot_no += 1
    screenshot.save(f"{scenario_path_g}/screenshots/{screenshot_no}.png")


def mouse_act(x, y, button, pressed):
    massege = None
    if button == pynput.mouse.Button.middle and pressed:
        make_screenshot(x, y)
        massege = f"{x},{y},{str(button)[7:]}"
    if button != pynput.mouse.Button.middle:
        if pressed:
            massege = f"{x},{y},{str(button)[7:]} down"
        else:
            massege = f"{x},{y},{str(button)[7:]} up"
    act_builder(massege)


def mouse_scroll(x, y, dx, dy):
    massege = f"{x},{y},scroll {dy}"
    act_builder(massege)


keyboard_listener = pynput.keyboard.Listener(on_press=keyboard_act_prress, on_release=keyboard_act_relase)
mouse_listener = pynput.mouse.Listener(on_click=mouse_act, on_scroll=mouse_scroll)
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()
