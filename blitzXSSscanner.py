import os
import sys
import time
import colorama
from colorama import Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import html
import logging
from datetime import datetime

colorama.init(autoreset=True)

# Pengaturan logging
logging.basicConfig(filename='xss_scanner.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Menampilkan Banner di terminal
def banner():
    os.system('clear' if os.name != 'nt' else 'cls') 
    print(Fore.CYAN + """ 
██████╗ ██╗     ██╗████████╗███████╗    ██╗  ██╗███████╗███████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ 
██╔══██╗██║     ██║╚══██╔══╝╚══███╔╝    ╚██╗██╔╝██╔════╝██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
██████╔╝██║     ██║   ██║     ███╔╝      ╚███╔╝ ███████╗███████╗    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██╔══██╗██║     ██║   ██║    ███╔╝       ██╔██╗ ╚════██║╚════██║    ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
██████╔╝███████╗██║   ██║   ███████╗    ██╔╝ ██╗███████║███████║    ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝    ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
                                                                                                                                
    """ + Fore.RESET)
    print(Fore.CYAN + "                 BLITZ XSS SCANNER" + Fore.RESET)
    print(Fore.CYAN + "               Managed by: 0xRedFox29" + Fore.RESET)
    time.sleep(0.5)

# Membaca payload XSS dari file teks
def read_payloads(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} tidak ditemukan.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Membuat laporan HTML sebagai hasil scanning
def generate_html_report(folder_path, vulnerable_payloads):
    report_file_path = os.path.join(folder_path, 'xss_vulnerability_report.html')
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XSS Vulnerability Report</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #000000; color: #ffffff; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #555555; padding: 10px; text-align: left; }
            th { background-color: #333333; }
            tr:nth-child(even) { background-color: #1a1a1a; }
            tr:nth-child(odd) { background-color: #262626; }
            img { max-width: 300px; height: auto; }
        </style>
    </head>
    <body>
        <center>
            <h2>XSS Vulnerability Report</h2>
            <h4>Daftar Payload pemicu pop up</h4>
        </center>
        <table>
            <thead>
                <tr>
                    <th>Payload</th>
                    <th>URL</th>
                    <th>Request Type</th>
                    <th>Screenshot</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Menambahkan payload yang rentan ke dalam tabel HTML
    if vulnerable_payloads:
        for item in vulnerable_payloads:
            html_content += f'''
                <tr>
                    <td>{html.escape(item['payload'])}</td>
                    <td><a href="{html.escape(item['url'])}" target="_blank">{html.escape(item['url'])}</a></td>
                    <td>{html.escape(item['request_type'])}</td>
                    <td><img src="{html.escape(item['screenshot'])}" alt="Screenshot XSS pop-up"></td>
                </tr>\n'''
    else:
        html_content += '<tr><td colspan="4">Tidak ada kerentanan XSS yang ditemukan.</td></tr>\n'
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Menyimpan konten HTML ke file
    with open(report_file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    return report_file_path

# Memindai URL terhadap XSS
def scan_xss(driver, url, payloads, request_type='GET', post_parameter=None):
    vulnerable_payloads = []
    print(f"Scanning {url} for XSS Vulnerability...")

    for payload in payloads:
        try:
            if request_type.upper() == 'POST' and post_parameter:
                driver.get(url)
                input_element = driver.find_element(By.NAME, post_parameter) # fitur komentar, userprofile, dsb
                input_element.clear()
                input_element.send_keys(payload)
                input_element.submit()
            else:
                full_url = url + payload
                driver.get(full_url)
            
            time.sleep(2)
            
            while True:
                try:
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                    print(f"\033[92m [+]Pop up alert found: {payload}\033[0m")
                    
                    screenshot_path = os.path.join(os.getenv('USERPROFILE'), f"screenshot_{int(time.time())}.png")
                    driver.save_screenshot(screenshot_path)
                    
                    vulnerable_payloads.append({
                        'payload': payload,
                        'url': url if request_type == 'POST' else full_url,
                        'request_type': request_type,
                        'screenshot': screenshot_path
                    })
                except:
                    break
        except Exception as e:
            logging.error(f"Error while scanning payload {payload}: {e}")
            continue
    
    return vulnerable_payloads

if __name__ == "__main__":
    banner()

    file_path = 'C:/path/path/path/path/XSSscaner/payloadxss.txt' #sesuaikan dengan file path anda
    user_profile = os.getenv('USERPROFILE')  
    save_folder_path = os.path.join(user_profile, f'XSS_Reports_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(save_folder_path, exist_ok=True)
    
    xss_payloads = read_payloads(file_path)
    target_url = input(Fore.CYAN + "Input Your Target Here (example: https://example.com/search?q=): " + Fore.RESET)
    
    request_type = input(Fore.YELLOW + "Request Type (GET/POST): " + Fore.RESET).strip().upper()
    
    post_parameter = None
    if request_type == "POST":
        post_parameter = input(Fore.YELLOW + "Enter POST parameter name: " + Fore.RESET).strip()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)  

    try:
        vulnerable_payloads = scan_xss(driver, target_url, xss_payloads, request_type, post_parameter)
        report_file_path = generate_html_report(save_folder_path, vulnerable_payloads)
        
        print(f"Laporan kerentanan XSS berhasil disimpan di: {report_file_path}")
        webbrowser.open('file:///' + report_file_path.replace('\\', '/'))
        
    finally:
        driver.quit()
