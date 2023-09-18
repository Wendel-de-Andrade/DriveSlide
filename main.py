import os
import tempfile
import time
import threading
import atexit
import tkinter as tk
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tkinter import *
from PIL import Image, ImageTk
import keyboard
import shutil
import customtkinter
from functools import partial
import pickle
import tkinter.messagebox as messagebox

# Salva as últimas entradas do programa em um arquivo em Documents
def save_last_entry(folder_id, check_interval, slide_interval):
    documents_folder = os.path.expanduser("~/Documents")
    pickle_file_path = os.path.join(documents_folder, "DriveSlideConfig.pickle")
    
    with open(pickle_file_path, "wb") as f:
        pickle.dump((folder_id, check_interval, slide_interval), f)

# Carrega as últimas entradas do programa usando o arquivo em Documents, caso seja a primeira vez abrindo o programa ele retorna "None, None, None"
def load_last_entry():
    try:
        documents_folder = os.path.expanduser("~/Documents")
        pickle_file_path = os.path.join(documents_folder, "DriveSlideConfig.pickle")
        
        with open(pickle_file_path, "rb") as f:
            folder_id, check_interval, slide_interval = pickle.load(f)
            return folder_id, check_interval, slide_interval
    except FileNotFoundError:
        return None, None, None
    
