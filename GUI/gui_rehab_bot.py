#Libraries
import subprocess, serial, math, time
# import sqlite3 as sql
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from scipy import signal
import numpy as np

#Driver Code
root = tk.Tk()
root.attributes('-fullscreen', True)
root.title("Rehab-Bot App")
root.configure(bg='cyan')

#Defining Arduino
arduino = serial.Serial(port='COM12', baudrate=115200, timeout = 0.1)
# arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout = 0.1)
print("Connected to :"+arduino.portstr)

#Creating/ Calling a Database
# con = sql.connect(r"D:\\KULIAH\SEMESTER 10\\CODE\\hmi\database\\rehab-bot.db")
# c = con.cursor()


#Variables
ID = StringVar()
PW = StringVar()
KP = DoubleVar()
KD = DoubleVar()
username = str()
password = str()
smax_p = str()
smin_p = str()
kmes_p = str()
rdur_p = int()
time_left = int()
hour = 0
minute = 0
second = 0
hours = int()
mins = int()
secs = int()
smax_a = str()
smin_a = str()
kpeg_a = str()
cdam_a = str()
smaxbaru_p =str()
sminbaru_p = str()
rdurbaru_p = str()
smaxbaru_a =str()
sminbaru_a = str()
send_code = str()
a1 = int()
b1 = int()
b2 = int()
berhenti_rehabilitasi_pasif_clicked = False

#Functions
def serial_write_mode_s():
    send_code_mode_s = "-s"
    print(send_code_mode_s)

    arduino.flush()
    arduino.write(send_code_mode_s.encode())

def serial_write_mode_9():
    send_code_mode_9 = "9"
    print(send_code_mode_9)

    arduino.flush()
    arduino.write(send_code_mode_9.encode())

def serial_write_mode_0(target_angle):
    send_code_mode_0 = "0;" + str(target_angle)
    print(send_code_mode_0)

    arduino.flush()
    arduino.write(send_code_mode_0.encode())

def serial_write_mode_1(max_angle,min_angle,speed,duration):
    send_code_mode_1 = "1;" + str(max_angle) + ";" + str(min_angle)  + ";" + str(speed)  + ";" + str(duration)
    print(send_code_mode_1)

    arduino.flush()
    arduino.write(send_code_mode_1.encode())

def serial_write_mode_3(max_angle,min_angle,k_spring,c_damping):

    convert_to_discrete(k_spring,c_damping)

    send_code_mode_3 = "3;0;" + str(a1) + ";" + str(b1) + ";" + str(b2) + ";" + str(max_angle) + ";" + str(min_angle)
    print(send_code_mode_3)

    arduino.flush()
    arduino.write(send_code_mode_3.encode())

def convert_to_discrete(spring_const, damping_coef):
    global a1, b1, b2

    # Low-pass Filter
    samplingFreq = 20                                   # (Hz)
    freq = 1                                            # pole frequency (rad/s)
    w0 = 2 * np.pi * freq                               # w0
    num = 1                                             # transfer function numerator coefficients
    den = [float(damping_coef), float(spring_const)]    # transfer function denominator coefficients
    lowPass = signal.TransferFunction(num, den)         # Transfer function

    dt = 1.0 / samplingFreq
    discreteLowPass = lowPass.to_discrete(dt, method='gbt', alpha=0.5)

    # The coefficients from the discrete form of the filter transfer function (but with a negative sign)
    b = discreteLowPass.num
    a = -discreteLowPass.den

    a1 = a[1]
    b1, b2 = b[:2]

