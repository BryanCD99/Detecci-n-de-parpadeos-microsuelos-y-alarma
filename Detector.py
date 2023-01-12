import cv2
import mediapipe as mp
import math
import time


class Detector():
    def __init__(self):
        # Funcion de dibujo ************
        self.mpDibujo = mp.solutions.drawing_utils
        self.Conf_Dib = self.mpDibujo.DrawingSpec(thickness=1, circle_radius=1)

        # Objeto para almacenar la malla facial
        self.mpMallaFacial = mp.solutions.face_mesh
        self.MallaFacial = self.mpMallaFacial.FaceMesh(max_num_faces=1, min_detection_confidence=0.8,
                                                       min_tracking_confidence=0.8)

        # Videocaptura **************
        self.Source = 0
        self.cap = None
        # Configuracion de parametros
        self.Parpadeo = False
        self.conteo = 0
        self.tiempo = 0
        self.inicio = 0
        self.final = 0
        self.conteo_sue = 0
        self.MeasureTime = 0
        self.showMask = True
        self.frame = None
        self.__MicroSue = False

    def VideoSource(self, Source):
        self.Source = Source
        self.cap = cv2.VideoCapture(Source)

    def VideoStart(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.Source)
            return True
        else:
            return False

    def AlarmTime(self, Time):
        self.AlarmTime = Time

    def Stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def MicroSue(self):
        if self.__MicroSue:
            return True
        else:
            return False

    def Detectar(self):
        if self.cap is not None:
            # Obtiene un frame de la camara
            ret, frame = self.cap.read()
            # Modo espejo para la camara
            frame = cv2.flip(frame, 1)
            # Redimensiona la imagen a 800x600
            frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_AREA)

            # Obtiene la malla facial aplicada al rostro detectado
            Analisis = self.MallaFacial.process(frame)

            # Listas para el procesamiento de la imagen
            AllPoints = []  # Almacena todos los puntos X,Y y un ID de identificación

            # Si se detecta algun rostro en el modelo de deteccion se ejecuta el respectivo analisis
            if Analisis.multi_face_landmarks:
                # Por cada rostro detectado se realiza un analisis
                for rostros in Analisis.multi_face_landmarks:

                    if (self.showMask):
                        # Dibuja sobre el frame la malla del rostro detectado
                        self.mpDibujo.draw_landmarks(frame, rostros, self.mpMallaFacial.FACE_CONNECTIONS, self.Conf_Dib,
                                                     self.Conf_Dib)

                    # Obtiene la posicion de cada punto sobre el frame
                    for id, puntos in enumerate(rostros.landmark):
                        al, an, c = frame.shape  # Obtiene las dimensiones del frame
                        x, y, z = int(puntos.x * an), int(puntos.y * al), float(
                            puntos.z)  # Convierte las proporciones de los puntos a pixeles

                        # Almacena todos los puntos de la malla del rostro
                        AllPoints.append([id, x, y, z])
                    # Procesa los puntos de los ojos
                    # Obtiene las coordenadas de los puntos de apertura del ojo derecho
                    x1, y1, z1 = AllPoints[145][1:]
                    # Obtiene las coordenadas de los puntos de apertura del ojo izquierdo
                    x2, y2, z2 = AllPoints[159][1:]  # 159
                    # Calcula la distancia entre los dos puntos dados
                    # cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), thickness=5)
                    longitud1 = math.hypot(x2 - x1, y2 - y1)
                    # print(longitud1)
                    x3, y3, z3 = AllPoints[374][1:]
                    x4, y4, z4 = AllPoints[386][1:]
                    # cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
                    longitud2 = math.hypot(x4 - x3, y4 - y3)

                    # Conteo de parpadeos
                    cv2.putText(frame, f'parpadeos: {int(self.conteo)}', (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 3)
                    cv2.putText(frame, f'Sonnolencias: {int(self.conteo_sue)}', (400, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255),
                                3)
                    cv2.putText(frame, f'Duracion: {int(self.MeasureTime)} S', (350, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 3)

                    if longitud1 < 12 and longitud2 < 12 and self.Parpadeo is False:
                        tiempo = 0
                        self.conteo = self.conteo + 1
                        self.Parpadeo = True
                        self.inicio = time.time()

                    elif longitud1 > 13.5 and longitud2 > 13.5 and self.Parpadeo == True:
                        self.Parpadeo = False
                        self.__MicroSue = False
                        # Contador de microsueños
                        if self.tiempo >= 3:
                            self.conteo_sue = self.conteo_sue + 1
                            self.MeasureTime = self.tiempo

                    if self.Parpadeo:
                        self.final = time.time()
                        # Temporizador
                        self.tiempo = round(self.final - self.inicio, 0)
                        if self.tiempo >= 3:
                            self.__MicroSue = True
            else:
                # Si no se detecta un rostro, entonces se resetea las variables de parpadeo y conteo
                self.conteo_sue = 0
                self.conteo = 0
                self.MeasureTime = 0
                self.Parpadeo = False
                self.__MicroSue = False

            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
