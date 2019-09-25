
# TKINTER
from tkinter import *               # Enables pythons GUI functions
from tkinter import messagebox, filedialog # Enables pythons GUI message boxes

from PIL import Image, ImageTk      # Enables pillow library for importing images
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) # Import Tkinter interface for figures
from struct import pack 

# MATPLOTLIB - Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib import style

# NUMPY
import numpy as np                  # Enables multi-dimentional arrays and matrices

# WAVE
import wave # Used for interfacing with .wav files

# PYAUDIO
import pyaudio # Used for sound playback

# MATLAB
import matlab.engine # Used for neural network setup

# MISC
import time
from time import sleep
import threading
import os
import datetime
from shutil import copyfile
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart

# Custom Libraries
from scripts import bt_server_v4 as bt # custom bluetooth receiver code

# Get relative path to file
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, r'heart_sounds\CPR_Works_Heart_Sounds\Normal[2].wav')

# Open audio file
wave_read = wave.open(filename, 'rb')

# This signal is used for plotting
signal = wave_read.readframes(-1)
signal = np.fromstring(signal, 'Int16')

# Playback sound
# define stream chunk   
chunk = 1629

class Splash(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)


        self.title("Loading Screen")        # Set the title
        self.xres = parent.winfo_width()    # Parent width
        self.yres = parent.winfo_height()   # Parent height
        self.xpos = parent.winfo_x()        # Parent x-position
        self.ypos = parent.winfo_y()        # Parent y-position
        
        # Scale the top level relative to the parent
        self.geometry("%dx%d+%d+%d" % (200,200,self.xpos + self.xres/2 - 100, self.ypos + self.yres/2 -100)) 

        # Load information for the gif
        self.loadname = os.path.join(dirname,r'icons\200.gif') # Get gif names
        self.frames = [ImageTk.PhotoImage(file=self.loadname,format = 'gif -index %i' %(i)) for i in range(111)] # Get all frames
        self.gif_img = Label(self, image = self.frames[0], bg = "White") # set the gif to the first frame
        self.gif_img.place(x = 0,y = 0) # place the gif on the top level

        # Load Additional Images
        self.goodname = os.path.join(dirname,r'icons\good.jpg') 
        self.badname = os.path.join(dirname,r'icons\bad.jpg')

        # Update the configure gui
        self.configure(bg = "White")
        self.update()

        # Additional steps for updating gif
        # gif_thread=threading.Thread(target=self.update_gif(0))
        # gif_thread.start()
        # self.after(100, self.update_gif, 0) # After is blocked by matlab

    def update_gif(self,i):
        i +=1
        # leave case
        if (i<100):
            print("gif -index %d" %(i))
            self.gif_img.configure(image = self.frames[i])
            self.gif_img.after(100, self.update_gif, i%110) 
    
