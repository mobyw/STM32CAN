#!python3 
# -*- coding:utf-8 -*-

import time
import json
import threading
from tkinter import *
from tkinter import ttk
import serial
import webbrowser

bg_color = '#29282E'
label_color = '#E9E5E2'
red_color = '#FF6666'
blue_color = '#0099CC'
yellow_color = '#FFFFCC'
orange_color = '#FF9900'
green_color = '#99CC99'
gray_color = '#393945'

serial_object = None


class Channel:
    name = "Name"
    id = 0
    analog = 0
    key = "xxxxxxxx"
    relay = 0

    def __init__(self, name="Name"):
        self.name = name


ch1 = Channel(name="设备1")
ch2 = Channel(name="设备2")
ch3 = Channel(name="设备3")
ch4 = Channel(name="设备4")
ch5 = Channel(name="设备5")

GUI = Tk()
GUI.title("Serial Data Acquisition")
GUI.configure(bg=bg_color)
GUI.geometry('780x186')
GUI.resizable(width=False, height=False)

# Gets both half the screen width/height and window width/height
positionRight = int(GUI.winfo_screenwidth() / 2 - 780 / 2)
positionDown = int(GUI.winfo_screenheight() / 2 - 186 / 2)

# Positions the window in the center
GUI.geometry("+{}+{}".format(positionRight, positionDown))

connection_status = False
relay1_status = 1
relay2_status = 1
refresh_rate = 2  # 2 Hz


def Go2Info():
    webbrowser.open("https://github.com/mobyw/STM32CAN")


menubar = Menu(GUI)
GUI.config(menu=menubar)
settingsmenu = Menu(menubar, tearoff=0, activebackground=bg_color, activeforeground=label_color)
menubar.add_cascade(label="Settings", menu=settingsmenu)

# settingsmenu.add_command(label="Channels", command=Create_SetWindow)
# settingsmenu.add_separator()
settingsmenu.add_command(label="Quit", command=GUI.quit)

helpmenu = Menu(menubar, tearoff=0, activebackground=red_color, activeforeground=label_color)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About", command=Go2Info)


def ConnectionEnd():
    global connection_status

    control_button.config(text="RUN")
    control_button.config(bg=blue_color)
    connection_status = False


def ConnectionStart():
    global connection_status

    control_button.config(text="STOP")
    control_button.config(bg=red_color)
    connection_status = True


def CTRLButton_Handle():
    global connection_status
    global serial_object

    if not connection_status:
        Try_Connection()
    else:
        ConnectionEnd()
        serial_object.close()


def Try_Connection():
    global connection_status
    global serial_object

    port = input_port.get()
    speed = speed_port.get()

    try:
        serial_object = serial.Serial(str(port), baudrate=speed, timeout=1)
        ConnectionStart()
    except serial.serialutil.SerialException:
        print("Cant Open Specified Port")
        ConnectionEnd()


def Relay1Button_Handle():
    global connection_status
    global relay1_status
    global serial_object

    if connection_status:
        if not relay1_status:
            serial_object.write('~001,1111.'.encode())
            relay1_status = 1
            relay1_button.config(text="R1 OFF")
            relay1_button.config(bg=blue_color)
        else:
            serial_object.write('~001,0000.'.encode())
            relay1_status = 0
            relay1_button.config(text="R1 ON")
            relay1_button.config(bg=red_color)


def Relay2Button_Handle():
    global connection_status
    global relay2_status
    global serial_object

    if connection_status:
        if not relay2_status:
            serial_object.write('~004,1111.'.encode())
            relay2_status = 1
            relay2_button.config(text="R2 OFF")
            relay2_button.config(bg=blue_color)
        else:
            serial_object.write('~004,0000.'.encode())
            relay2_status = 0
            relay2_button.config(text="R2 ON")
            relay2_button.config(bg=red_color)


