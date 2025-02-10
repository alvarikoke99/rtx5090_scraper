from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import smtplib
import traceback
from dotenv import load_dotenv
import os

load_dotenv()

URL_NVIDIA = os.getenv("URL", "https://marketplace.nvidia.com/es-es/consumer/graphics-cards/?locale=es-es&page=1&limit=12&gpu=RTX%205090&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~1")
SENDER_ADDR = os.getenv("SENDER_ADDR", "alert-mail@gmail.com")
RECEIVER_ADDR = os.getenv("RECEIVER_ADDR", "personal-mail@gmail.com")
PWD = os.getenv("EMAIL_PWD", "password")
N = int(os.getenv("ITER_CYCLES", 1))
WAIT_TIME = int(os.getenv("WAIT_TIME", 3))
ERROR_ALERT = os.getenv("ERROR_ALERT", "FALSE").lower() == "true"
IMAGE_PATH = os.getenv("IMG_PATH", "success_screenshot.png")
SEND_IMG = os.getenv("SEND_IMG", "FALSE").lower() == "true"

# code to use in crontab scheduler
# SHELL=/bin/bash
# * 8-23,0-3 * * * DISPLAY=:0 /usr/bin/python3 /home/ubuntu/scraper/linux_scraper_se.py >> /home/ubuntu/Documentos/Scraper/log.out

def createMsg(sender_addr, receiver_addr, subject, body) -> MIMEMultipart:
    # Create message object instance
    msg = MIMEMultipart()
        
    # Setup the parameters of the message
    msg['From'] = sender_addr
    msg['To'] = receiver_addr
    msg['Subject'] = subject
        
    # Add in the message body
    msg.attach(MIMEText(body, 'plain'))

    return msg

def attachImg(msg, image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as image_file:
                image = MIMEImage(image_file.read(), _subtype="png")
                image.add_header('Content-ID', '<image>')
                msg.attach(image)

                # Get the current body (it's the last attached part)
                plain_body = "" # initialize
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain': #find the plain text body
                        plain_body = part.get_payload()
                        msg.detach(part) # detach the plain text body
                        break

                html_body = plain_body + "\n\n<img src='cid:image'>"  # Create the HTML body
                msg.attach(MIMEText(html_body, 'html')) # attach HTML body

                return msg
        except Exception as e:
            print(f"Error attaching image: {e}")
    else:
        print(f"Image not found at: {image_path}")
    return msg

def sendMsg(sender_addr, msg):
    # Create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
        
    # Login Credentials for sending the mail
    server.login(sender_addr, PWD)
        
    # Send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

def sendAlertMail(sender_addr, receiver_addr, subject, body):
    msg = createMsg(sender_addr, receiver_addr, subject, body) 
    sendMsg(sender_addr, msg)

def sendAlertMailWithImg(sender_addr, receiver_addr, subject, body, image_path):
    msg = createMsg(sender_addr, receiver_addr, subject, body) 
    msg = attachImg(msg, image_path)
    sendMsg(sender_addr, msg)

def check_button_exists(driver):
    try:
        button_element = driver.find_element(By.CSS_SELECTOR, "button.stock-grey-out.link-btn.i-408")
        if button_element:
            driver.save_screenshot(IMAGE_PATH)
            return True
        else:
            return False
    except:
        driver.save_screenshot("error_screenshot.png")
        return False
    
def checkStockNvidia(driver):
    has_stock = check_button_exists(driver)
    if has_stock:
        message = "El enlace del articulo es el siguiente: " + URL_NVIDIA
        if SEND_IMG:
            sendAlertMailWithImg(SENDER_ADDR, RECEIVER_ADDR, "STOCK DE RTX 5090", message, IMAGE_PATH)
        else:
            sendAlertMail(SENDER_ADDR, RECEIVER_ADDR, "STOCK DE RTX 5090", message)
        print("STOCK - Mail sent at: ", time.ctime(time.time()))
        print("")

try:
    # Start webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(options=chrome_options)

    for i in range(N):
        # Check if there is stock of FE
        driver.get(URL_NVIDIA)
        time.sleep(WAIT_TIME)
        checkStockNvidia(driver)

    # Close webdriver
    time.sleep(3)
    driver.close()
    driver.quit() 
    print("Running - ", time.ctime(time.time()))
    print("")

except Exception as e:
    error_trace = traceback.format_exc()
    print("ERROR - ", time.ctime(time.time()))
    print(error_trace)
    if ERROR_ALERT:
        sendMsg(SENDER_ADDR, RECEIVER_ADDR, "Error en el servidor", error_trace)