# Design the GUI
class OrisApp:
    def __init__(self, master):

        self.master = master                    # Set the root as a class instance
        self.eng = matlab.engine.start_matlab() # Open Matlab (bottleneck)
        self.server=bt.BtServer()               # Set socket to bind
        master.title("Oris Auscultations")      # Set the title
        
        self.entry_list = []    # Holds entry values
        self.label_list = []    # Holds label values
        
        self.patient_list_e = []    # Holds entry values for patient
        self.patient_list_l = []    # Holds label values for patient
        self.color_codes = []       # Hold colour code options
        
        # List output of neural network
        self.string_list1 = [['m_RR', 'sd_RR', 'mean_IntS1', 'sd_IntS1'],
                   ['mean_IntS2','sd_IntS2', 'mean_IntSys', 'sd_IntSys'],
                   ['mean_IntDia', 'sd_IntDia', 'm_Ratio_SysRR', 'sd_Ratio_SysRR'],
                   ['m_Ratio_DiaRR','sd_Ratio_DiaRR', 'm_Ratio_SysDia', 'sd_Ratio_SysDia'],
                   ['m_Amp_SysS1','sd_Amp_SysS1', 'm_Amp_DiaS2', 'sd_Amp_DiaS2'],
                   ['mSK_S1','sdSK_S1', 'mSK_Sys','sdSK_Sys']]

        # List information of the patient
        self.string_list2 = ["First Name: ",
                        "Last Name: ",
                        "Gender: ",
                        "Age: ",
                        "Email:",
                        "Insurance Number: ",
                        "Phone Number: ",
                        "Address: ",
                        "Practitioner: ",
                        "Hospital Name: ",
                        "Comments",
                        ""]

        self.color_codes.append("#121212") # Black
        self.color_codes.append("#FFFFFF") # White
        self.color_codes.append("#535353") # Gray

        # GRID (0,0) -> (0,6)
        ############################################################################################################
        
        self.now = datetime.datetime.now()
        self.ddmmyy = Label(master, text="%d.%d.%d" % (self.now.day, self.now.month, self.now.year), state='normal',bg = self.color_codes[1])
        self.ddmmyy.grid(row = 0, column = 0,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)

        # Bluetooth
        self.bt_status = StringVar()
        self.bt_status.set("Status: Not Connected")
        
        if self.server.address == "":
            self.bt_status.set("Status: Not Connected")
        else:
            self.bt_status.set("Status: Connected")            

        self.health_status = StringVar()
        self.health_status.set("Analysis: Undefined")
        
        # Connection Status
        self.labelBT = Label(master, text=self.bt_status.get(), state='normal',bg = self.color_codes[1])
        self.labelBT.grid(row = 0, column = 2,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)
        
        # Bluetooth
        self.button7 = Button(master, text = "Bluetooth", command = self.enableBluetooth)
        self.button7.grid(row = 0, column = 3,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)
        
        # BPM
        self.labelBPM = Label(master, text="BPM: ", state='normal',bg = self.color_codes[1])
        self.labelBPM.grid(row = 0, column = 5,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)

        # Status
        self.labelStatus = Label(master, text = self.health_status.get(), state='normal',bg = self.color_codes[1])
        self.labelStatus.grid(row = 0, column = 6,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)

        # Live plot 
        self.buttonLivePlt = Button(master, text = "Live Plot", command = self.liveplot)
        self.buttonLivePlt.grid(row = 0, column = 8,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)

        # GRID (1,0) -> (2,1) - LOGO
        ############################################################################################################
        self.init_r = 1 # Initial row for this section
        self.init_c = 0 # Initial col for this section

        # Initalize canvas 
        self.display = Canvas(master, bd=0, bg = self.color_codes[1], highlightthickness=0,width=226, height=150)
        self.display.grid(row = self.init_r, column = self.init_c,columnspan = 2, rowspan=1, sticky=W+E+N+S, padx = 5, pady=5)

        #  Create logo 
        self.logoname = os.path.join(dirname,r'icons\logo_design_white_bg.png')
        self.logo = Image.open(self.logoname)
        self.logo_width, self.logo_height = self.logo.size;
        self.resized = self.logo.resize((226,150),Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.resized)

        self.display.create_image(0, 30, image = self.img, anchor=NW)

        # GRID (2,0) -> (14,1) - PATIENT INFO
        ############################################################################################################
        self.init_r = 2 # Initial row for this section
        self.init_c = 0 # Initial col for this section


        # for labeling entries
        self.entry_counter = 0
        
        for r in range(self.init_r,self.init_r + 12):
            
           # Create a tkinter objects
           # entries 0-12
           self.patient_list_e.append(Entry(master, text="entry " + str(self.entry_counter), state='normal',bg = self.color_codes[1]))
           self.patient_list_l.append(Label(master, text= self.string_list2[r-self.init_r],bg = self.color_codes[1]))

           self.entry_counter = self.entry_counter + 1
           
           # Place the object onto the grid
           self.patient_list_l[r-self.init_r].grid(row = r,column = 0, sticky = SW)
           self.patient_list_e[r-self.init_r].grid(row = r,column = 1, sticky = SW)
           
           # Configure options
           self.patient_list_l[r-self.init_r].config(font=("Times New Roman", 10))
        
        # GRID (1,2) -> (7,10) - GRAPH
        ############################################################################################################
        self.init_r = 1 # Initial row for this section
        self.init_c = 2 # Initial col for this section

        # Create graph figure
        style.use('ggplot')
        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.plt = self.fig.subplots()
        
        # (nchannels, sampwidth, framerate, nframes, comptype, compname)
        self.wave_params = wave_read.getparams()

        nframes = self.wave_params[3]
        rate = self.wave_params[2]
        duration = nframes / float(rate)
        x = np.linspace(0,duration,nframes)
        
        self.plt.plot(x,signal)
        self.plt.set_xlabel('Time (Seconds)')
        self.plt.set_ylabel('.Wav file Magnitude')
    
        # Create a Canvas for the graph
        self.Canvas1 = FigureCanvasTkAgg(self.fig, master=master)
        self.Canvas1.draw()
        self.Canvas1.get_tk_widget().grid(row = self.init_r,column = self.init_c, columnspan=20, rowspan=6,
                    sticky=W+E+N+S, padx = 5, pady=5)

        # GRID (8,2):(14,11)
        ############################################################################################################
        self.init_r = 8 # Initial row for this section
        self.init_c = 1 # Initial col for this section, this is multiplied by 2

        # Create Entries and Labels for the Data
        for r in range(self.init_r,self.init_r+6):

           # list of entries per row
           self.entry_rows = []
           self.label_rows = []
           for c in range(self.init_c,self.init_c+4):
              
              # Create a tkinter objects
              self.entry_rows.append(Entry(master, text="entry " + str(self.entry_counter), state='disabled', bg = self.color_codes[1]))
              self.label_rows.append(Label(master, text= self.string_list1[r-self.init_r][c-self.init_c],bg = self.color_codes[1]))
              self.entry_counter = self.entry_counter + 1

              # Place the object onto the grid
              self.label_rows[c-self.init_c].grid(row = r, column = c*2, sticky = SW)
              self.entry_rows[c-self.init_c].grid(row = r, column = c*2 + 1)

              # Configure types
              self.label_rows[c-self.init_c].config(font=("Times New Roman", 10))

           # Store data into a list for reference
           self.entry_list.append(self.entry_rows)
           self.label_list.append(self.label_rows)

        # GRID (14,0):(14,11)
        ############################################################################################################
        self.init_r = 14 # Initial row for this section
        self.init_c = 0 # Initial col for this section

        # buttons
        
        # New Button
        self.button0 = Button(master, text = "New Patient Data")
        self.button0.grid(row = self.init_r, column = 0,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)
        # Load Button
        self.button1 = Button(master, text = "Load Patient Data")
        self.button1.grid(row = self.init_r, column = 1,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)
        # Save Button
        self.button2 = Button(master, text = "Save and Email Data", command = self.save_wav)
        self.button2.grid(row = self.init_r, column = 2,columnspan=1, sticky = W+E+N+S, padx = 5, pady=10)
        
        # Load New Sound
        self.button3 = Button(master, text = "Load sound", command = self.loaddata)
        self.button3.grid(row = self.init_r, column = 3,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)
        # Sound Button
        self.button4 = Button(master, text = "Play sound", command = self.soundplayback)
        self.button4.grid(row = self.init_r, column = 5,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)
        # Analysis Button
        self.button5 = Button(master, text = "Analysis", command = self.challenge2016)
        self.button5.grid(row = self.init_r, column = 7,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)
        # Convert txt to wav
        self.button6 = Button(master, text = "Convert", command = self.convert)
        self.button6.grid(row = self.init_r, column = 9,columnspan=2, sticky = W+E+N+S, padx = 5, pady=10)
        
        ############################################################################################################
                  
        # ETC

        win = Toplevel(self.master)
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        win.destroy()

        self.master.update()
        
        self.gui_width = master.winfo_width()
        self.gui_height = master.winfo_height()
        
        x = screen_width/4 - self.gui_width/4
        y = screen_height/4 - self.gui_height/4
        
        master.geometry("+%d+%d" % (x, y))
        master.configure(bg = self.color_codes[1])
        

    def save_wav(self):

        global wave_read, filename
        
        wave_read.close()
        
        temp_file = filedialog.asksaveasfilename(title = "Save file",filetypes = ((".wav files","*.wav"),("all files","*.*")), defaultextension=".wav")
        if temp_file == "":
            wave_read = wave.open(filename,"rb")
            return
        copyfile(filename, temp_file)
        print("FILE SAVED")
        
        filename = temp_file
        
        sender_email = "smptOrisAuscultations@gmail.com"
        receiver_email = self.patient_list_e[4].get()

        if receiver_email == "":
            wave_read = wave.open(filename,"rb")
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = 'Oris Auscultations'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        text =  "Hello " + str(self.patient_list_e[0].get()) + """
        
        This email contains a recording of your heartbeat.\n
        Thanks for using our capstone!\n
        With Best Regards,
        Oris"""
        
        msg.attach(MIMEText(text, 'plain'))

        fp = open(temp_file,'rb')
        filedata = fp.read()
        
        audio = MIMEAudio(_audiodata = filedata, _subtype = 'wav')
        audio.add_header('Content-Disposition', 'attachment', filename = os.path.basename(temp_file))

        msg.attach(audio)

        # Send the message via our own SMTP server.
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(sender_email, "oriscapstone")
        s.send_message(msg)
        s.quit()
        print("FILE EMAILED")
        
        fp.close()
        wave_read = wave.open(filename, 'rb')
        
    def enableBluetooth(self):
        self.master.after(0, self.bt_server_handler)
        # This will get it's own thread
        self.server.accept_conn()
        
    def bt_server_handler(self):

        if self.server.address == "":
            self.bt_status.set("Status: Searching...")
            self.labelBT.config(text=self.bt_status.get())
        else:
            
            if(self.server.state == 1):
                self.bt_status.set("Status: Receiving")
                self.labelBT.config(text=self.bt_status.get())

            if(self.server.state == 2):
                self.bt_status.set("Status: Sending Complete")
                self.labelBT.config(text=self.bt_status.get())
                self.bt_updater()
                return
                            
        self.master.after(1000, self.bt_server_handler)

    
    def bt_updater(self):
        global filename, wave_read, signal
        txtname = os.path.join(dirname, r'test0.txt')
        filename = os.path.join(dirname, r'output.wav')
        wave_read.close()
         
        # read text file
        textfile = open(txtname, "rb")
        raw_data = textfile.readlines();
        
        # format text file data
        write_data=[]
        empty_bytes = 0
        
        for i in range(0,len(raw_data)-1):
            num = raw_data[i]
            
            # ignore empty bytes
            if num != b'\r\n' and num != b'-\r\n':
                write_data.append(pack('h',int(num)))
            else:
                empty_bytes = empty_bytes + 1
        # Get the frequency value from the runtime

        runtime = raw_data[-1]
        freq_wav = (len(raw_data)-empty_bytes-1)/float(runtime)
        freq_wav = int(round(freq_wav))
        
        print(freq_wav)
        
        # create a wavefile
        wave_write = wave.open("output.wav",'wb')
        wave_write.setparams((1, 2, freq_wav, len(raw_data)-1, 'NONE', 'not compressed')) #set parameters: 1 channel, 2 bytes per entry for int16, initial size 0, sampling frequncy, uncompressed
        wave_write.writeframes(b''.join(write_data))
        wave_write.close

        print("Done .txt to .wav conversion")

        sleep(1)
        for i in range(0,3):
            try:
                wave_read = wave.open(filename, 'rb')
                break
            except EOFError as error:
                sleep(2)
                continue
        
        try:    
            signal = wave_read.readframes(-1)
            signal = np.fromstring(signal, 'Int16')

            # (nchannels, sampwidth, framerate, nframes, comptype, compname)
            self.wave_params = wave_read.getparams()

            nframes = self.wave_params[3]
            rate = self.wave_params[2]
            duration = nframes / float(rate)
            x = np.linspace(0,duration,nframes)

            self.labelBPM.config(text="BPM:      ")
            self.fig.clear()
            self.plt = self.fig.subplots()
            self.plt.plot(x,signal)
            self.plt.set_xlabel('Time (Seconds)')
            self.plt.set_ylabel('.Wav file Magnitude')
            self.Canvas1.draw()
        except Exception as error:
            print ("Could not open newly generated .wav file")
            
        # Remove all analysis stuff
        for r in range(0,len(self.entry_list)):
            for c in range(0,len(self.entry_list[0])):
                self.entry_list[r][c].config(state = "normal")
                self.entry_list[r][c].delete(0, END)
                self.entry_list[r][c].config(state = "disabled")

        return
        
    def soundplayback(self):
        # wave_params: 0-nchannels, 1-sampwidth, 2-framerate, 3-nframes
        self.wave_params = wave_read.getparams()
        
        p = pyaudio.PyAudio()
        stream = p.open(format = p.get_format_from_width(self.wave_params[1]),  
                        channels = self.wave_params[0],  
                        rate = self.wave_params[2],  
                        output = True)
        #read data
        wave_read.rewind()
        data = wave_read.readframes(chunk)  

        #play stream  
        while data:  
            stream.write(data)  
            data = wave_read.readframes(chunk)

        #stop stream  
        stream.stop_stream()  
        stream.close()

        #close PyAudio  
        p.terminate()
        
    def challenge2016(self):
        self.master.withdraw()
        self.splash = Splash(self.master)
        
        self.eng.addpath(os.path.join(dirname,r'neural_network'),nargout=0)
        self.eng.addpath(os.path.join(dirname,r'heart_sounds'),nargout=0)

        basename = os.path.basename(filename)

        try:
            # sleep(5)
            self.classifyResult = self.eng.challenge(os.path.dirname(os.path.abspath(filename))+'\\'+os.path.splitext(basename)[0],nargout=1)
            self.classifyResult = self.classifyResult[0]
        except:
            print("Unable to analyze")
            self.splash.destroy()
            self.master.deiconify()
            return

        # mean beat-beat interval
        m_RR_pos = self.classifyResult[1] + self.classifyResult[2] 
        m_RR_neg = self.classifyResult[1] - self.classifyResult[2]

        nframes = self.wave_params[3]
        rate = float(self.wave_params[2])
        
        matlab_sampling = 1000
        scaling = matlab_sampling/rate

        duration = nframes / rate
        
        BMP_pos = round(scaling * 60*rate/m_RR_pos)
        BMP_neg = round(scaling * 60*rate/m_RR_neg)

        self.labelBPM.config(text="BPM: " + str(BMP_pos) + " - " + str(BMP_neg))
        
        print("Mean beat-to-beat: " + str(m_RR_pos) + ": " + str(m_RR_neg))
        print("Number of frames: " + str(nframes))
        print("Duration: " + str(duration))
        print("Frequency: " + str(rate))
        print("BPM: " + str(BMP_pos) + " - " + str(BMP_neg))

        for r in range(0,len(self.entry_list)):
            for c in range(0,len(self.entry_list[0])):
                self.entry_list[r][c].config(state = "normal") # Allow editing
                self.entry_list[r][c].delete(0, END) # Delete current text
                self.entry_list[r][c].insert(10,round(self.classifyResult[4*r+c+1]/rate/scaling,4)) # Enter classification Results
                self.entry_list[r][c].config(state = "disabled") # Disable Text

        self.splash.destroy()   
        self.master.deiconify()

        print("Classifying Result: " + str(self.classifyResult[0]))
        
        if self.classifyResult[0] == -1:
            self.health_status.set("Analysis: Normal")
            self.labelStatus.config(text=self.health_status.get())
            
        elif self.classifyResult[0] == 1: 
            self.health_status.set("Analysis: Abnormal")
            self.labelStatus.config(text=self.health_status.get())
            
        else:
            self.health_status.set("Analysis: Undefined")
            self.labelStatus.config(text=self.health_status.get())
            
        self.master.update()
        
    def loaddata(self):

        global filename, wave_read, signal
        
        temp_file = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("wav files","*.wav"),("all files","*.*")))
        if (temp_file != ""):
            filename = temp_file
        else:
            return
        wave_read.close()
        
        wave_read = wave.open(filename, 'rb')
        signal = wave_read.readframes(-1)
        signal = np.fromstring(signal, 'Int16')

        # (nchannels, sampwidth, framerate, nframes, comptype, compname)
        self.wave_params = wave_read.getparams()

        nframes = self.wave_params[3]
        rate = self.wave_params[2]
        duration = nframes / float(rate)
        x = np.linspace(0,duration,nframes)
        
        self.fig.clear()
        self.plt = self.fig.subplots()
        self.plt.plot(x,signal)
        self.plt.set_xlabel('Time (Seconds)')
        self.plt.set_ylabel('.Wav file Magnitude')
        self.Canvas1.draw()

        self.labelBPM.config(text="BPM:      ")
        for r in range(0,len(self.entry_list)):
            for c in range(0,len(self.entry_list[0])):
                self.entry_list[r][c].config(state = "normal")
                self.entry_list[r][c].delete(0, END)
                self.entry_list[r][c].config(state = "disabled")
                
    def convert(self):

        # open text file
        temp_file =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
        if (temp_file != ""):
            txtname = temp_file
        else:
            return
        
        # read text file
        textfile = open(txtname, "rb")
        raw_data = textfile.readlines();
        
        # format text file data
        write_data=[]
        
        for i in range(0,len(raw_data)-1):
            num = raw_data[i]
            # ignore empty bytes
            if num != b'\r\n' and num != b'-\r\n':
                write_data.append(pack('h',int(num)))

        # Get the frequency value from the runtime
        freq_wav = (len(raw_data)-1)/float(raw_data[-1])
        freq_wav = int(round(freq_wav))        

        # create a wavefile
        wave_write = wave.open("output.wav",'wb')
        
        #set parameters: 1 channel, 2 bytes per entry for int16, initial size 0, sampling frequncy, uncompressed
        wave_write.setparams((1, 2, freq_wav, len(raw_data)-1, 'NONE', 'not compressed')) 
        wave_write.writeframes(b''.join(write_data))
        wave_write.close
        print("Done .txt to .wav conversion")

    def liveplot(self):
        self.xs = range(0,2000)
        self.ys = [0]*2000

        self.fig.clear()
        self.plt = self.fig.subplots()
        
        # attach a figure, an animation function, arguements and duration
        self.ani = animation.FuncAnimation(self.fig, self.animate,interval=1)
        self.Canvas1.draw()

    def animate(self,i):
        
        self.ys = self.ys[-2000:]

       # if (self.server.state == 0):
       #     self.xs.append(i)
       #     self.ys.append(np.sin(6.28*i/100))
            
        if (self.server.state == 1):
            if (self.server.sem_plot == 1):
                self.ys = self.server.liveData
                #print(self.ys)
        else:
            self.ani.event_source.stop()
            
        self.plt.clear()
        self.plt.plot(self.xs, self.ys)

        if (self.server.state == 2):
            self.xs = []
            self.ys = []
            i = 0
            self.ani.event_source.stop()
        
if __name__ == "__main__":    
    root = Tk()
    my_gui = OrisApp(root)
    root.mainloop()
    
    wave_read.close()
