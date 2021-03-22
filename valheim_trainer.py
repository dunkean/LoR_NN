import pyautogui

pyautogui.sleep(2)
while(True):
    pyautogui.click()
    pyautogui.sleep(1.5)
    pyautogui.click()
    pyautogui.sleep(1.5)
    # pyautogui.click()
    pyautogui.sleep(0.5)
    pyautogui.keyDown('Z')
    pyautogui.sleep(1)
    pyautogui.keyUp('Z')