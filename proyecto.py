import cv2
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import mediapipe as mp
 
cap = cv2.VideoCapture(0) #Chequeo de camara
 
mpHands = mp.solutions.hands #detecta mano/dedo
hands = mpHands.Hands()   #completar la configuración de inicialización de las manos
mpDraw = mp.solutions.drawing_utils
 
#Para acceder al altavoz a través de la biblioteca pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volbar=400
volper=0
 
volMin,volMax = volume.GetVolumeRange()[:2]
 
while True:
    success,img = cap.read() #Si la cámara funciona captura una imagen
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #Convertir a rgb
    
    #Recopilación de información de gestos
    results = hands.process(imgRGB) #completa el procesamiento de la imagen.
 
    lmList = [] #lista vacía
    if results.multi_hand_landmarks: #lista de todas las manos detectadas.
        #Accediendo a la lista, podemos obtener la información del bit de bandera correspondiente a cada mano
        for handlandmark in results.multi_hand_landmarks:
            for id,lm in enumerate(handlandmark.landmark): #agregar contador y devolverlo
                # Obtener puntos de la articulación de los dedos
                h,w,_ = img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy]) #agregando a la lista vacía 'lmList'
            mpDraw.draw_landmarks(img,handlandmark,mpHands.HAND_CONNECTIONS)
    
    if lmList != []:
        #obtener el valor en un punto
                        #x      #y
        x1,y1 = lmList[4][1],lmList[4][2]  #pulgar
        x2,y2 = lmList[8][1],lmList[8][2]  #dedo índice
        #creando un círculo en las puntas de los dedos pulgar e índice
        cv2.circle(img,(x1,y1),13,(255,0,0),cv2.FILLED) #imagen #dedos #radio #rgb
        cv2.circle(img,(x2,y2),13,(255,0,0),cv2.FILLED) #imagen #dedos #radio #rgb
        cv2.line(img,(x1,y1),(x2,y2),(255,0,0),3)  #crea una línea en blanco y negro con las puntas de los dedos índice y pulgar
 
        length = hypot(x2-x1,y2-y1) #distancia b/n puntas usando hipotenusa
 # de numpy encontramos nuestra longitud, convirtiendo el rango de la mano en términos de rango de volumen, es decir, b/n -63.5 a 0
        vol = np.interp(length,[30,350],[volMin,volMax]) 
        volbar=np.interp(length,[30,350],[400,150])
        volper=np.interp(length,[30,350],[0,100])
        
        
        print(vol,int(length))
        volume.SetMasterVolumeLevel(vol, None)
        
        #Rango de mano 30 - 350
        # Rango de volumen -63.5 - 0.0
        #creación de barra de volumen para el nivel de volumen
        cv2.rectangle(img,(50,150),(85,400),(0,0,255),4) # vid ,posición inicial ,posición final ,rgb ,espesor
        cv2.rectangle(img,(50,int(volbar)),(85,400),(0,0,255),cv2.FILLED)
        cv2.putText(img,f"{int(volper)}%",(10,40),cv2.FONT_ITALIC,1,(0, 255, 98),3)
        #diga el porcentaje de volumen, la ubicación, la fuente del texto, la longitud, el color rgb, el grosor
    cv2.imshow('Image',img) #mostrar el vídeo
    if cv2.waitKey(1) & 0xff==ord(' '): #Al usar la barra espaciadora, el retraso se detendrá
        break
        
cap.release()     #stop cam       
cv2.destroyAllWindows() #close window