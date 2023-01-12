import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
from PIL import Image, ImageTk
from Detector import *
from Arduino import *
from DIalogos import *

# variables de uso general ******
width = 920
height = 580
Inicio = False
Port = None
AlarmTime = 2000.0  # En milliseconds
PulsRefresh = 1
PulsTime = 0
Dato = None

# Colores de la interfaz
BackGroundColor = 'gray88'
PanelControlBackColor = 'gray88'

# Variables para almacenar las imagenes
ImagenF = None
imagenConVideo = None
imagenDesVideo = None


# Funcion de inicio de captura del video al hacer clic sobre el area de video
def IniciarVideo(event):
    Iniciar()
# Función de iniciar captura del video
def Iniciar():
    global Inicio,ImagenF,imagenDesVideo, imagenConVideo, PulsTime, Dato
    if Inicio:
        Inicio = False
        background.configure(image=ImagenF)
        background.image = ImagenF

        # Pone el boton en modo conectar
        ConDesVideo.configure(image=imagenConVideo)
        ConDesVideo.image = imagenConVideo
        BPM.config(text="No disponible")
        Detect.Stop()
    else:
        if Arduino.OpenPort is False:
            d = MyDialog(ventana)
            ventana.wait_window(d.top)
            if d.Eleccion() is False:
                return
        Inicio = True
        if Detect.VideoStart():
            # Pone el boton en modo desconectar
            ConDesVideo.configure(image=imagenDesVideo)
            ConDesVideo.image = imagenDesVideo
            PulsTime = time.time()
            Dato = None
            ventana.after(10, Visualizar)

# Función para mostrar el video en la interfaz
def Visualizar():
    global Inicio,PulsRefresh,PulsTime, Dato
    if Inicio:
        Detect.Detectar()
        # Si se detecta un microsueño entonces se envia la alarma
        if Detect.MicroSue() == True:
            print("Dormido")
            Arduino.SendChar('A')
            Arduino.SendFloat(AlarmTime)

        # Conversion del video a formato de la interfaz
        im = Image.fromarray(Detect.frame)
        im = im.resize((600, 400))
        img = ImageTk.PhotoImage(image=im)

        # Mostramos en el GUI
        background.configure(image=img)
        background.image = img

        # Obtiene el valor del BPM
        if time.time()-PulsTime > PulsRefresh:
            Arduino.SendChar('B')
            Dato = Arduino.ReadSingleFloat()
            PulsTime = time.time()

        if Dato is not None:
            BPM.config(text="  " + str(int(Dato)), fg="#000000")
        else:
            BPM.config(text="No disponible", fg="#8B7D6B")

        #if Inicio:
        # LLama nuevamente a la función para de esta forma mostrar video de forma continua
        ventana.after(10, Visualizar)
    else:
        Detect.Stop()
        Inicio = False

# Función para configurar el puerto
def SetPort(event):
    global Port
    Port = Port_Menu.get()
    #print(Port_Menu.get())


# Funcion para finalizar todos los procesos cuando se cierra la interfaz
def on_closing():
    Detect.Stop()
    ventana.destroy()

def ConDesUSB():
    global Port
    if Port is None:
        msg = tkinter.messagebox.showinfo(title="Conexión", message="Seleccione un puerto serial")
    else:
        if Arduino.OpenPort:
            Arduino.Close()
            # Pone el boton en modo desconectar
            ConDesUSB.configure(image=imagenBotConectar)
            ConDesUSB.image = imagenBotConectar
        else:
             if Arduino.begin(Port, 115200) is False:
                msg = tkinter.messagebox.showinfo(title="Conexión" ,message="No se pudo abrir el puerto serial")
             else:
                msg = tkinter.messagebox.showinfo(title="Conexión", message="Conexión exitosa")
                # Pone el boton en modo desconectar
                ConDesUSB.configure(image=imagenBotCerrar)
                ConDesUSB.image = imagenBotCerrar