# Função principal da tela de Slide
def slide(folder_id, check_interval, slide_interval):
    
    # Configuração inicial de váriaveis
    def setup(folder_id, check_interval, slide_interval):
        temp_dir = create_temp_dir()
        drive = authenticate_google_drive()
        images = download_images(drive, folder_id, temp_dir)
        downloaded_file_names = get_downloaded_file_names(drive, folder_id)

        return temp_dir, drive, images, downloaded_file_names, check_interval, slide_interval

    # Cria um diretório temporário e registra sua limpeza no fechamento do programa
    def create_temp_dir():
        temp_dir = tempfile.mkdtemp()
        atexit.register(cleanup_temp_dir, temp_dir)
        return temp_dir

    def cleanup_temp_dir(temp_dir):
        shutil.rmtree(temp_dir)

    # Autenticação do Google Drive
    def authenticate_google_drive():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return GoogleDrive(gauth)

    # Baixa imagens do Google Drive e atualiza a lista de imagens
    def download_images(drive, folder_id, temp_dir):
        try:
            file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
            image_paths = []

            for file in file_list:
                if 'image' in file['mimeType']:
                    image_content = drive.CreateFile({'id': file['id']})
                    image_path = os.path.join(temp_dir, file['title'])
                    image_content.GetContentFile(image_path)
                    image_paths.append(image_path)

            return image_paths
        except Exception as e:
            messagebox.showerror("Erro", "A pasta do Google Drive não foi encontrada ou não está compartilhada. Verifique o ID da pasta e as configurações de compartilhamento.")
            root.destroy()  # Fecha a janela se ocorrer um erro

    # Obtém os nomes dos arquivos baixados do Google Drive
    def get_downloaded_file_names(drive, folder_id):
        file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        return set(file['title'] for file in file_list)

    # Obtém os nomes dos arquivos na pasta temporária
    def get_temp_file_names(temp_dir):
        return set(os.listdir(temp_dir))

    # Verifica e atualiza as imagens a cada check_interval (em segundos)
    def check_and_update_images(drive, folder_id, temp_dir, images, downloaded_file_names, check_interval):
        while True:
            try:
                # print("Iniciando verificação do Google Drive...")  # Adiciona uma mensagem de log
                temp_file_names = get_temp_file_names(temp_dir)

                download_new_images(drive, temp_dir, images, downloaded_file_names, temp_file_names)
                delete_unused_images(temp_dir, downloaded_file_names)

            except Exception as e:
                # print(f"Erro ao verificar/atualizar imagens: {str(e)}")
                messagebox.showerror("Erro", "Erro ao verificar/atualizar imagens, favor tentar novamente mais tarde!")
                root.destroy()  # Fecha a janela se ocorrer um erro

            time.sleep(check_interval)

    # Baixa novas imagens que estão no Google Drive, mas não na pasta temporária
    def download_new_images(drive, temp_dir, images, downloaded_file_names, temp_file_names):
        for file in drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList():
            if 'image' in file['mimeType'] and file['title'] not in temp_file_names:
                image_content = drive.CreateFile({'id': file['id']})
                image_path = os.path.join(temp_dir, file['title'])
                image_content.GetContentFile(image_path)
                images.append(image_path)
                downloaded_file_names.add(file['title'])

    # Exclui imagens na pasta temporária que não estão no Google Drive
    def delete_unused_images(temp_dir, downloaded_file_names):
        for file_name in downloaded_file_names.copy():
            if file_name not in downloaded_file_names:
                file_path = os.path.join(temp_dir, file_name)
                os.remove(file_path)
                downloaded_file_names.remove(file_name)
                images.remove(file_path)
                
    # Redimensiona uma imagem mantendo a proporção
    def resize_image(image_path, new_width, new_height):
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height

        if new_width / aspect_ratio < new_height:
            new_height = int(new_width / aspect_ratio)
        else:
            new_width = int(new_height * aspect_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    # Atualiza as imagens
    def update_images(image_label, images, current_image_idx, slide_interval):
        current_image_idx += 1
        if current_image_idx >= len(images):
            current_image_idx = 0

        image_path = images[current_image_idx]

        if os.path.exists(image_path):
            photo = resize_image(image_path, screen_width, screen_height)
            image_label.config(image=photo)
            image_label.image = photo
            
        else:
            # print(f"Arquivo não encontrado: {image_path}")
            messagebox.showerror("Erro", f"Arquivo não encontrado: {image_path}")
            root.destroy()  # Fecha a janela se ocorrer um erro

        root.after(slide_interval, partial(update_images, image_label, images, current_image_idx, slide_interval))

    # Função para fechar a janela
    def on_closing():
        root.destroy()
        cleanup_temp_dir(temp_dir)
        
     # Aplcando as informações das variáveis no setup
    temp_dir, drive, images, downloaded_file_names, check_interval, slide_interval = setup(folder_id, check_interval, slide_interval)
    current_image_idx = 0

    # Cria a tela do Slide como secundária da tela principal "gui"
    root = tk.Toplevel(gui)
    root.attributes('-fullscreen', True)
    root.title("Google Drive Image Slideshow")

    # Fecha a janela quando a tecla "ESC" for pressionada
    keyboard.add_hotkey('esc', root.destroy)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    image_label = Label(root)
    image_label.pack()

    # Inicia a função de verificação de imagens em uma thread separada (evita travamentos na hora da verificação)
    check_thread = threading.Thread(target=check_and_update_images, args=(drive, folder_id, temp_dir, images, downloaded_file_names, check_interval))
    check_thread.daemon = True
    check_thread.start()

    update_images(image_label, images, current_image_idx, slide_interval)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

# Inicia a tela de configuração do programa
customtkinter.set_appearance_mode("system")
gui = customtkinter.CTk()

gui.geometry("350x350")
gui.resizable(False, False)
gui.title("Slide from Drive by WendelSH09")

# Carrega as últimas informações colocadas nos campos de texto
def load_and_fill_last_entry():
    global folder_id, check_interval, slide_interval

    folder_id, check_interval, slide_interval = load_last_entry()

    if folder_id:
        folder_entry.delete(0, "end")
        folder_entry.insert(0, folder_id)

    if check_interval:
        combobox_1.set(str(check_interval))

    if slide_interval:
        combobox_2.set(str(slide_interval // 1000))
        
# Insere as informaçãoes colocadas no programa em váriaveis e chama a função do Slide
def slide_init():
    global folder_id, check_interval, slide_interval

    folder_id = folder_entry.get()
    check_interval = int(combobox_1.get())
    slide_interval = int(combobox_2.get())
    slide_interval *= 1000
    
    save_last_entry(folder_id, check_interval, slide_interval)
    slide(folder_id, check_interval, slide_interval)

# Frame para organizar os elementos internamente
frame1 = customtkinter.CTkFrame(master=gui)
frame1.pack(pady=20, padx=60, fill="both", expand=True)

folder_label = customtkinter.CTkLabel(frame1, text="ID da Pasta do DRIVE", anchor="w")
folder_label.grid(row=0, column=0, padx=45, pady=(10, 0))
folder_entry = customtkinter.CTkEntry(frame1, placeholder_text="ID da Pasta")
folder_entry.grid(row=1, column=0, columnspan=1, padx=45, pady=0, sticky="nsew")

sec_label = customtkinter.CTkLabel(frame1, text="Intervalo de Verificação", anchor="w")
sec_label.grid(row=3, column=0, padx=45, pady=(20, 0))
combobox_1 = customtkinter.CTkComboBox(frame1, values=["10", "30", "60"])
combobox_1.grid(row=4, column=0, padx=45, pady=0)

tempo_label = customtkinter.CTkLabel(frame1, text="Tempo do Slide", anchor="w")
tempo_label.grid(row=5, column=0, padx=45, pady=(20, 0))
combobox_2 = customtkinter.CTkComboBox(frame1, values=["2", "3", "4", "5", "6", "7", "8", "9"])
combobox_2.grid(row=6, column=0, padx=45, pady=0)

start_button = customtkinter.CTkButton(frame1, text="Iniciar", command=slide_init)
start_button.grid(row=7, column=0, padx=20, pady=50)    

# Roda o programa principal, mas antes, chama a função para carregar as últimas predefinições
if __name__ == "__main__":
    load_and_fill_last_entry()

    gui.mainloop()