import tkinter as tk
class MyDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.parent = parent
        self.top.title("Salir")
        size = self.parent.geometry().split('+')[0].split('x')
        self.Size = [int(n) for n in size]
        self.top.geometry("+%d+%d" % (self.parent.winfo_x() + (self.Size[0]/2), self.parent.winfo_y() + (self.Size[1]/2)))
        self.__EleccionPrivada = False

        tk.Label(self.top, text="Arduino no esta conectado.\nSi continua no se podra encender las alarmas").grid(row=0, column=0, columnspan=2)

        self.button1 = tk.Button(self.top, text="Si, deseo continuar.", command=self.Continuar)
        self.button2 = tk.Button(self.top, text="         No         ", command=self.Cerrar)
        self.button1.grid(row=1, column=0, padx=5, pady=5)
        self.button2.grid(row=1, column=1, padx=5, pady=5)

    def Eleccion(self):
        if self.__EleccionPrivada:
            self.__EleccionPrivada = False
            return True
        else:
            return False

    def Continuar(self):
        self.top.destroy()
        self.__EleccionPrivada = True

    def Cerrar(self):
        self.top.destroy()
        self.__EleccionPrivada = False