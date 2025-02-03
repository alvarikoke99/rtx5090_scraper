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
sender_addr = os.getenv("SENDER_ADDR", "alert-mail@gmail.com")
receiver_addr = os.getenv("RECEIVER_ADDR", "personal-mail@gmail.com")
pwd = os.getenv("EMAIL_PWD", "password")
N = int(os.getenv("ITER_CYCLES", 1))
wait_time = int(os.getenv("WAIT_TIME", 3))
error_alert = os.getenv("ERROR_ALERT", "FALSE").lower() == "true"

# code to use in crontab scheduler
# SHELL=/bin/bash
# * 8-23,0-3 * * * DISPLAY=:0 /usr/bin/python3 /home/ubuntu/scraper/linux_scraper_se.py >> /home/ubuntu/Documentos/Scraper/log.out

def sendMsg(sender_addr, receiver_addr, subject, body):
    # Create message object instance
    msg = MIMEMultipart()
        
    # Setup the parameters of the message
    msg['From'] = sender_addr
    msg['To'] = receiver_addr
    msg['Subject'] = subject
        
    # Add in the message body
    msg.attach(MIMEText(body, 'plain'))
        
    # Create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
        
    # Login Credentials for sending the mail
    server.login(sender_addr, pwd)
        
    # Send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

def check_button_exists(driver):
    try:
        button_element = driver.find_element(By.CSS_SELECTOR, "button.stock-grey-out.link-btn.i-408")
        if button_element:
            return True
        else:
            return False
    except:
        driver.save_screenshot("headless_screenshot.png")
        return False
    
    

def checkStockNvidia(driver):
    is_out_of_stock = check_button_exists(driver)
    if not is_out_of_stock:
        message = "El enlace del articulo es el siguiente: " + URL_NVIDIA
        sendMsg(sender_addr, receiver_addr, "STOCK DE RTX 5090", message)
        print("Mail sent at: ", time.ctime(time.time()))
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
        time.sleep(wait_time)
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
    if error_alert:
        sendMsg(sender_addr, receiver_addr, "Error en el servidor", error_trace)