def open_onboard(event):
    subprocess.Popen(["onboard"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def keluar_aplikasi():
    root.destroy()

def masuk():
    username = ID.get()
    password = PW.get()
    if username == "admin" and password == "admin":
        Login_Page_Frame.pack_forget()
        Start_Page_Frame.pack()

        label_Start_Page_2.config(text='"'+username+'"',
                                fg='black',bg='cyan',
                                font=("Arial",20,"bold"))
        
    else:
        messagebox.showerror("Error","Wrong username or password, try again!")

    ID.set("")
    PW.set("")

def keluar_akun():
    global frames

    for frame in frames:
        frame.pack_forget()

    Login_Page_Frame.pack()

def mulai():
    global frames

    for frame in frames:
        frame.pack_forget()

    Home_Page_Frame.pack()

    # Arduino Code
    serial_write_mode_0(0)

def kembali_1():
    global frames

    for frame in frames:
        frame.pack_forget()

    Start_Page_Frame.pack()

def kembali_2():
    global frames
    
    for frame in frames:
        frame.pack_forget()
        
    Home_Page_Frame.pack()

def kembali_3():
    global frames
    
    for frame in frames:
        frame.pack_forget()

    Pasif_Ongoing_Page_Frame.pack()

def kembali_4():
    global frames
    
    for frame in frames:
        frame.pack_forget()

    Aktif_Ongoing_Page_Frame.pack()

def pasif():
    global frames
    
    for frame in frames:
        frame.pack_forget()

    Pasif_Page_Frame.pack()

def aktif():
    global frames
    
    for frame in frames:
        frame.pack_forget()

    Aktif_Page_Frame.pack()

def update_1(event):
    global smax_p, smin_p, kmes_p, rdur_p, hour, minute, second
    smax_p = str(slider_Pasif_Page_1.get())
    smin_p = str(slider_Pasif_Page_2.get())
    kmes_p = str(slider_Pasif_Page_3.get())
    rdur_p = hour*60 + minute + second/60

    label_Pasif_Page_6.config(text="Sudut maksimum    = "+smax_p+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Pasif_Page_7.config(text="Sudut minimum       = "+smin_p+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Pasif_Page_8.config(text="Kecepatan mesin    = "+kmes_p+"%",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Pasif_Page_9.config(text="Durasi rehabilitasi   = "+str(hour)+" jam "+str(minute)+" menit "+str(second)+" detik",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

def update_2(event):
    global smax_a, smin_a, kpeg_a, cdam_a
    smax_a = str(slider_Aktif_Page_1.get())
    smin_a = str(slider_Aktif_Page_2.get())
    kpeg_a = entry_Aktif_Page_1.get()
    cdam_a = entry_Aktif_Page_2.get()

    label_Aktif_Page_6.config(text="Sudut maksimum    = "+smax_a+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Aktif_Page_7.config(text="Sudut minimum       = "+smin_a+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Aktif_Page_8.config(text="Konstanta pegas     = "+kpeg_a+" N/m",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Aktif_Page_9.config(text="Koefisien damping   = "+cdam_a+" Ns/m",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

def update_3(event):
    global smaxbaru_p, sminbaru_p, smaxbaru_a, sminbaru_a
    smaxbaru_p = str(slider_Pasif_Ubah_Page_1.get())
    sminbaru_p = str(slider_Pasif_Ubah_Page_2.get())
    smaxbaru_a = str(slider_Aktif_Ubah_Page_1.get())
    sminbaru_a = str(slider_Aktif_Ubah_Page_2.get())

    label_Pasif_Ubah_Page_6.config(text="Sudut Maksimum Baru = "+smaxbaru_p+"°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))

    label_Pasif_Ubah_Page_7.config(text="Sudut Minimum Baru    = "+sminbaru_p+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

    label_Aktif_Ubah_Page_6.config(text="Sudut Maksimum Baru = "+smaxbaru_a+"°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))

    label_Aktif_Ubah_Page_7.config(text="Sudut Minimum Baru    = "+sminbaru_a+"°",
                                fg='black',bg='cyan',
                                font=("Arial",14,"bold"))

def update_pembacaan_sudut():
    data = arduino.readline().decode().strip()
    if data:
        label_Pasif_Ongoing_Page_10.config(text=str(data)+"°",
                                fg='black',bg='white',
                                font=("Arial",20,"bold"))

        label_Aktif_Ongoing_Page_10.config(text=str(data)+"°",
                                fg='black',bg='white',
                                font=("Arial",20,"bold"))

    root.after(100,update_pembacaan_sudut)

def hour_up():
    global hour
    if hour < 99:
        hour += 1
    elif hour == 99:
        hour = 0
    
    label_Pasif_Page_Timer_1.config(text="%02d" % (hour,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))

    update_1("<B1-Click>")

def hour_down():
    global hour
    if hour > 0:
        hour -= 1
    elif hour == 0:
        hour = 99

    label_Pasif_Page_Timer_1.config(text="%02d" % (hour,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))

    update_1("<B1-Click>")

def minute_up():
    global minute
    if minute < 59:
        minute += 1
    elif minute == 59:
        minute = 0

    label_Pasif_Page_Timer_3.config(text="%02d" % (minute,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))

    update_1("<B1-Click>")

def minute_down():
    global minute
    if minute > 0:
        minute -= 1
    elif minute == 0:
        minute = 59

    label_Pasif_Page_Timer_3.config(text="%02d" % (minute,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))

    update_1("<B1-Click>")   

def second_up():
    global second
    if second < 59:
        second += 1
    elif second == 59:
        second = 0

    label_Pasif_Page_Timer_5.config(text="%02d" % (second,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",28,"bold"))

    update_1("<B1-Click>")

def second_down():
    global second
    if second > 0:
        second -= 1
    elif second == 0:
        second = 59

    label_Pasif_Page_Timer_5.config(text="%02d" % (second,),
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",28,"bold"))

    update_1("<B1-Click>")

def callback():
    global berhenti_rehabilitasi_pasif_clicked
    berhenti_rehabilitasi_pasif_clicked = not berhenti_rehabilitasi_pasif_clicked

def loop_time():
    global time_left, hours, mins, secs, berhenti_rehabilitasi_pasif_clicked, frames
    if berhenti_rehabilitasi_pasif_clicked == True:
        berhenti_rehabilitasi_pasif_clicked = False
    
    elif time_left > 0:
        # updating time variables
        mins,secs = divmod(time_left,60)
        hours = 0
        if mins > 60:

            hours, mins = divmod(mins, 60)

        label_Pasif_Ongoing_Page_4.config(text="%02d" % (hours,),
                                fg='black',bg='white',
                                font=("Arial",30,"bold"))

        label_Pasif_Ongoing_Page_6.config(text="%02d" % (mins,),
                                    fg='black',bg='white',
                                    font=("Arial",30,"bold"))

        label_Pasif_Ongoing_Page_8.config(text="%02d" % (secs,),
                                    fg='black',bg='white',
                                    font=("Arial",30,"bold"))
            
        # decresing the value of time_left 
        # after every one sec by one
        time_left -= 1

        # print(time_left)

        # looping driver
        root.after(1000,loop_time)

    elif time_left == 0:
        # update gui
        label_Pasif_Ongoing_Page_4.config(text="00",
                                fg='black',bg='white',
                                font=("Arial",30,"bold"))

        label_Pasif_Ongoing_Page_6.config(text="00",
                                    fg='black',bg='white',
                                    font=("Arial",30,"bold"))

        label_Pasif_Ongoing_Page_8.config(text="00",
                                    fg='black',bg='white',
                                    font=("Arial",30,"bold"))
        
        messagebox.showinfo("Time Countdown","Durasi Rehabilitasi Selesai")

        # lanjut ke halaman finish page    
        for frame in frames:
            frame.pack_forget()

        Finish_Page_Frame.pack()

        # Arduino Code
        serial_write_mode_s()

def mulai_rehabilitasi_pasif():
    global smax_p, smin_p, kmes_p, rdur_p, time_left, frames
    
    slider_Pasif_Ubah_Page_1.set(smax_p)
    slider_Pasif_Ubah_Page_2.set(smin_p)

    label_Pasif_Ongoing_Page_2.config(text="Sudut Maksimum = " + str(smax_p) + "°\n\nSudut Minimum    = " + str(smin_p) + "°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))

    label_Pasif_Ubah_Page_4.config(text="Sudut Maksimum\nSebelumnya = "+str(smax_p)+"°",
                             fg='black',bg='chocolate',
                             font=("Arial",10))

    label_Pasif_Ubah_Page_5.config(text="Sudut Minimum\nSebelumnya = "+str(smin_p)+"°",
                                fg='black',bg='gray',
                                font=("Arial",10))

    for frame in frames:
        frame.pack_forget()

    Pasif_Ongoing_Page_Frame.pack()

    # Turn on timer
    time_left = rdur_p*60
    loop_time()

    # Read measured angle
    update_pembacaan_sudut()

    # Arduino Code
    serial_write_mode_1(smax_p, smin_p, kmes_p, rdur_p)

def mulai_rehabilitasi_aktif():
    global smax_a, smin_a, kpeg_a, cdam_a, frames
    
    for frame in frames:
        frame.pack_forget()

    Aktif_Ongoing_Page_Frame.pack()

    slider_Aktif_Ubah_Page_1.set(smax_a)
    slider_Aktif_Ubah_Page_2.set(smin_a)

    label_Aktif_Ongoing_Page_2.config(text="Sudut Maksimum = " + str(smax_a) + "°\n\nSudut Minimum    = " + str(smin_a) + "°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))

    label_Aktif_Ubah_Page_4.config(text="Sudut Maksimum\nSebelumnya = "+str(smax_a)+"°",
                             fg='black',bg='chocolate',
                             font=("Arial",10))

    label_Aktif_Ubah_Page_5.config(text="Sudut Minimum\nSebelumnya = "+str(smin_a)+"°",
                                fg='black',bg='gray',
                                font=("Arial",10))

    update_pembacaan_sudut()

    # Arduino Code
    serial_write_mode_3(smax_a, smin_a, kpeg_a, cdam_a)

def ubah_rehabilitasi_pasif():
    global frames
    
    for frame in frames:
        frame.pack_forget()

    Pasif_Ubah_Page_Frame.pack()

def ubah_rehabilitasi_pasif_confirmed():
    global smaxbaru_p, sminbaru_p, kmes_p, rdurbaru_p, time_left, frames

    global frames
    
    for frame in frames:
        frame.pack_forget()

    Pasif_Ongoing_Page_Frame.pack()

    rdurbaru_p = time_left/60

    # GUI Update
    label_Pasif_Ongoing_Page_2.config(text="Sudut Maksimum = " + str(smaxbaru_p) + "°\n\nSudut Minimum    = " + str(sminbaru_p) + "°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))

    # Arduino Code
    serial_write_mode_s()
    root.after(1000, serial_write_mode_1, smaxbaru_p, sminbaru_p, kmes_p, rdurbaru_p)

def berhenti_rehabilitasi_pasif():
    global frames
    
    for frame in frames:
        frame.pack_forget()
        
    Finish_Page_Frame.pack()

    callback()

    # Arduino Code
    serial_write_mode_s()

def ubah_rehabilitasi_aktif():
    global frames
    
    for frame in frames:
        frame.pack_forget()
        
    Aktif_Ubah_Page_Frame.pack()

def ubah_rehabilitasi_aktif_confirmed():
    global smaxbaru_a, sminbaru_a, kpeg_a, cdam_a, frames
    
    for frame in frames:
        frame.pack_forget()
        
    Aktif_Ongoing_Page_Frame.pack()

    # GUI Update
    label_Aktif_Ongoing_Page_2.config(text="Sudut Maksimum = " + str(smaxbaru_a) + "°\n\nSudut Minimum    = " + str(sminbaru_a) + "°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))

    # Arduino Code
    serial_write_mode_s()
    root.after(1000, serial_write_mode_3, smaxbaru_a, sminbaru_a, kpeg_a, cdam_a)

def berhenti_rehabilitasi_aktif():
    global frames
    
    for frame in frames:
        frame.pack_forget()
        
    Finish_Page_Frame.pack()

    # Arduino Code
    serial_write_mode_s()

def return_to_start_page():
    global frames
    
    for frame in frames:
        frame.pack_forget()
        
    Start_Page_Frame.pack()

#Main Frame
Main_Frame = tk.Frame(root,bg='cyan')
Main_Frame.pack(padx=10,pady=10)
Main_Frame.pack_propagate(False)
Main_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

#Pages
#Login Page Frame
Login_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Login_Page_Frame.pack(padx=10,pady=10)
Login_Page_Frame.pack_propagate(False)
Login_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Login_Page_Frame_1 = tk.Frame(Login_Page_Frame,bg='cyan')
Login_Page_Frame_1.pack(padx=10,pady=10)
Login_Page_Frame_1.pack_propagate(False)
Login_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Login_Page_Frame_1a = tk.Frame(Login_Page_Frame_1,bg='cyan')
Login_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Login_Page_Frame_1a.pack_propagate(False)
Login_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Login_Page_Frame_1b = tk.Frame(Login_Page_Frame_1,bg='cyan')
Login_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Login_Page_Frame_1b.pack_propagate(False)
Login_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Login_Page_Frame_2 = tk.Frame(Login_Page_Frame,bg='cyan')
Login_Page_Frame_2.pack(padx=10,pady=10)
Login_Page_Frame_2.pack_propagate(False)
Login_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.35)

Login_Page_Frame_2a = tk.Frame(Login_Page_Frame_2,bg='cyan')
Login_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Login_Page_Frame_2a.pack_propagate(False)
Login_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.35,height=root.winfo_screenheight()*0.35)

Login_Page_Frame_2b = tk.Frame(Login_Page_Frame_2,bg='cyan')
Login_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Login_Page_Frame_2b.pack_propagate(False)
Login_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.65,height=root.winfo_screenheight()*0.35)

Login_Page_Frame_3 = tk.Frame(Login_Page_Frame,bg='cyan')
Login_Page_Frame_3.pack(padx=10,pady=10)
Login_Page_Frame_3.pack_propagate(False)
Login_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Login_Page_Frame_3a = tk.Frame(Login_Page_Frame_3,bg='cyan')
Login_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Login_Page_Frame_3a.pack_propagate(False)
Login_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.1)

Login_Page_Frame_3b = tk.Frame(Login_Page_Frame_3,bg='cyan')
Login_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Login_Page_Frame_3b.pack_propagate(False)
Login_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.1)

Login_Page_Frame_4 = tk.Frame(Login_Page_Frame,bg='cyan')
Login_Page_Frame_4.pack(padx=10,pady=10)
Login_Page_Frame_4.pack_propagate(False)
Login_Page_Frame_4.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.4)

label_Login_Page_1 = tk.Label(Login_Page_Frame_1a,text="REHAB-BOT APP",
                              fg='black',bg='cyan',
                              font=("Arial",30,"bold"))
label_Login_Page_1.pack(padx=35,pady=10,fill=BOTH,side='right')

label_Login_Page_2 = tk.Label(Login_Page_Frame_2a,text="User ID         :",
                              width=20,
                              bg='cyan',
                              font=("Arial",16,"bold"),
                              anchor="e",justify=LEFT)
label_Login_Page_2.pack(padx=50,pady=30,anchor="e")

label_Login_Page_3 = tk.Label(Login_Page_Frame_2a,text="Password    :",
                              width=20,bg='cyan',
                              font=("Arial",16,"bold"),
                              anchor="e",justify=LEFT)
label_Login_Page_3.pack(padx=50,pady=30,anchor="e")

label_Login_Page_4 = tk.Label(Login_Page_Frame_3a,text="Belum punya akun Rehab-Bot?",
                              width=30,
                              bg='cyan',
                              font=("Arial",14))
label_Login_Page_4.pack(pady=10,anchor='e')

button_Login_Page_1 = tk.Button(Login_Page_Frame_4,text="MASUK",
                                width=20,
                                fg='black',bg='yellow',
                                font=("Arial",30),
                                relief="raise",
                                command=masuk)
button_Login_Page_1.pack(padx=10,anchor='n')

button_Login_Page_2 = tk.Button(Login_Page_Frame_3b,text="BUAT AKUN BARU",
                                width=15,
                                fg='blue',bg='cyan',
                                font=("Arial",14,"bold"),
                                relief='flat')
button_Login_Page_2.pack(pady=5,anchor='w')

entry_Login_Page_1 = tk.Entry(Login_Page_Frame_2b,
                              textvar=ID,
                              width=28,
                              font=("Arial",16))
entry_Login_Page_1.pack(padx=10,pady=32,anchor='w')
entry_Login_Page_1.bind("<FocusIn>",open_onboard)

entry_Login_Page_2 = tk.Entry(Login_Page_Frame_2b,
                              textvar=PW,
                              width=28,
                              font=("Arial",16)
                              ,show="*")
entry_Login_Page_2.pack(padx=10,pady=26,anchor='w')
entry_Login_Page_2.bind("<FocusIn>",open_onboard)

button_Login_Page_3 = tk.Button(Login_Page_Frame_1b,text="Keluar\nAplikasi",
                                width=10,
                                fg='white',bg='red',
                                font=("Arial",14,"bold"),
                                relief='raise',
                                command = keluar_aplikasi)
button_Login_Page_3.pack(pady=5,padx=5)

#Start Page Frame
Start_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Start_Page_Frame.pack(padx=10,pady=10)
Start_Page_Frame.pack_propagate(False)
Start_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Start_Page_Frame_1 = tk.Frame(Start_Page_Frame,bg='cyan')
Start_Page_Frame_1.pack(padx=10,pady=10)
Start_Page_Frame_1.pack_propagate(False)
Start_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Start_Page_Frame_1a = tk.Frame(Start_Page_Frame_1,bg='cyan')
Start_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Start_Page_Frame_1a.pack_propagate(False)
Start_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Start_Page_Frame_1b = tk.Frame(Start_Page_Frame_1,bg='cyan')
Start_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Start_Page_Frame_1b.pack_propagate(False)
Start_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Start_Page_Frame_2 = tk.Frame(Start_Page_Frame,bg='cyan')
Start_Page_Frame_2.pack(padx=10,pady=10)
Start_Page_Frame_2.pack_propagate(False)
Start_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.35)

Start_Page_Frame_3 = tk.Frame(Start_Page_Frame,bg='cyan')
Start_Page_Frame_3.pack(padx=10,pady=10)
Start_Page_Frame_3.pack_propagate(False)
Start_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

label_Start_Page_1 = tk.Label(Start_Page_Frame_1a,text="SELAMAT DATANG!",
                             fg='black',bg='cyan',
                             font=("Arial",30,"bold"),
                             anchor='e')
label_Start_Page_1.pack(fill=BOTH,padx=10)

label_Start_Page_2 = tk.Label(Start_Page_Frame_2,text='"admin"',
                             fg='black',bg='cyan',
                             font=("Arial",20,"bold"))
label_Start_Page_2.pack(fill=BOTH,pady=15,padx=10,anchor='center')

label_Start_Page_3 = tk.Label(Start_Page_Frame_2,text="Alat Rehabilitasi\nEkstremitas Bawah\nBerbasis Rumah",
                             fg='black',bg='cyan',
                             font=("Arial",24,"bold"))
label_Start_Page_3.pack(fill=BOTH,pady=10,padx=10,anchor='center')

button_Start_Page_1 = tk.Button(Start_Page_Frame_3,text="MULAI",
                               width=20,
                               fg='white',bg='green',
                               font=("Arial",30),
                               relief="raise",
                               command=mulai)
button_Start_Page_1.pack(padx=10,pady=50,side="bottom")

button_Start_Page_2 = tk.Button(Start_Page_Frame_1b,text="Keluar\nAkun",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14,"bold"),
                               relief="raise",
                               command=keluar_akun)
button_Start_Page_2.pack(pady=10,padx=10,side="top")

#Home Page Frame
Home_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Home_Page_Frame.pack(padx=10,pady=10)
Home_Page_Frame.pack_propagate(False)
Home_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Home_Page_Frame_1 = tk.Frame(Home_Page_Frame,bg='cyan')
Home_Page_Frame_1.pack(padx=10,pady=10)
Home_Page_Frame_1.pack_propagate(False)
Home_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Home_Page_Frame_1a = tk.Frame(Home_Page_Frame_1,bg='cyan')
Home_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Home_Page_Frame_1a.pack_propagate(False)
Home_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Home_Page_Frame_1b = tk.Frame(Home_Page_Frame_1,bg='cyan')
Home_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Home_Page_Frame_1b.pack_propagate(False)
Home_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Home_Page_Frame_2 = tk.Frame(Home_Page_Frame,bg='cyan')
Home_Page_Frame_2.pack(padx=10,pady=10)
Home_Page_Frame_2.pack_propagate(False)
Home_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.4)

Home_Page_Frame_2a = tk.Frame(Home_Page_Frame_2,bg='cyan')
Home_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Home_Page_Frame_2a.pack_propagate(False)
Home_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.4)

Home_Page_Frame_2b = tk.Frame(Home_Page_Frame_2,bg='cyan')
Home_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Home_Page_Frame_2b.pack_propagate(False)
Home_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.4)

Home_Page_Frame_3 = tk.Frame(Home_Page_Frame,bg='cyan')
Home_Page_Frame_3.pack(padx=10,pady=10)
Home_Page_Frame_3.pack_propagate(False)
Home_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.35)

Home_Page_Frame_3a = tk.Frame(Home_Page_Frame_3,bg='cyan')
Home_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Home_Page_Frame_3a.pack_propagate(False)
Home_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.35)

Home_Page_Frame_3b = tk.Frame(Home_Page_Frame_3,bg='cyan')
Home_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Home_Page_Frame_3b.pack_propagate(False)
Home_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.35)

label_Home_Page_1 = tk.Label(Home_Page_Frame_1a,text="HALAMAN UTAMA",
                             fg='black',bg='cyan',
                             font=("Arial",30,"bold")
                             ,anchor='e')
label_Home_Page_1.pack(fill=X,pady=10,padx=10)

button_Home_Page_1 = tk.Button(Home_Page_Frame_2a,text="REHABILITASI\nPASIF",
                               width=20,
                               fg='black',bg='yellow',
                               font=("Arial",30,"bold"),
                               relief="raise",
                               command=pasif)
button_Home_Page_1.pack(padx=10,pady=10,side='bottom')

button_Home_Page_2 = tk.Button(Home_Page_Frame_2b,text="REHABILITASI\nAKTIF",
                               width=20,
                               fg='black',bg='yellow',
                               font=("Arial",30,"bold"),
                               relief="raise",
                               command=aktif)
button_Home_Page_2.pack(padx=10,pady=10,side='bottom')

label_Home_Page_2 = tk.Label(Home_Page_Frame_3a,text="Gerakan bolak-balik secara otomatis",
                             fg='black',bg='cyan',
                             font=("Arial",14))
label_Home_Page_2.pack(pady=10,padx=10,anchor='n')

label_Home_Page_3 = tk.Label(Home_Page_Frame_3b,text="Beri dorongan untuk\nmenggerakkan mesin",
                             fg='black',bg='cyan',
                             font=("Arial",14))
label_Home_Page_3.pack(pady=10,padx=10,anchor='n')

button_Home_Page_3 = tk.Button(Home_Page_Frame_1b,text="Kembali",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14),
                               relief="raise",
                               command=kembali_1)
button_Home_Page_3.pack(pady=10,padx=10)

#Pasif Page Frame
Pasif_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Pasif_Page_Frame.pack(padx=10,pady=10)
Pasif_Page_Frame.pack_propagate(False)
Pasif_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Pasif_Page_Frame_1 = tk.Frame(Pasif_Page_Frame,bg='cyan')
Pasif_Page_Frame_1.pack(padx=10,pady=10)
Pasif_Page_Frame_1.pack_propagate(False)
Pasif_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_1a = tk.Frame(Pasif_Page_Frame_1,bg='cyan')
Pasif_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Pasif_Page_Frame_1a.pack_propagate(False)
Pasif_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_1b = tk.Frame(Pasif_Page_Frame_1,bg='cyan')
Pasif_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Pasif_Page_Frame_1b.pack_propagate(False)
Pasif_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2 = tk.Frame(Pasif_Page_Frame,bg='cyan')
Pasif_Page_Frame_2.pack(padx=10,pady=10)
Pasif_Page_Frame_2.pack_propagate(False)
Pasif_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

Pasif_Page_Frame_2a = tk.Frame(Pasif_Page_Frame_2,bg='chocolate',highlightbackground='black',highlightthickness=3)
Pasif_Page_Frame_2a.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2a.pack_propagate(False)
Pasif_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.215,height=root.winfo_screenheight()*0.5)

Pasif_Page_Frame_2b = tk.Frame(Pasif_Page_Frame_2,bg='gray',highlightbackground='black',highlightthickness=3)
Pasif_Page_Frame_2b.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2b.pack_propagate(False)
Pasif_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.215,height=root.winfo_screenheight()*0.5)

Pasif_Page_Frame_2c = tk.Frame(Pasif_Page_Frame_2,bg='blue',highlightbackground='black',highlightthickness=3)
Pasif_Page_Frame_2c.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2c.pack_propagate(False)
Pasif_Page_Frame_2c.configure(width=root.winfo_screenwidth()*0.215,height=root.winfo_screenheight()*0.5)

Pasif_Page_Frame_2d = tk.Frame(Pasif_Page_Frame_2,bg='yellow',highlightbackground='black',highlightthickness=3)
Pasif_Page_Frame_2d.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d.pack_propagate(False)
Pasif_Page_Frame_2d.configure(width=root.winfo_screenwidth()*0.33,height=root.winfo_screenheight()*0.5)

Pasif_Page_Frame_2d_1 = tk.Frame(Pasif_Page_Frame_2d,bg='yellow')
Pasif_Page_Frame_2d_1.pack(padx=2,pady=2,side='top')
Pasif_Page_Frame_2d_1.pack_propagate(False)
Pasif_Page_Frame_2d_1.configure(width=root.winfo_screenwidth()*0.33,height=root.winfo_screenheight()*0.05)

Pasif_Page_Frame_2d_2 = tk.Frame(Pasif_Page_Frame_2d,bg='yellow')
Pasif_Page_Frame_2d_2.pack(padx=2,pady=2,side='top')
Pasif_Page_Frame_2d_2.pack_propagate(False)
Pasif_Page_Frame_2d_2.configure(width=root.winfo_screenwidth()*0.33,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_2a = tk.Frame(Pasif_Page_Frame_2d_2,bg='yellow')
Pasif_Page_Frame_2d_2a.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_2a.pack_propagate(False)
Pasif_Page_Frame_2d_2a.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_2b = tk.Frame(Pasif_Page_Frame_2d_2,bg='yellow')
Pasif_Page_Frame_2d_2b.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_2b.pack_propagate(False)
Pasif_Page_Frame_2d_2b.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_2c = tk.Frame(Pasif_Page_Frame_2d_2,bg='yellow')
Pasif_Page_Frame_2d_2c.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_2c.pack_propagate(False)
Pasif_Page_Frame_2d_2c.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_2d = tk.Frame(Pasif_Page_Frame_2d_2,bg='yellow')
Pasif_Page_Frame_2d_2d.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_2d.pack_propagate(False)
Pasif_Page_Frame_2d_2d.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_2e = tk.Frame(Pasif_Page_Frame_2d_2,bg='yellow')
Pasif_Page_Frame_2d_2e.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_2e.pack_propagate(False)
Pasif_Page_Frame_2d_2e.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3 = tk.Frame(Pasif_Page_Frame_2d,bg='yellow')
Pasif_Page_Frame_2d_3.pack(padx=2,pady=2,side='top')
Pasif_Page_Frame_2d_3.pack_propagate(False)
Pasif_Page_Frame_2d_3.configure(width=root.winfo_screenwidth()*0.33,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3a = tk.Frame(Pasif_Page_Frame_2d_3,bg='yellow')
Pasif_Page_Frame_2d_3a.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_3a.pack_propagate(False)
Pasif_Page_Frame_2d_3a.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3b = tk.Frame(Pasif_Page_Frame_2d_3,bg='yellow')
Pasif_Page_Frame_2d_3b.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_3b.pack_propagate(False)
Pasif_Page_Frame_2d_3b.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3c = tk.Frame(Pasif_Page_Frame_2d_3,bg='yellow')
Pasif_Page_Frame_2d_3c.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_3c.pack_propagate(False)
Pasif_Page_Frame_2d_3c.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3d = tk.Frame(Pasif_Page_Frame_2d_3,bg='yellow')
Pasif_Page_Frame_2d_3d.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_3d.pack_propagate(False)
Pasif_Page_Frame_2d_3d.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_3e = tk.Frame(Pasif_Page_Frame_2d_3,bg='yellow')
Pasif_Page_Frame_2d_3e.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_3e.pack_propagate(False)
Pasif_Page_Frame_2d_3e.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4 = tk.Frame(Pasif_Page_Frame_2d,bg='yellow')
Pasif_Page_Frame_2d_4.pack(padx=2,pady=2,side='top')
Pasif_Page_Frame_2d_4.pack_propagate(False)
Pasif_Page_Frame_2d_4.configure(width=root.winfo_screenwidth()*0.33,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4a = tk.Frame(Pasif_Page_Frame_2d_4,bg='yellow')
Pasif_Page_Frame_2d_4a.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_4a.pack_propagate(False)
Pasif_Page_Frame_2d_4a.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4b = tk.Frame(Pasif_Page_Frame_2d_4,bg='yellow')
Pasif_Page_Frame_2d_4b.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_4b.pack_propagate(False)
Pasif_Page_Frame_2d_4b.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4c = tk.Frame(Pasif_Page_Frame_2d_4,bg='yellow')
Pasif_Page_Frame_2d_4c.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_4c.pack_propagate(False)
Pasif_Page_Frame_2d_4c.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4d = tk.Frame(Pasif_Page_Frame_2d_4,bg='yellow')
Pasif_Page_Frame_2d_4d.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_4d.pack_propagate(False)
Pasif_Page_Frame_2d_4d.configure(width=root.winfo_screenwidth()*0.01,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_2d_4e = tk.Frame(Pasif_Page_Frame_2d_4,bg='yellow')
Pasif_Page_Frame_2d_4e.pack(padx=2,pady=2,side='left')
Pasif_Page_Frame_2d_4e.pack_propagate(False)
Pasif_Page_Frame_2d_4e.configure(width=root.winfo_screenwidth()*0.075,height=root.winfo_screenheight()*0.15)

Pasif_Page_Frame_3 = tk.Frame(Pasif_Page_Frame,bg='cyan')
Pasif_Page_Frame_3.pack(padx=10,pady=10)
Pasif_Page_Frame_3.pack_propagate(False)
Pasif_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.25)

Pasif_Page_Frame_3a = tk.Frame(Pasif_Page_Frame_3,bg='cyan')
Pasif_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Pasif_Page_Frame_3a.pack_propagate(False)
Pasif_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

Pasif_Page_Frame_3b = tk.Frame(Pasif_Page_Frame_3,bg='cyan')
Pasif_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Pasif_Page_Frame_3b.pack_propagate(False)
Pasif_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

label_Pasif_Page_1 = tk.Label(Pasif_Page_Frame_1a,text="REHABILITASI PASIF",
                             fg='black',bg='cyan',
                             font=("Arial",30,"bold")
                             ,anchor='e')
label_Pasif_Page_1.pack(fill=X,pady=10,padx=10)

button_Pasif_Page_1 = tk.Button(Pasif_Page_Frame_1b,text="Kembali",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14),
                               relief="raise",
                               command=kembali_2)
button_Pasif_Page_1.pack(pady=10,padx=10)

button_Pasif_Page_2 = tk.Button(Pasif_Page_Frame_3b,text="MULAI REHABILITASI",
                               width=20,
                               fg='white',bg='green',
                               font=("Arial",20,"bold"),
                               relief="raise",
                               command=mulai_rehabilitasi_pasif)
button_Pasif_Page_2.pack(pady=30,padx=10)

label_Pasif_Page_2 = tk.Label(Pasif_Page_Frame_2a,text="Sudut Maksimum",
                             fg='black',bg='chocolate',
                             font=("Arial",14,"bold"))
label_Pasif_Page_2.pack(pady=5,padx=2)

slider_Pasif_Page_1 = Scale(Pasif_Page_Frame_2a,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Pasif_Page_1.pack(padx=2,pady=2)
slider_Pasif_Page_1.bind("<Leave>",update_1)

label_Pasif_Page_3 = tk.Label(Pasif_Page_Frame_2b,text="Sudut Minimum",
                             fg='black',bg='gray',
                             font=("Arial",14,"bold"))
label_Pasif_Page_3.pack(pady=5,padx=2)

slider_Pasif_Page_2 = Scale(Pasif_Page_Frame_2b,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Pasif_Page_2.pack(padx=2,pady=5)
slider_Pasif_Page_2.bind("<Leave>",update_1)

label_Pasif_Page_4 = tk.Label(Pasif_Page_Frame_2c,text="Kecepatan Mesin",
                             fg='black',bg='blue',
                             font=("Arial",14,"bold"))
label_Pasif_Page_4.pack(pady=5,padx=2)

slider_Pasif_Page_3 = Scale(Pasif_Page_Frame_2c,
                            from_=100, to=10,
                            resolution=10,tickinterval=90,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Pasif_Page_3.pack(padx=2,pady=2)
slider_Pasif_Page_3.bind("<Leave>",update_1)

label_Pasif_Page_5 = tk.Label(Pasif_Page_Frame_2d_1,text="Durasi Rehabilitasi",
                             fg='black',bg='yellow',
                             font=("Arial",14,"bold"))
label_Pasif_Page_5.pack(pady=5,padx=2)

#Adjustable Timer
label_Pasif_Page_Timer_1 = tk.Label(Pasif_Page_Frame_2d_3a,text="00",
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))
label_Pasif_Page_Timer_1.pack(pady=2,padx=2,expand=TRUE)

label_Pasif_Page_Timer_2 = tk.Label(Pasif_Page_Frame_2d_3b,text=":",
                            fg='black',bg='yellow',
                            font=("Arial",30,"bold"))
label_Pasif_Page_Timer_2.pack(pady=2,padx=2,expand=TRUE)

label_Pasif_Page_Timer_3 = tk.Label(Pasif_Page_Frame_2d_3c,text="00",
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",30,"bold"))
label_Pasif_Page_Timer_3.pack(pady=2,padx=2,expand=TRUE)

label_Pasif_Page_Timer_4 = tk.Label(Pasif_Page_Frame_2d_3d,text=":",
                            fg='black',bg='yellow',
                            font=("Arial",30,"bold"))
label_Pasif_Page_Timer_4.pack(pady=2,padx=2,expand=TRUE)

label_Pasif_Page_Timer_5 = tk.Label(Pasif_Page_Frame_2d_3e,text="00",
                            fg='black',bg='white',highlightbackground="black",highlightthickness=3,
                            font=("Arial",28,"bold"))
label_Pasif_Page_Timer_5.pack(pady=2,padx=2,expand=TRUE)

button_Pasif_Page_Timer_1 = tk.Button(Pasif_Page_Frame_2d_2a,text="↑",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=hour_up)
button_Pasif_Page_Timer_1.pack(pady=2,padx=2,side='bottom')

button_Pasif_Page_Timer_2 = tk.Button(Pasif_Page_Frame_2d_4a,text="↓",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=hour_down)
button_Pasif_Page_Timer_2.pack(pady=2,padx=2,side='top')

button_Pasif_Page_Timer_3 = tk.Button(Pasif_Page_Frame_2d_2c,text="↑",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=minute_up)
button_Pasif_Page_Timer_3.pack(pady=2,padx=2,side='bottom')

button_Pasif_Page_Timer_4 = tk.Button(Pasif_Page_Frame_2d_4c,text="↓",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=minute_down)
button_Pasif_Page_Timer_4.pack(pady=2,padx=2,side='top')

button_Pasif_Page_Timer_5 = tk.Button(Pasif_Page_Frame_2d_2e,text="↑",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=second_up)
button_Pasif_Page_Timer_5.pack(pady=2,padx=2,side='bottom')

button_Pasif_Page_Timer_6 = tk.Button(Pasif_Page_Frame_2d_4e,text="↓",
                               width=3,
                               fg='black',bg='light gray',
                               font=("Arial",24,"bold"),
                               relief="raise",
                               command=second_down)
button_Pasif_Page_Timer_6.pack(pady=2,padx=2,side='top')

#Indicator Label
label_Pasif_Page_6 = tk.Label(Pasif_Page_Frame_3a,text="Sudut maksimum    = 0°",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Pasif_Page_6.pack(pady=2,padx=5,anchor='w')

label_Pasif_Page_7 = tk.Label(Pasif_Page_Frame_3a,text="Sudut minimum       = 0°",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Pasif_Page_7.pack(pady=2,padx=5,anchor='w')

label_Pasif_Page_8 = tk.Label(Pasif_Page_Frame_3a,text="Kecepatan mesin    = 10%",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Pasif_Page_8.pack(pady=2,padx=5,anchor='w')

label_Pasif_Page_9 = tk.Label(Pasif_Page_Frame_3a,text="Durasi rehabilitasi   = 0 jam 0 menit 0 detik",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Pasif_Page_9.pack(pady=2,padx=5,anchor='w')

#Aktif Page Frame
Aktif_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Aktif_Page_Frame.pack(padx=10,pady=10)
Aktif_Page_Frame.pack_propagate(False)
Aktif_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Aktif_Page_Frame_1 = tk.Frame(Aktif_Page_Frame,bg='cyan')
Aktif_Page_Frame_1.pack(padx=10,pady=10)
Aktif_Page_Frame_1.pack_propagate(False)
Aktif_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Aktif_Page_Frame_1a = tk.Frame(Aktif_Page_Frame_1,bg='cyan')
Aktif_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Aktif_Page_Frame_1a.pack_propagate(False)
Aktif_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Aktif_Page_Frame_1b = tk.Frame(Aktif_Page_Frame_1,bg='cyan')
Aktif_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Aktif_Page_Frame_1b.pack_propagate(False)
Aktif_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Aktif_Page_Frame_2 = tk.Frame(Aktif_Page_Frame,bg='cyan')
Aktif_Page_Frame_2.pack(padx=10,pady=10)
Aktif_Page_Frame_2.pack_propagate(False)
Aktif_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

Aktif_Page_Frame_2a = tk.Frame(Aktif_Page_Frame_2,bg='chocolate',highlightbackground='black',highlightthickness=3)
Aktif_Page_Frame_2a.pack(padx=2,pady=2,side='left')
Aktif_Page_Frame_2a.pack_propagate(False)
Aktif_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.23,height=root.winfo_screenheight()*0.5)

Aktif_Page_Frame_2b = tk.Frame(Aktif_Page_Frame_2,bg='gray',highlightbackground='black',highlightthickness=3)
Aktif_Page_Frame_2b.pack(padx=2,pady=2,side='left')
Aktif_Page_Frame_2b.pack_propagate(False)
Aktif_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.23,height=root.winfo_screenheight()*0.5)

Aktif_Page_Frame_2c = tk.Frame(Aktif_Page_Frame_2,bg='blue',highlightbackground='black',highlightthickness=3)
Aktif_Page_Frame_2c.pack(padx=2,pady=2,side='left')
Aktif_Page_Frame_2c.pack_propagate(False)
Aktif_Page_Frame_2c.configure(width=root.winfo_screenwidth()*0.23,height=root.winfo_screenheight()*0.5)

Aktif_Page_Frame_2d = tk.Frame(Aktif_Page_Frame_2,bg='yellow',highlightbackground='black',highlightthickness=3)
Aktif_Page_Frame_2d.pack(padx=2,pady=2,side='left')
Aktif_Page_Frame_2d.pack_propagate(False)
Aktif_Page_Frame_2d.configure(width=root.winfo_screenwidth()*0.23,height=root.winfo_screenheight()*0.5)

Aktif_Page_Frame_3 = tk.Frame(Aktif_Page_Frame,bg='cyan')
Aktif_Page_Frame_3.pack(padx=10,pady=10)
Aktif_Page_Frame_3.pack_propagate(False)
Aktif_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.25)

Aktif_Page_Frame_3a = tk.Frame(Aktif_Page_Frame_3,bg='cyan')
Aktif_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Aktif_Page_Frame_3a.pack_propagate(False)
Aktif_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

Aktif_Page_Frame_3b = tk.Frame(Aktif_Page_Frame_3,bg='cyan')
Aktif_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Aktif_Page_Frame_3b.pack_propagate(False)
Aktif_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

label_Aktif_Page_1 = tk.Label(Aktif_Page_Frame_1a,text="REHABILITASI AKTIF",
                             fg='black',bg='cyan',
                             font=("Arial",30,"bold")
                             ,anchor='e')
label_Aktif_Page_1.pack(fill=X,pady=10,padx=30)

button_Aktif_Page_1 = tk.Button(Aktif_Page_Frame_1b,text="Kembali",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14),
                               relief="raise",
                               command=kembali_2)
button_Aktif_Page_1.pack(pady=10,padx=10)

button_Aktif_Page_2 = tk.Button(Aktif_Page_Frame_3b,text="MULAI REHABILITASI",
                               width=20,
                               fg='white',bg='green',
                               font=("Arial",20,"bold"),
                               relief="raise",
                               command=mulai_rehabilitasi_aktif)
button_Aktif_Page_2.pack(pady=30,padx=10)

label_Aktif_Page_2 = tk.Label(Aktif_Page_Frame_2a,text="Sudut Maksimum",
                             fg='black',bg='chocolate',
                             font=("Arial",14,"bold"))
label_Aktif_Page_2.pack(pady=5,padx=2)

slider_Aktif_Page_1 = Scale(Aktif_Page_Frame_2a,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Aktif_Page_1.pack(padx=2,pady=2)
slider_Aktif_Page_1.bind("<Leave>",update_2)

label_Aktif_Page_3 = tk.Label(Aktif_Page_Frame_2b,text="Sudut Minimum",
                             fg='black',bg='gray',
                             font=("Arial",14,"bold"))
label_Aktif_Page_3.pack(pady=5,padx=2)

slider_Aktif_Page_2 = Scale(Aktif_Page_Frame_2b,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Aktif_Page_2.pack(padx=2,pady=5)
slider_Aktif_Page_2.bind("<Leave>",update_2)

label_Aktif_Page_4 = tk.Label(Aktif_Page_Frame_2c,text="Konstanta Pegas",
                             fg='black',bg='blue',
                             font=("Arial",14,"bold"))
label_Aktif_Page_4.pack(pady=5,padx=2)

entry_Aktif_Page_1 = tk.Entry(Aktif_Page_Frame_2c,
                              textvar=KP,
                              width=7,
                              font=("Arial",24),
                              justify='center')
entry_Aktif_Page_1.pack(padx=10,pady=10,expand = TRUE)
entry_Aktif_Page_1.bind("<FocusIn>",open_onboard)
entry_Aktif_Page_1.bind("<Leave>",update_2)

# slider_Aktif_Page_3 = Scale(Aktif_Page_Frame_2c,
#                             from_=2.0, to=0.0,
#                             resolution=0.01,tickinterval=2.0,
#                             length=300,width=50,sliderlength=70,
#                             orient=VERTICAL,
#                             font=("Arial",16))
# slider_Aktif_Page_3.pack(padx=2,pady=2)
# slider_Aktif_Page_3.bind("<Leave>",update_2)

label_Aktif_Page_5 = tk.Label(Aktif_Page_Frame_2d,text="Koefisien Damping",
                             fg='black',bg='yellow',
                             font=("Arial",14,"bold"))
label_Aktif_Page_5.pack(pady=5,padx=2)

entry_Aktif_Page_2 = tk.Entry(Aktif_Page_Frame_2d,
                              textvar=KD,
                              width=7,
                              font=("Arial",24),
                              justify='center')
entry_Aktif_Page_2.pack(padx=10,pady=10,expand = TRUE)
entry_Aktif_Page_2.bind("<FocusIn>",open_onboard)
entry_Aktif_Page_2.bind("<Leave>",update_2)

# slider_Aktif_Page_4 = Scale(Aktif_Page_Frame_2d,
#                             from_=2.0, to=0.0,
#                             resolution=0.01,tickinterval=2.0,
#                             length=300,width=50,sliderlength=70,
#                             orient=VERTICAL,
#                             font=("Arial",16))
# slider_Aktif_Page_4.pack(padx=2,pady=2)
# slider_Aktif_Page_4.bind("<Leave>",update_2)

label_Aktif_Page_6 = tk.Label(Aktif_Page_Frame_3a,text="Sudut maksimum    = 0°",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Aktif_Page_6.pack(pady=2,padx=5,anchor='w')

label_Aktif_Page_7 = tk.Label(Aktif_Page_Frame_3a,text="Sudut minimum       = 0°",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Aktif_Page_7.pack(pady=2,padx=5,anchor='w')

label_Aktif_Page_8 = tk.Label(Aktif_Page_Frame_3a,text="Konstanta pegas      = 0.0 N/m",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Aktif_Page_8.pack(pady=2,padx=5,anchor='w')

label_Aktif_Page_9 = tk.Label(Aktif_Page_Frame_3a,text="Koefisien damping   = 0.0 Ns/m",
                            fg='black',bg='cyan',
                            font=("Arial",14,"bold"))
label_Aktif_Page_9.pack(pady=2,padx=5,anchor='w')

#Pasif Ongoing Page Frame
Pasif_Ongoing_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Pasif_Ongoing_Page_Frame.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame.pack_propagate(False)
Pasif_Ongoing_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Pasif_Ongoing_Page_Frame_1 = tk.Frame(Pasif_Ongoing_Page_Frame,bg='cyan')
Pasif_Ongoing_Page_Frame_1.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame_1.pack_propagate(False)
Pasif_Ongoing_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Pasif_Ongoing_Page_Frame_1a = tk.Frame(Pasif_Ongoing_Page_Frame_1,bg='cyan')
Pasif_Ongoing_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_1a.pack_propagate(False)
Pasif_Ongoing_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Pasif_Ongoing_Page_Frame_1b = tk.Frame(Pasif_Ongoing_Page_Frame_1,bg='cyan')
Pasif_Ongoing_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Pasif_Ongoing_Page_Frame_1b.pack_propagate(False)
Pasif_Ongoing_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Pasif_Ongoing_Page_Frame_2 = tk.Frame(Pasif_Ongoing_Page_Frame,bg='green')
Pasif_Ongoing_Page_Frame_2.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame_2.pack_propagate(False)
Pasif_Ongoing_Page_Frame_2.configure(width=root.winfo_screenwidth()*0.75,height=root.winfo_screenheight()*0.175)

Pasif_Ongoing_Page_Frame_2a = tk.Frame(Pasif_Ongoing_Page_Frame_2,bg='green',highlightbackground="black",highlightthickness=3)
Pasif_Ongoing_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_2a.pack_propagate(False)
Pasif_Ongoing_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.175)

Pasif_Ongoing_Page_Frame_2b = tk.Frame(Pasif_Ongoing_Page_Frame_2,bg='green',highlightbackground="black",highlightthickness=3)
Pasif_Ongoing_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Pasif_Ongoing_Page_Frame_2b.pack_propagate(False)
Pasif_Ongoing_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.175)

Pasif_Ongoing_Page_Frame_2b_1 = tk.Frame(Pasif_Ongoing_Page_Frame_2b,bg='green')
Pasif_Ongoing_Page_Frame_2b_1.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_2b_1.pack_propagate(False)
Pasif_Ongoing_Page_Frame_2b_1.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.175)

Pasif_Ongoing_Page_Frame_2b_2 = tk.Frame(Pasif_Ongoing_Page_Frame_2b,bg='white',highlightbackground="black",highlightthickness=3)
Pasif_Ongoing_Page_Frame_2b_2.pack(padx=10,pady=10,side='right')
Pasif_Ongoing_Page_Frame_2b_2.pack_propagate(False)
Pasif_Ongoing_Page_Frame_2b_2.configure(width=root.winfo_screenwidth()*0.2,height=root.winfo_screenheight()*0.175)
                                     
Pasif_Ongoing_Page_Frame_3 = tk.Frame(Pasif_Ongoing_Page_Frame,bg='cyan')
Pasif_Ongoing_Page_Frame_3.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame_3.pack_propagate(False)
Pasif_Ongoing_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.1)
                                     
Pasif_Ongoing_Page_Frame_4 = tk.Frame(Pasif_Ongoing_Page_Frame,bg='white',highlightbackground='black',highlightthickness=5)
Pasif_Ongoing_Page_Frame_4.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame_4.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_4a = tk.Frame(Pasif_Ongoing_Page_Frame_4,bg='white')
Pasif_Ongoing_Page_Frame_4a.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_4a.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4a.configure(width=root.winfo_screenwidth()*0.09,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_4b = tk.Frame(Pasif_Ongoing_Page_Frame_4,bg='white')
Pasif_Ongoing_Page_Frame_4b.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_4b.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4b.configure(width=root.winfo_screenwidth()*0.04,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_4c = tk.Frame(Pasif_Ongoing_Page_Frame_4,bg='white')
Pasif_Ongoing_Page_Frame_4c.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_4c.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4c.configure(width=root.winfo_screenwidth()*0.09,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_4d = tk.Frame(Pasif_Ongoing_Page_Frame_4,bg='white')
Pasif_Ongoing_Page_Frame_4d.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_4d.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4d.configure(width=root.winfo_screenwidth()*0.04,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_4e = tk.Frame(Pasif_Ongoing_Page_Frame_4,bg='white')
Pasif_Ongoing_Page_Frame_4e.pack(padx=10,pady=10,side='left')
Pasif_Ongoing_Page_Frame_4e.pack_propagate(False)
Pasif_Ongoing_Page_Frame_4e.configure(width=root.winfo_screenwidth()*0.09,height=root.winfo_screenheight()*0.2)

Pasif_Ongoing_Page_Frame_5 = tk.Frame(Pasif_Ongoing_Page_Frame,bg='cyan')
Pasif_Ongoing_Page_Frame_5.pack(padx=10,pady=10)
Pasif_Ongoing_Page_Frame_5.pack_propagate(False)
Pasif_Ongoing_Page_Frame_5.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.3)

label_Pasif_Ongoing_Page_1 = tk.Label(Pasif_Ongoing_Page_Frame_1a,text="REHABILITASI PASIF",
                             fg='black',bg='cyan',
                             font=("Arial",24,"bold"),
                             anchor='e')
label_Pasif_Ongoing_Page_1.pack(fill=X,pady=10,padx=30)

label_Pasif_Ongoing_Page_2 = tk.Label(Pasif_Ongoing_Page_Frame_2a,text="Sudut Maksimum = 0°\n\nSudut Minimum    = 0°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))
label_Pasif_Ongoing_Page_2.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_3 = tk.Label(Pasif_Ongoing_Page_Frame_3,text="Sisa Durasi Rehabilitasi:",
                             fg='black',bg='cyan',
                             font=("Arial",18,"bold"))
label_Pasif_Ongoing_Page_3.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_4 = tk.Label(Pasif_Ongoing_Page_Frame_4a,text="00",
                             fg='black',bg='white',
                             font=("Arial",30,"bold"))
label_Pasif_Ongoing_Page_4.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_5 = tk.Label(Pasif_Ongoing_Page_Frame_4b,text=":",
                             fg='black',bg='white',
                             font=("Arial",30,"bold"))
label_Pasif_Ongoing_Page_5.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_6 = tk.Label(Pasif_Ongoing_Page_Frame_4c,text="00",
                             fg='black',bg='white',
                             font=("Arial",30,"bold"))
label_Pasif_Ongoing_Page_6.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_7 = tk.Label(Pasif_Ongoing_Page_Frame_4d,text=":",
                             fg='black',bg='white',
                             font=("Arial",30,"bold"))
label_Pasif_Ongoing_Page_7.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_8 = tk.Label(Pasif_Ongoing_Page_Frame_4e,text="00",
                             fg='black',bg='white',
                             font=("Arial",30,"bold"))
label_Pasif_Ongoing_Page_8.pack(fill=X,pady=10,padx=10,expand=TRUE)

button_Pasif_Ongoing_Page_1 = tk.Button(Pasif_Ongoing_Page_Frame_5,text="BERHENTI REHABILITASI",
                               width=25,
                               fg='white',bg='red',
                               font=("Arial",20,"bold"),
                               relief="raise",
                               command=berhenti_rehabilitasi_pasif)
button_Pasif_Ongoing_Page_1.pack(pady=10,padx=10,expand=TRUE)

button_Pasif_Ongoing_Page_2 = tk.Button(Pasif_Ongoing_Page_Frame_1b,text="Ubah Nilai\nSudut",
                               width=15,
                               fg='black',bg='yellow',
                               font=("Arial",14,"bold"),
                               relief="raise",
                               command=ubah_rehabilitasi_pasif)
button_Pasif_Ongoing_Page_2.pack(pady=10,padx=10)

label_Pasif_Ongoing_Page_9 = tk.Label(Pasif_Ongoing_Page_Frame_2b_1,text="Pembacaan Sudut :",
                             fg='white',bg='green',
                             font=("Arial",14,"bold"))
label_Pasif_Ongoing_Page_9.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

label_Pasif_Ongoing_Page_10 = tk.Label(Pasif_Ongoing_Page_Frame_2b_2,text="120°",
                             fg='black',bg='white',
                             font=("Arial",20,"bold"))
label_Pasif_Ongoing_Page_10.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

#Aktif Ongoing Page Frame
Aktif_Ongoing_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Aktif_Ongoing_Page_Frame.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame.pack_propagate(False)
Aktif_Ongoing_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Aktif_Ongoing_Page_Frame_1 = tk.Frame(Aktif_Ongoing_Page_Frame,bg='cyan')
Aktif_Ongoing_Page_Frame_1.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame_1.pack_propagate(False)
Aktif_Ongoing_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Aktif_Ongoing_Page_Frame_1a = tk.Frame(Aktif_Ongoing_Page_Frame_1,bg='cyan')
Aktif_Ongoing_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Aktif_Ongoing_Page_Frame_1a.pack_propagate(False)
Aktif_Ongoing_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Aktif_Ongoing_Page_Frame_1b = tk.Frame(Aktif_Ongoing_Page_Frame_1,bg='cyan')
Aktif_Ongoing_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Aktif_Ongoing_Page_Frame_1b.pack_propagate(False)
Aktif_Ongoing_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Aktif_Ongoing_Page_Frame_2 = tk.Frame(Aktif_Ongoing_Page_Frame,bg='green')
Aktif_Ongoing_Page_Frame_2.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame_2.pack_propagate(False)
Aktif_Ongoing_Page_Frame_2.configure(width=root.winfo_screenwidth()*0.75,height=root.winfo_screenheight()*0.175)

Aktif_Ongoing_Page_Frame_2a = tk.Frame(Aktif_Ongoing_Page_Frame_2,bg='green',highlightbackground="black",highlightthickness=3)
Aktif_Ongoing_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Aktif_Ongoing_Page_Frame_2a.pack_propagate(False)
Aktif_Ongoing_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.175)

Aktif_Ongoing_Page_Frame_2b = tk.Frame(Aktif_Ongoing_Page_Frame_2,bg='green',highlightbackground="black",highlightthickness=3)
Aktif_Ongoing_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Aktif_Ongoing_Page_Frame_2b.pack_propagate(False)
Aktif_Ongoing_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.175)

Aktif_Ongoing_Page_Frame_2b_1 = tk.Frame(Aktif_Ongoing_Page_Frame_2b,bg='green')
Aktif_Ongoing_Page_Frame_2b_1.pack(padx=10,pady=10,side='left')
Aktif_Ongoing_Page_Frame_2b_1.pack_propagate(False)
Aktif_Ongoing_Page_Frame_2b_1.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.175)

Aktif_Ongoing_Page_Frame_2b_2 = tk.Frame(Aktif_Ongoing_Page_Frame_2b,bg='white',highlightbackground="black",highlightthickness=3)
Aktif_Ongoing_Page_Frame_2b_2.pack(padx=10,pady=10,side='right')
Aktif_Ongoing_Page_Frame_2b_2.pack_propagate(False)
Aktif_Ongoing_Page_Frame_2b_2.configure(width=root.winfo_screenwidth()*0.2,height=root.winfo_screenheight()*0.175)
                                     
Aktif_Ongoing_Page_Frame_3 = tk.Frame(Aktif_Ongoing_Page_Frame,bg='cyan')
Aktif_Ongoing_Page_Frame_3.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame_3.pack_propagate(False)
Aktif_Ongoing_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.1)
                                     
Aktif_Ongoing_Page_Frame_4 = tk.Frame(Aktif_Ongoing_Page_Frame,bg='white',highlightbackground='black',highlightthickness=5)
Aktif_Ongoing_Page_Frame_4.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame_4.pack_propagate(False)
Aktif_Ongoing_Page_Frame_4.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.2)

Aktif_Ongoing_Page_Frame_5 = tk.Frame(Aktif_Ongoing_Page_Frame,bg='cyan')
Aktif_Ongoing_Page_Frame_5.pack(padx=10,pady=10)
Aktif_Ongoing_Page_Frame_5.pack_propagate(False)
Aktif_Ongoing_Page_Frame_5.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.35)

label_Aktif_Ongoing_Page_1 = tk.Label(Aktif_Ongoing_Page_Frame_1a,text="REHABILITASI AKTIF",
                             fg='black',bg='cyan',
                             font=("Arial",30,"bold"),
                             anchor='e')
label_Aktif_Ongoing_Page_1.pack(fill=X,pady=10)

label_Aktif_Ongoing_Page_2 = tk.Label(Aktif_Ongoing_Page_Frame_2a,text="Sudut Maksimum = 0°\n\nSudut Minimum    = 0°",
                             fg='white',bg='green',
                             font=("Arial",12,"bold"))
label_Aktif_Ongoing_Page_2.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

label_Aktif_Ongoing_Page_3 = tk.Label(Aktif_Ongoing_Page_Frame_3,text="Banyak Perulangan Gerakan Rehabilitasi:",
                             fg='black',bg='cyan',
                             font=("Arial",18,"bold"))
label_Aktif_Ongoing_Page_3.pack(fill=X,pady=10,padx=10,expand=TRUE)

label_Aktif_Ongoing_Page_4 = tk.Label(Aktif_Ongoing_Page_Frame_4,text="0",
                             fg='black',bg='white',
                             font=("Arial",50,"bold"))
label_Aktif_Ongoing_Page_4.pack(fill=X,pady=10,padx=10,expand=TRUE)

button_Aktif_Ongoing_Page_1 = tk.Button(Aktif_Ongoing_Page_Frame_5,text="BERHENTI REHABILITASI",
                               width=25,
                               fg='white',bg='red',
                               font=("Arial",20,"bold"),
                               relief="raise",
                                command=berhenti_rehabilitasi_aktif)
button_Aktif_Ongoing_Page_1.pack(pady=10,padx=10,expand=TRUE)

button_Aktif_Ongoing_Page_2 = tk.Button(Aktif_Ongoing_Page_Frame_1b,text="Ubah Nilai\nSudut",
                               width=15,
                               fg='black',bg='yellow',
                               font=("Arial",14,"bold"),
                               relief="raise",
                                command=ubah_rehabilitasi_aktif)
button_Aktif_Ongoing_Page_2.pack(pady=10,padx=10)

label_Aktif_Ongoing_Page_9 = tk.Label(Aktif_Ongoing_Page_Frame_2b_1,text="Pembacaan Sudut :",
                             fg='white',bg='green',
                             font=("Arial",14,"bold"))
label_Aktif_Ongoing_Page_9.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

label_Aktif_Ongoing_Page_10 = tk.Label(Aktif_Ongoing_Page_Frame_2b_2,text="120°",
                             fg='black',bg='white',
                             font=("Arial",20,"bold"))
label_Aktif_Ongoing_Page_10.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

# Pasif_Ubah_Page_Frame
Pasif_Ubah_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Pasif_Ubah_Page_Frame.pack(padx=10,pady=10)
Pasif_Ubah_Page_Frame.pack_propagate(False)
Pasif_Ubah_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Pasif_Ubah_Page_Frame_1 = tk.Frame(Pasif_Ubah_Page_Frame,bg='cyan')
Pasif_Ubah_Page_Frame_1.pack(padx=10,pady=10)
Pasif_Ubah_Page_Frame_1.pack_propagate(False)
Pasif_Ubah_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Pasif_Ubah_Page_Frame_1a = tk.Frame(Pasif_Ubah_Page_Frame_1,bg='cyan')
Pasif_Ubah_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Pasif_Ubah_Page_Frame_1a.pack_propagate(False)
Pasif_Ubah_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Pasif_Ubah_Page_Frame_1b = tk.Frame(Pasif_Ubah_Page_Frame_1,bg='cyan')
Pasif_Ubah_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Pasif_Ubah_Page_Frame_1b.pack_propagate(False)
Pasif_Ubah_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Pasif_Ubah_Page_Frame_2 = tk.Frame(Pasif_Ubah_Page_Frame,bg='cyan')
Pasif_Ubah_Page_Frame_2.pack(padx=10,pady=10)
Pasif_Ubah_Page_Frame_2.pack_propagate(False)
Pasif_Ubah_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2a = tk.Frame(Pasif_Ubah_Page_Frame_2,bg='chocolate',highlightbackground='black',highlightthickness=5)
Pasif_Ubah_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Pasif_Ubah_Page_Frame_2a.pack_propagate(False)
Pasif_Ubah_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2a_1 = tk.Frame(Pasif_Ubah_Page_Frame_2a,bg='chocolate')
Pasif_Ubah_Page_Frame_2a_1.pack(padx=10,pady=10,side='left')
Pasif_Ubah_Page_Frame_2a_1.pack_propagate(False)
Pasif_Ubah_Page_Frame_2a_1.configure(width=root.winfo_screenwidth()*0.15,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2a_2 = tk.Frame(Pasif_Ubah_Page_Frame_2a,bg='chocolate')
Pasif_Ubah_Page_Frame_2a_2.pack(padx=10,pady=10,side='right')
Pasif_Ubah_Page_Frame_2a_2.pack_propagate(False)
Pasif_Ubah_Page_Frame_2a_2.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2b = tk.Frame(Pasif_Ubah_Page_Frame_2,bg='gray',highlightbackground='black',highlightthickness=5)
Pasif_Ubah_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Pasif_Ubah_Page_Frame_2b.pack_propagate(False)
Pasif_Ubah_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2b_1 = tk.Frame(Pasif_Ubah_Page_Frame_2b,bg='gray')
Pasif_Ubah_Page_Frame_2b_1.pack(padx=10,pady=10,side='left')
Pasif_Ubah_Page_Frame_2b_1.pack_propagate(False)
Pasif_Ubah_Page_Frame_2b_1.configure(width=root.winfo_screenwidth()*0.15,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_2b_2 = tk.Frame(Pasif_Ubah_Page_Frame_2b,bg='gray')
Pasif_Ubah_Page_Frame_2b_2.pack(padx=10,pady=10,side='right')
Pasif_Ubah_Page_Frame_2b_2.pack_propagate(False)
Pasif_Ubah_Page_Frame_2b_2.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.5)

Pasif_Ubah_Page_Frame_3 = tk.Frame(Pasif_Ubah_Page_Frame,bg='cyan')
Pasif_Ubah_Page_Frame_3.pack(padx=10,pady=10)
Pasif_Ubah_Page_Frame_3.pack_propagate(False)
Pasif_Ubah_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.25)

Pasif_Ubah_Page_Frame_3a = tk.Frame(Pasif_Ubah_Page_Frame_3,bg='cyan')
Pasif_Ubah_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Pasif_Ubah_Page_Frame_3a.pack_propagate(False)
Pasif_Ubah_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

Pasif_Ubah_Page_Frame_3b = tk.Frame(Pasif_Ubah_Page_Frame_3,bg='cyan')
Pasif_Ubah_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Pasif_Ubah_Page_Frame_3b.pack_propagate(False)
Pasif_Ubah_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.4,height=root.winfo_screenheight()*0.25)

label_Pasif_Ubah_Page_1 = tk.Label(Pasif_Ubah_Page_Frame_1a,text="Ubah Sudut Maksimum atau Minimum",
                             fg='black',bg='cyan',
                             font=("Arial",18,"bold")
                             ,anchor='e')
label_Pasif_Ubah_Page_1.pack(fill=X,pady=10)

button_Pasif_Ubah_Page_1 = tk.Button(Pasif_Ubah_Page_Frame_1b,text="Kembali",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14),
                               relief="raise",
                               command=kembali_3)
button_Pasif_Ubah_Page_1.pack(pady=10,padx=10)

label_Pasif_Ubah_Page_2 = tk.Label(Pasif_Ubah_Page_Frame_2a_2,text="Sudut Maksimum Baru",
                             fg='black',bg='chocolate',
                             font=("Arial",12,"bold"))
label_Pasif_Ubah_Page_2.pack(pady=5,padx=2)

slider_Pasif_Ubah_Page_1 = Scale(Pasif_Ubah_Page_Frame_2a_2,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Pasif_Ubah_Page_1.pack(padx=2,pady=2)
slider_Pasif_Ubah_Page_1.bind("<Leave>",update_3)

label_Pasif_Ubah_Page_3 = tk.Label(Pasif_Ubah_Page_Frame_2b_2,text="Sudut Minimum Baru",
                             fg='black',bg='gray',
                             font=("Arial",12,"bold"))
label_Pasif_Ubah_Page_3.pack(pady=5,padx=2)

slider_Pasif_Ubah_Page_2 = Scale(Pasif_Ubah_Page_Frame_2b_2,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Pasif_Ubah_Page_2.pack(padx=2,pady=5)
slider_Pasif_Ubah_Page_2.bind("<Leave>",update_3)

label_Pasif_Ubah_Page_4 = tk.Label(Pasif_Ubah_Page_Frame_2a_1,text="Sudut Maksimum\nSebelumnya = °",
                            fg='black',bg='chocolate',
                            font=("Arial",10))
label_Pasif_Ubah_Page_4.pack(pady=5,padx=2,expand=TRUE)

label_Pasif_Ubah_Page_5 = tk.Label(Pasif_Ubah_Page_Frame_2b_1,text="Sudut Minimum\nSebelumnya = °",
                            fg='black',bg='gray',
                            font=("Arial",10))
label_Pasif_Ubah_Page_5.pack(pady=5,padx=2,expand=TRUE)

label_Pasif_Ubah_Page_6 = tk.Label(Pasif_Ubah_Page_Frame_3a,text="Sudut Maksimum Baru = 0°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))
label_Pasif_Ubah_Page_6.pack(pady=5,padx=2,anchor='w')

label_Pasif_Ubah_Page_7 = tk.Label(Pasif_Ubah_Page_Frame_3a,text="Sudut Minimum Baru    = 0°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))
label_Pasif_Ubah_Page_7.pack(pady=5,padx=2,anchor='w')

button_Pasif_Ubah_Page_2 = tk.Button(Pasif_Ubah_Page_Frame_3b,text="UBAH",
                               width=10,
                               fg='white',bg='green',
                               font=("Arial",20,"bold"),
                               relief="raise",
                               command=ubah_rehabilitasi_pasif_confirmed)
button_Pasif_Ubah_Page_2.pack(pady=30,padx=10)

# Aktif_Ubah_Page_Frame
Aktif_Ubah_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Aktif_Ubah_Page_Frame.pack(padx=10,pady=10)
Aktif_Ubah_Page_Frame.pack_propagate(False)
Aktif_Ubah_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Aktif_Ubah_Page_Frame_1 = tk.Frame(Aktif_Ubah_Page_Frame,bg='cyan')
Aktif_Ubah_Page_Frame_1.pack(padx=10,pady=10)
Aktif_Ubah_Page_Frame_1.pack_propagate(False)
Aktif_Ubah_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.15)

Aktif_Ubah_Page_Frame_1a = tk.Frame(Aktif_Ubah_Page_Frame_1,bg='cyan')
Aktif_Ubah_Page_Frame_1a.pack(padx=10,pady=10,side='left')
Aktif_Ubah_Page_Frame_1a.pack_propagate(False)
Aktif_Ubah_Page_Frame_1a.configure(width=root.winfo_screenwidth()*0.7,height=root.winfo_screenheight()*0.15)

Aktif_Ubah_Page_Frame_1b = tk.Frame(Aktif_Ubah_Page_Frame_1,bg='cyan')
Aktif_Ubah_Page_Frame_1b.pack(padx=10,pady=10,side='right')
Aktif_Ubah_Page_Frame_1b.pack_propagate(False)
Aktif_Ubah_Page_Frame_1b.configure(width=root.winfo_screenwidth()*0.3,height=root.winfo_screenheight()*0.15)

Aktif_Ubah_Page_Frame_2 = tk.Frame(Aktif_Ubah_Page_Frame,bg='cyan')
Aktif_Ubah_Page_Frame_2.pack(padx=10,pady=10)
Aktif_Ubah_Page_Frame_2.pack_propagate(False)
Aktif_Ubah_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2a = tk.Frame(Aktif_Ubah_Page_Frame_2,bg='chocolate',highlightbackground='black',highlightthickness=5)
Aktif_Ubah_Page_Frame_2a.pack(padx=10,pady=10,side='left')
Aktif_Ubah_Page_Frame_2a.pack_propagate(False)
Aktif_Ubah_Page_Frame_2a.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2a_1 = tk.Frame(Aktif_Ubah_Page_Frame_2a,bg='chocolate')
Aktif_Ubah_Page_Frame_2a_1.pack(padx=10,pady=10,side='left')
Aktif_Ubah_Page_Frame_2a_1.pack_propagate(False)
Aktif_Ubah_Page_Frame_2a_1.configure(width=root.winfo_screenwidth()*0.15,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2a_2 = tk.Frame(Aktif_Ubah_Page_Frame_2a,bg='chocolate')
Aktif_Ubah_Page_Frame_2a_2.pack(padx=10,pady=10,side='right')
Aktif_Ubah_Page_Frame_2a_2.pack_propagate(False)
Aktif_Ubah_Page_Frame_2a_2.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2b = tk.Frame(Aktif_Ubah_Page_Frame_2,bg='gray',highlightbackground='black',highlightthickness=5)
Aktif_Ubah_Page_Frame_2b.pack(padx=10,pady=10,side='right')
Aktif_Ubah_Page_Frame_2b.pack_propagate(False)
Aktif_Ubah_Page_Frame_2b.configure(width=root.winfo_screenwidth()*0.45,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2b_1 = tk.Frame(Aktif_Ubah_Page_Frame_2b,bg='gray')
Aktif_Ubah_Page_Frame_2b_1.pack(padx=10,pady=10,side='left')
Aktif_Ubah_Page_Frame_2b_1.pack_propagate(False)
Aktif_Ubah_Page_Frame_2b_1.configure(width=root.winfo_screenwidth()*0.15,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_2b_2 = tk.Frame(Aktif_Ubah_Page_Frame_2b,bg='gray')
Aktif_Ubah_Page_Frame_2b_2.pack(padx=10,pady=10,side='right')
Aktif_Ubah_Page_Frame_2b_2.pack_propagate(False)
Aktif_Ubah_Page_Frame_2b_2.configure(width=root.winfo_screenwidth()*0.25,height=root.winfo_screenheight()*0.5)

Aktif_Ubah_Page_Frame_3 = tk.Frame(Aktif_Ubah_Page_Frame,bg='cyan')
Aktif_Ubah_Page_Frame_3.pack(padx=10,pady=10)
Aktif_Ubah_Page_Frame_3.pack_propagate(False)
Aktif_Ubah_Page_Frame_3.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.25)

Aktif_Ubah_Page_Frame_3a = tk.Frame(Aktif_Ubah_Page_Frame_3,bg='cyan')
Aktif_Ubah_Page_Frame_3a.pack(padx=10,pady=10,side='left')
Aktif_Ubah_Page_Frame_3a.pack_propagate(False)
Aktif_Ubah_Page_Frame_3a.configure(width=root.winfo_screenwidth()*0.5,height=root.winfo_screenheight()*0.25)

Aktif_Ubah_Page_Frame_3b = tk.Frame(Aktif_Ubah_Page_Frame_3,bg='cyan')
Aktif_Ubah_Page_Frame_3b.pack(padx=10,pady=10,side='right')
Aktif_Ubah_Page_Frame_3b.pack_propagate(False)
Aktif_Ubah_Page_Frame_3b.configure(width=root.winfo_screenwidth()*0.4,height=root.winfo_screenheight()*0.25)

label_Aktif_Ubah_Page_1 = tk.Label(Aktif_Ubah_Page_Frame_1a,text="Ubah Sudut Maksimum atau Minimum",
                             fg='black',bg='cyan',
                             font=("Arial",18,"bold")
                             ,anchor='e')
label_Aktif_Ubah_Page_1.pack(fill=X,pady=10)

button_Aktif_Ubah_Page_1 = tk.Button(Aktif_Ubah_Page_Frame_1b,text="Kembali",
                               width=10,
                               fg='white',bg='red',
                               font=("Arial",14),
                               relief="raise",
                               command=kembali_4)
button_Aktif_Ubah_Page_1.pack(pady=10,padx=10)

label_Aktif_Ubah_Page_2 = tk.Label(Aktif_Ubah_Page_Frame_2a_2,text="Sudut Maksimum Baru",
                             fg='black',bg='chocolate',
                             font=("Arial",12,"bold"))
label_Aktif_Ubah_Page_2.pack(pady=5,padx=2)

slider_Aktif_Ubah_Page_1 = Scale(Aktif_Ubah_Page_Frame_2a_2,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Aktif_Ubah_Page_1.pack(padx=2,pady=2)
slider_Aktif_Ubah_Page_1.bind("<Leave>",update_3)

label_Aktif_Ubah_Page_3 = tk.Label(Aktif_Ubah_Page_Frame_2b_2,text="Sudut Minimum Baru",
                             fg='black',bg='gray',
                             font=("Arial",12,"bold"))
label_Aktif_Ubah_Page_3.pack(pady=5,padx=2)

slider_Aktif_Ubah_Page_2 = Scale(Aktif_Ubah_Page_Frame_2b_2,
                            from_=120, to=-10,
                            resolution=5,tickinterval=120,
                            length=300,width=50,sliderlength=70,
                            orient=VERTICAL,
                            font=("Arial",16))
slider_Aktif_Ubah_Page_2.pack(padx=2,pady=5)
slider_Aktif_Ubah_Page_2.bind("<Leave>",update_3)

label_Aktif_Ubah_Page_4 = tk.Label(Aktif_Ubah_Page_Frame_2a_1,text="Sudut Maksimum\nSebelumnya = °",
                            fg='black',bg='chocolate',
                            font=("Arial",10))
label_Aktif_Ubah_Page_4.pack(pady=5,padx=2,expand=TRUE)

label_Aktif_Ubah_Page_5 = tk.Label(Aktif_Ubah_Page_Frame_2b_1,text="Sudut Minimum\nSebelumnya = °",
                            fg='black',bg='gray',
                            font=("Arial",10))
label_Aktif_Ubah_Page_5.pack(pady=5,padx=2,expand=TRUE)

label_Aktif_Ubah_Page_6 = tk.Label(Aktif_Ubah_Page_Frame_3a,text="Sudut Maksimum Baru = 0°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))
label_Aktif_Ubah_Page_6.pack(pady=5,padx=2,anchor='w')

label_Aktif_Ubah_Page_7 = tk.Label(Aktif_Ubah_Page_Frame_3a,text="Sudut Minimum Baru    = 0°",
                             fg='black',bg='cyan',
                             font=("Arial",14,"bold"))
label_Aktif_Ubah_Page_7.pack(pady=5,padx=2,anchor='w')

button_Aktif_Ubah_Page_2 = tk.Button(Aktif_Ubah_Page_Frame_3b,text="UBAH",
                               width=10,
                               fg='white',bg='green',
                               font=("Arial",20,"bold"),
                               relief="raise",
                               command=ubah_rehabilitasi_aktif_confirmed)
button_Aktif_Ubah_Page_2.pack(pady=30,padx=10)

# Finish_Page_Frame
Finish_Page_Frame = tk.Frame(Main_Frame,bg='cyan')
Finish_Page_Frame.pack(padx=10,pady=10)
Finish_Page_Frame.pack_propagate(False)
Finish_Page_Frame.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight())

Finish_Page_Frame_1 = tk.Frame(Finish_Page_Frame,bg='cyan')
Finish_Page_Frame_1.pack()
Finish_Page_Frame_1.pack_propagate(False)
Finish_Page_Frame_1.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

Finish_Page_Frame_2 = tk.Frame(Finish_Page_Frame,bg='cyan')
Finish_Page_Frame_2.pack()
Finish_Page_Frame_2.pack_propagate(False)
Finish_Page_Frame_2.configure(width=root.winfo_screenwidth(),height=root.winfo_screenheight()*0.5)

label_Finish_Page_1 = tk.Label(Finish_Page_Frame_1,text="REHABILITASI SELESAI",
                             fg='black',bg='cyan',
                             font=("Arial",40,"bold"))
label_Finish_Page_1.pack(fill=BOTH,pady=10,padx=10,expand=TRUE)

button_Finish_Page_1 = tk.Button(Finish_Page_Frame_2,text="KEMBALI",
                               width=20,
                               fg='black',bg='yellow',
                               font=("Arial",30,"bold"),
                               relief="raise",
                               command=return_to_start_page)
button_Finish_Page_1.pack(pady=10,padx=10)

# Collecting all frames
frames = [
    Login_Page_Frame,
    Start_Page_Frame,
    Home_Page_Frame,
    Pasif_Page_Frame,
    Aktif_Page_Frame,
    Pasif_Ongoing_Page_Frame,
    Aktif_Ongoing_Page_Frame,
    Pasif_Ubah_Page_Frame,
    Aktif_Ubah_Page_Frame,
    Finish_Page_Frame,
]

root.mainloop()