def SerialDataAcq():
    global connection_status
    global serial_object

    while True:
        time.sleep(0.1)  # delay for do not overload the CPU
        while connection_status:
            try:
                serial_input = serial_object.readline()
                strJson = str(serial_input, encoding='utf-8')
                if strJson:
                    
                    if "id" in strJson:
                        jsonData = json.loads(strJson)
                        print(strJson)

                        if jsonData["id"] == 1:
                            ch1.analog = int(jsonData["analog"])
                            ch1.key = '{0:08b}'.format(int(jsonData["key"]))
                            ch1.relay = int(jsonData["relay"])
                        elif jsonData["id"] == 2:
                            ch2.analog = int(jsonData["analog"])
                            ch2.key = '{0:08b}'.format(int(jsonData["key"]))
                            ch2.relay = int(jsonData["relay"])
                        elif jsonData["id"] == 3:
                            ch3.analog = int(jsonData["analog"])
                            ch3.key = '{0:08b}'.format(int(jsonData["key"]))
                            ch3.relay = int(jsonData["relay"])
                        elif jsonData["id"] == 4:
                            ch4.analog = int(jsonData["analog"])
                            ch4.key = '{0:08b}'.format(int(jsonData["key"]))
                            ch4.relay = int(jsonData["relay"])
                        elif jsonData["id"] == 5:
                            ch5.analog = int(jsonData["analog"])
                            ch5.key = '{0:08b}'.format(int(jsonData["key"]))
                            ch5.relay = int(jsonData["relay"])

            except ConnectionError:
                print("Connection Error")
                ConnectionEnd()


def UpdateGUI():
    global connection_status

    while True:
        time.sleep(1 / refresh_rate)

        while connection_status:
            time.sleep(1 / refresh_rate)

            item_name1.set(ch1.name)
            item_name2.set(ch2.name)
            item_name3.set(ch3.name)
            item_name4.set(ch4.name)
            item_name5.set(ch5.name)

            pbar1.config(max=1023)
            pbar2.config(max=1023)
            pbar3.config(max=1023)
            pbar4.config(max=1023)
            pbar5.config(max=1023)

            input1a.set(str(ch1.analog))
            input2a.set(str(ch2.analog))
            input3a.set(str(ch3.analog))
            input4a.set(str(ch4.analog))
            input5a.set(str(ch5.analog))

            input1k.set(''.join(reversed(ch1.key.replace("1", "○").replace("0", "●"))))
            input2k.set(''.join(reversed(ch2.key.replace("1", "○").replace("0", "●"))))
            input3k.set(''.join(reversed(ch3.key.replace("1", "○").replace("0", "●"))))
            input4k.set(''.join(reversed(ch4.key.replace("1", "○").replace("0", "●"))))
            input5k.set(''.join(reversed(ch5.key.replace("1", "○").replace("0", "●"))))

            pbar1["value"] = ch1.analog
            pbar2["value"] = ch2.analog
            pbar3["value"] = ch3.analog
            pbar4["value"] = ch4.analog
            pbar5["value"] = ch5.analog


# FRAMES
x = 5
y = 5

item1 = Frame(height=130, width=150, bd=2, relief='groove', bg=bg_color)
item1.place(x=x, y=y)
x += 155
item2 = Frame(height=130, width=150, bd=2, relief='groove', bg=bg_color)
item2.place(x=x, y=y)
x += 155
item3 = Frame(height=130, width=150, bd=2, relief='groove', bg=bg_color)
item3.place(x=x, y=y)
x += 155
item4 = Frame(height=130, width=150, bd=2, relief='groove', bg=bg_color)
item4.place(x=x, y=y)
x += 155
item5 = Frame(height=130, width=150, bd=2, relief='groove', bg=bg_color)
item5.place(x=x, y=y)

info = Frame(height=40, width=770, bd=2, relief='groove', bg=bg_color)
info.place(x=5, y=140)

# ENTRY
x = 80
y = 160

