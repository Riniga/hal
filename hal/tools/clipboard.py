import pyperclip

def get_clipboard_text():
    clipboard_content = pyperclip.paste()
    if  isinstance(clipboard_content, str):
        return clipboard_content
    else:
        print('No clipboard text to copy')
        return None