# Principal
if __name__ == "__main__":

    # Inicializador del detector de rostros
    Detect = Detector()
    # Inicia el modulo de comunicación con Arduino
    Arduino = ArduinoSerial()

    # Inicia la configuracion de la ventana
    ventana = tk.Tk()
    ventana.title("Interfaz de detección de sueños")
    ventana.geometry(str(width) + "x" + str(height))
    ventana.resizable(width=0, height=0)
    ventana.configure(background=BackGroundColor)
    ventana.protocol("WM_DELETE_WINDOW", on_closing)

    # Inicializacion de los objetos
    # Panel de control -----flat, groove, raised, ridge, solid, or sunken
    panel = tk.PanedWindow(ventana, bg=PanelControlBackColor, relief="groove", bd=2, height="400", width="200")
    panel.place(x=680, y=70)

    # Texto puerto
    PuertoName = tk.Label(panel, text="Puerto: ", bg=PanelControlBackColor,font=9)
    PuertoName.place(x=10, y=10)

    # Selector de puerto
    Ports = Arduino.puertos_seriales()
    Port_Menu = tkinter.ttk.Combobox(panel,values=Ports,state="readonly",background="")
    Port_Menu.bind("<<ComboboxSelected>>", SetPort)
    Port_Menu.place(x=10, y=40)

    # Boton de iniciar/cerrar conexion
    imagenBotCerrar = Image.open("BotonCerrarConexion.png")
    imagenBotCerrar = imagenBotCerrar.resize((150, 50))
    imagenBotCerrar = ImageTk.PhotoImage(imagenBotCerrar)
    imagenBotConectar = Image.open("Conectar.png")
    imagenBotConectar = imagenBotConectar.resize((150, 50))
    imagenBotConectar = ImageTk.PhotoImage(imagenBotConectar)
    ConDesUSB = tk.Button(panel, text="Conectar", image=imagenBotConectar, height="50", width="150", border=0, command=ConDesUSB)
    ConDesUSB.config(bg=BackGroundColor)
    ConDesUSB.place(x=10, y=80)

    # Texto Iniciar
    PuertoName = tk.Label(panel, text="Iniciar captura:", bg=PanelControlBackColor,font=9)
    PuertoName.place(x=10, y=160)

    # Boton de iniciar/apagar video
    imagenConVideo = Image.open("BotonConectarVideo.png")
    imagenConVideo = imagenConVideo.resize((150, 50))
    imagenConVideo = ImageTk.PhotoImage(imagenConVideo)
    imagenDesVideo = Image.open("BotonDesconectarVideo.png")
    imagenDesVideo = imagenDesVideo.resize((150, 50))
    imagenDesVideo = ImageTk.PhotoImage(imagenDesVideo)
    ConDesVideo = tk.Button(panel, text="Iniciar", image=imagenConVideo, height="50", width="150", border=0, command=Iniciar)
    ConDesVideo.config(bg=BackGroundColor)
    ConDesVideo.place(x=10, y=200)

    # Texto BPM
    BPMLabel = tk.Label(panel, text="BPM:", bg=PanelControlBackColor,font=9)
    BPMLabel.place(x=10, y=300)

    BPM = tk.Label(panel, text="No disponible", bg=PanelControlBackColor,font=9,fg="#8B7D6B")
    BPM.place(x=10, y=330)

    # Ventana de video **********
    imagenBackVideo = Image.open("Background.png")
    imagenBackVideo = imagenBackVideo.resize((600, 400))
    ImagenF = ImageTk.PhotoImage(imagenBackVideo)
    background = tk.Label(image=ImagenF, text="Fondo")
    background.place(x=50, y=70)
    # Permite que al hacer clic sobre el area del video, iniciar o detener el proceso de captura de imagen
    background.bind("<Button-1>",IniciarVideo)

    ventana.update()
    ventana.mainloop()

