        
import os
import picamera
import RPi.GPIO as GPIO
import smtplib
from time import sleep

# Importing modules for sending mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sender = '330ohms.p@gmail.com'
password = '*********'
receiver ='saul@330ohms.com'

DIR = './Database/'
FILE_PREFIX = 'image'
            
pin_pir = 22
pin_boton = 27
pin_led = 17
pin_led2 = 10

estado = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_pir, GPIO.IN)
GPIO.setup(pin_boton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_led, GPIO.OUT)
GPIO.setup(pin_led2, GPIO.OUT)

def button_cb(channel):
    global estado
    estado = not estado
    GPIO.output( pin_led2 , estado )
    print("Boton presionado")
    print("Estado: " + str(estado) + "\n")
    
def pir_cb(channel):
    print("Movimiento detectado")
    if estado:
        send_mail()
    else:
        print ("Presiona el botón para activar la captura")

GPIO.add_event_detect( pin_pir , GPIO.RISING , callback=pir_cb, bouncetime = 100)
GPIO.add_event_detect( pin_boton , GPIO.FALLING , callback=button_cb , bouncetime = 300)

def send_mail():
    print ('Sending E-Mail')
    # Create the directory if not exists
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    
    filename = os.path.join(DIR, 'image.jpg')
    
    # Capture the face
    with picamera.PiCamera() as camera:
        pic = camera.capture(filename)
    
    
    # Sending mail
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Movement Detected'
    
    body = 'Picture is Attached.'
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename= %s' % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()
    

GPIO.output( pin_led , True )


try:
    while 1:
        sleep(1)
except KeyboardInterrupt:
    # CTRL+C
    print("\nInterrupcion por teclado")
except:
    print("Otra interrupcion")
finally:
    GPIO.cleanup()
    print("GPIO.cleanup() ejecutado")
        