# BUTTONS
control_button = Button(
    text="RUN",
    font=("Consolas-with-Yahei", 9),
    width=12,
    command=CTRLButton_Handle,
    bg=blue_color,
    fg=label_color
)
control_button.place(x=x, y=y + 2, anchor="center")

x += 155
relay1_button = Button(
    text="R1 OFF",
    font=("Consolas-with-Yahei", 9),
    width=12,
    command=Relay1Button_Handle,
    bg=blue_color,
    fg=label_color
)
relay1_button.place(x=x, y=y + 2, anchor="center")

x += 155
relay2_button = Button(
    text="R2 OFF",
    font=("Consolas-with-Yahei", 9),
    width=12,
    command=Relay2Button_Handle,
    bg=blue_color,
    fg=label_color
)
relay2_button.place(x=x, y=y + 2, anchor="center")

x += 155
input_port = Entry(
    widt=12,
    font=("Consolas-with-Yahei", 12),
    justify="center",
    bg=gray_color,
    fg=label_color
)
input_port.insert(INSERT, "COM30")
input_port.place(x=x, y=y, anchor="center")

x += 155
speed_port = Entry(
    widt=12,
    font=("Consolas-with-Yahei", 12),
    justify="center",
    bg=gray_color,
    fg=label_color
)
speed_port.insert(INSERT, "115200")
speed_port.place(x=x, y=y, anchor="center")

# PROGRESS BAR
ProgressBar_style = ttk.Style()
ProgressBar_style.theme_use('clam')

ProgressBar_style.configure(
    "red.Horizontal.TProgressbar",
    troughcolor=bg_color,
    background=red_color,
    bordercolor=red_color,
    lightcolor=red_color,
    darkcolor=red_color
)

ProgressBar_style.configure(
    "blue.Horizontal.TProgressbar",
    troughcolor=bg_color,
    background=blue_color,
    bordercolor=blue_color,
    lightcolor=blue_color,
    darkcolor=blue_color
)

ProgressBar_style.configure(
    "yellow.Horizontal.TProgressbar",
    troughcolor=bg_color,
    background=yellow_color,
    bordercolor=yellow_color,
    lightcolor=yellow_color,
    darkcolor=yellow_color
)

ProgressBar_style.configure(
    "orange.Horizontal.TProgressbar",
    troughcolor=bg_color,
    background=orange_color,
    bordercolor=orange_color,
    lightcolor=orange_color,
    darkcolor=orange_color
)

ProgressBar_style.configure(
    "green.Horizontal.TProgressbar",
    troughcolor=bg_color,
    background=green_color,
    bordercolor=green_color,
    lightcolor=green_color,
    darkcolor=green_color
)

x = 80
y = 110

pbar1 = ttk.Progressbar(
    style="red.Horizontal.TProgressbar",
    orient=HORIZONTAL,
    mode='determinate',
    length=130,
    max=1024
)

pbar1.place(x=x, y=y, anchor="center")
pbar1["value"] = ch1.analog

x += 155
pbar2 = ttk.Progressbar(
    style="blue.Horizontal.TProgressbar",
    orient=HORIZONTAL,
    mode='determinate',
    length=130,
    max=1024
)

pbar2.place(x=x, y=y, anchor="center")
pbar2["value"] = ch2.analog

x += 155
pbar3 = ttk.Progressbar(
    style="yellow.Horizontal.TProgressbar",
    orient=HORIZONTAL,
    mode='determinate',
    length=130,
    max=1024
)

pbar3.place(x=x, y=y, anchor="center")
pbar3["value"] = ch3.analog

x += 155
pbar4 = ttk.Progressbar(
    style="orange.Horizontal.TProgressbar",
    orient=HORIZONTAL,
    mode='determinate',
    length=130,
    max=1024
)

pbar4.place(x=x, y=y, anchor="center")
pbar4["value"] = ch4.analog

