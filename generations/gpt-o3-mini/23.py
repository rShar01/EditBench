from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
import win32gui
import win32con


def ocultar_janela_chrome():
    """Oculta a janela do Chrome usando win32gui"""
    def callback(hwnd, windows):
        if "chrome" in win32gui.GetWindowText(hwnd).lower():
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        return True

    win32gui.EnumWindows(callback, None)


no_number_button_path = '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[2]/div/button'
# carregou //*[@id="app"]/div/div[2]/div[2]

# options.add_argument('--headless')
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')
# input('aa')

timer = 0
print('Aguardando o carregamento das conversas...')
while True:
    if timer > 180:
        sys.exit()

    try:
        element = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]')
        if element:
            element_text = element.text
            print(element_text)

            if "Carregando suas conversas" in element_text:
                break

    except Exception:
        pass

    timer = timer + 1
    time.sleep(1)


# input('Pressione Enter após fazer o login com QR code...')
print('LOGADO!')
time.sleep(5)  # Espera carregar a sessão


def verificar_numero_whatsapp(numero):
    try:
        url = f"https://web.whatsapp.com/send/?phone={numero}"
        driver.get(url)

        # Define um tempo máximo de espera
        wait = WebDriverWait(driver, 20)

        try:
            # Espera pelo elemento de chat ou mensagem de erro
            _ = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]')
                )
            )
            return True

        except TimeoutException:
            # Verifica se existe mensagem de erro
            try:
                _ = driver.find_element(By.XPATH, no_number_button_path)
                return False
            except NoSuchElementException:
                return False

    except Exception as ex:
        print(f'Erro inesperado: {ex}')
        return False


def verificar_lista_numeros(numeros):
    resultados = {}
    for numero in numeros:
        resultado = verificar_numero_whatsapp(numero)
        print(f'RESULTADO: {resultado}')
        resultados[numero] = resultado
        time.sleep(2)
    return resultados


# Exemplo de uso
if __name__ == "__main__":
    numeros_teste = [
        "5519996287504545"
    ]

    try:
        resultados = verificar_lista_numeros(numeros_teste)

        for numero, existe in resultados.items():
            status = "está" if existe else "não está"
            print(f"O número {numero} {status} registrado no WhatsApp")
    finally:
        driver.quit()  # Garante que o driver seja fechado ao finalizar
