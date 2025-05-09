from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver_global = None

def iniciar_navegador():
    global driver_global

    options = Options()
    # Conectar ao Chrome já aberto
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    service = Service(ChromeDriverManager().install())
    driver_global = webdriver.Chrome(service=service, options=options)

    driver_global.get("https://www.google.com/search?q=python")

    if driver_global is None:
        #print("❌ Erro ao conectar ao navegador.")
        return None

    #print("✅ Conectado ao navegador já aberto.")
    driver_global.get("https://www.google.com/")
    return driver_global

def get_driver():
    return driver_global

def reiniciar_servidor(url):
    navegador = get_driver()
    if navegador:
        navegador.get(url)
        wait = WebDriverWait(navegador, 10)
        try:
            # Aguarda até que o botão de reiniciar esteja presente
            reiniciar_botao = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[2]/section/div[1]/div[2]/div[1]/button[2]")))
            try:
                reiniciar_botao.click()
                return True
            except Exception as e:
                print("Erro ao clicar no botão de reiniciar:", e)
                return False
            finally:
                # Sai da página para poupar recursos
                navegador.get("https://www.google.com/")
        except Exception as e:
            print(e)
            return False

def get_driver():
    return driver_global

if __name__ == "__main__":
    iniciar_navegador()