x += 155
pbar5 = ttk.Progressbar(
    style="green.Horizontal.TProgressbar",
    orient=HORIZONTAL,
    mode='determinate',
    length=130,
    max=1024
)

pbar5.place(x=x, y=y, anchor="center")
pbar5["value"] = ch5.analog

# VARIABLE LABELS
x = 80
y = 20

item_name1 = StringVar()
item_name1.set(ch1.name)

label1 = Label(
    textvariable=item_name1,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label1.place(x=x, y=y, anchor="center")

x += 155
item_name2 = StringVar()
item_name2.set(ch2.name)
label2 = Label(
    textvariable=item_name2,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label2.place(x=x, y=y, anchor="center")

x += 155
item_name3 = StringVar()
item_name3.set(ch3.name)
label3 = Label(
    textvariable=item_name3,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label3.place(x=x, y=y, anchor="center")

x += 155
item_name4 = StringVar()
item_name4.set(ch4.name)
label4 = Label(
    textvariable=item_name4,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label4.place(x=x, y=y, anchor="center")

x += 155
item_name5 = StringVar()
item_name5.set(ch5.name)
label5 = Label(
    textvariable=item_name5,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label5.place(x=x, y=y, anchor="center")

x = 80
y = 75

input1a = StringVar()
input1a.set(str(ch1.analog))
label1a = Label(
    textvariable=input1a,
    font=("Consolas-with-Yahei", 20),
    bg=bg_color,
    fg=label_color
)
label1a.place(x=x, y=y, anchor="center")

x += 155
input2a = StringVar()
input2a.set(str(ch2.analog))
label2a = Label(
    textvariable=input2a,
    font=("Consolas-with-Yahei", 20),
    bg=bg_color,
    fg=label_color
)
label2a.place(x=x, y=y, anchor="center")

x += 155
input3a = StringVar()
input3a.set(str(ch3.analog))
label3a = Label(
    textvariable=input3a,
    font=("Consolas-with-Yahei", 20),
    bg=bg_color,
    fg=label_color
)
label3a.place(x=x, y=y, anchor="center")

x += 155
input4a = StringVar()
input4a.set(str(ch4.analog))
label4a = Label(
    textvariable=input4a,
    font=("Consolas-with-Yahei", 20),
    bg=bg_color,
    fg=label_color
)
label4a.place(x=x, y=y, anchor="center")

x += 155
input5a = StringVar()
input5a.set(str(ch5.analog))
label5a = Label(
    textvariable=input5a,
    font=("Consolas-with-Yahei", 20),
    bg=bg_color,
    fg=label_color
)
label5a.place(x=x, y=y, anchor="center")

x = 80
y = 45

input1k = StringVar()
input1k.set(str(ch1.key))
label1k = Label(
    textvariable=input1k,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label1k.place(x=x, y=y, anchor="center")

x += 155
input2k = StringVar()
input2k.set(str(ch2.key))
label2k = Label(
    textvariable=input2k,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label2k.place(x=x, y=y, anchor="center")

x += 155
input3k = StringVar()
input3k.set(str(ch3.key))
label3k = Label(
    textvariable=input3k,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label3k.place(x=x, y=y, anchor="center")

x += 155
input4k = StringVar()
input4k.set(str(ch4.key))
label4k = Label(
    textvariable=input4k,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label4k.place(x=x, y=y, anchor="center")

x += 155
input5k = StringVar()
input5k.set(str(ch5.key))
label5k = Label(
    textvariable=input5k,
    font=("Consolas-with-Yahei", 13),
    bg=bg_color,
    fg=label_color
)
label5k.place(x=x, y=y, anchor="center")

myThread1 = threading.Thread(target=UpdateGUI)
myThread1.daemon = True
myThread1.start()

myThread2 = threading.Thread(target=SerialDataAcq)
myThread2.daemon = True
myThread2.start()

if __name__ == '__main__':
    GUI.mainloop()
