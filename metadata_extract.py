import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import os


class MetadataViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metadata Viewer V1.1")
        self.root.geometry("1000x500")
        self.root.minsize(1000, 500)

        # Enable drag-and-drop support
        self.root.tk.call('package', 'require', 'tkdnd')

        # Main frame with rounded corners effect and blue border
        self.main_frame = tk.Frame(root, bd=2, relief=tk.SOLID, bg='deepskyblue2')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Inner frame (ahora en skyblue1 también)
        self.inner_frame = tk.Frame(self.main_frame, bg='skyblue1', bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title Label centered
        self.title_label = tk.Label(
            self.inner_frame,
            text="METADATA VIEWER 1.1",
            font=("Arial", 16, "bold"),
            bg="skyblue1"
        )
        self.title_label.pack(pady=10)

        # Left and right frames for layout
        self.content_frame = tk.Frame(self.inner_frame, bg='skyblue1')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left side - Metadata
        self.left_frame = tk.Frame(self.content_frame, bg='skyblue1')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Drop area with border
        self.drop_frame = tk.Frame(self.left_frame, bg='skyblue1', bd=2, relief=tk.SOLID)
        self.drop_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.drop_label = tk.Label(
            self.drop_frame,
            text="Drop file here",
            font=("Arial", 12),
            bg="lightgray",
            height=3
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)

        # Almacenar los campos de metadata en un diccionario para fácil acceso
        self.metadata_labels = {}
        self.metadata_labels['noise_seed'] = self.create_metadata_field(self.left_frame, "Noise Seed :")
        self.metadata_labels['lora'] = self.create_metadata_field(self.left_frame, "Lora :")
        self.metadata_labels['strength'] = self.create_metadata_field(self.left_frame, "Strength :")
        self.metadata_labels['unet_name'] = self.create_metadata_field(self.left_frame, "Unet Name :")
        
        # Campo de texto con fondo verde claro y borde para el prompt
        self.text_frame = tk.Frame(self.left_frame, bg='lightblue1', bd=2, relief=tk.SOLID)
        self.text_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.text_frame, text="Prompt:", font=("Arial", 11, "bold"), bg='lightblue1').pack(anchor=tk.W, padx=5, pady=2)
        self.text_widget = tk.Text(self.text_frame, height=4, wrap=tk.WORD, bg='lightblue1', bd=0)
        self.text_widget.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.text_widget.config(state="disabled")

        # Right side - Image Preview
        self.right_frame = tk.Frame(self.content_frame, bg='lightblue')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # Vista previa de la imagen con fondo lavanda y borde
        self.preview_frame = tk.Frame(self.right_frame, bg='slate blue', bd=2, relief=tk.SOLID)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_preview_label = tk.Label(
            self.preview_frame,
            text="Image Preview",
            font=("Arial", 12),
            bg="slate blue"
        )
        self.image_preview_label.pack(fill=tk.BOTH, expand=True)

    def create_metadata_field(self, parent, label_text, initial_value=""):
        frame = tk.Frame(parent, bg='skyblue1')
        frame.pack(fill=tk.X, pady=2)
        
        # Etiqueta para el nombre del campo (Label)
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 11, "bold"),
            bg='skyblue1',
            anchor='w'
        )
        label.pack(side=tk.LEFT)
        
        # Campo de texto para el valor (Text)
        value_text = tk.Text(
            frame,
            height=1,
            font=("Arial", 11),
            bg='springgreen2',
            wrap=tk.NONE,
            bd=0
        )
        value_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        value_text.insert(tk.END, initial_value)
        value_text.config(state="disabled")  # Sólo lectura
        
        return value_text

    def handle_drop(self, event):
        file_path = event.data.strip()
        if os.path.isfile(file_path):
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            # Cargar la imagen
            image = Image.open(file_path)
            
            # Obtener dimensiones originales
            original_width, original_height = image.size
            
            # Calcular dimensiones a la mitad
            preview_width = original_width // 2
            preview_height = original_height // 2
            
            # Ajustar la geometría de la ventana según las dimensiones de la imagen
            if preview_width > preview_height:
                self.root.geometry("1575x520")
                self.root.minsize(1575, 520)
            else:
                self.root.geometry("1300x815")
                self.root.minsize(1300, 815)

            # Redimensionar la imagen a la mitad
            image = image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)

            # Crear imagen de vista previa
            self.image_preview = ImageTk.PhotoImage(image)

            # Configurar el label para mostrar la imagen
            self.image_preview_label.config(
                image=self.image_preview, 
                text=""
            )

            # Extraer y mostrar los metadatos desde el campo "prompt" incrustado en el PNG
            if not isinstance(image.info, dict) or "prompt" not in image.info:
                raise ValueError("No valid metadata found in the PNG file.")

            metadata = json.loads(image.info["prompt"])

            # Actualizar los campos de metadatos usando el nuevo JSON:
            # - Noise Seed: se obtiene de la llave "1402:0" -> inputs -> noise_seed
            # - Lora y Strength: se obtienen de la llave "1404" -> inputs -> lora_1
            # - Unet Name: se obtiene de la llave "1408" -> inputs -> unet_name
            # - Prompt: se obtiene de la llave "1403:0" -> inputs -> text

            self.update_text_widget(
                self.metadata_labels['noise_seed'], 
                str(metadata.get("1402:0", {}).get("inputs", {}).get("noise_seed", "N/A"))
            )
            self.update_text_widget(
                self.metadata_labels['lora'], 
                str(metadata.get("1404", {}).get("inputs", {}).get("lora_1", {}).get("lora", "N/A"))
            )
            self.update_text_widget(
                self.metadata_labels['strength'], 
                str(metadata.get("1404", {}).get("inputs", {}).get("lora_1", {}).get("strength", "N/A"))
            )
            self.update_text_widget(
                self.metadata_labels['unet_name'], 
                str(metadata.get("1408", {}).get("inputs", {}).get("unet_name", "N/A"))
            )

            # Actualizar el campo de texto para el prompt
            self.text_widget.config(state="normal")
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, metadata.get("1403:0", {}).get("inputs", {}).get("text", "N/A"))
            self.text_widget.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            
    def update_text_widget(self, text_widget, new_text):
        text_widget.config(state="normal")  # Habilitar edición temporalmente
        text_widget.delete(1.0, tk.END)       # Borrar contenido actual
        text_widget.insert(tk.END, new_text)  # Insertar nuevo texto
        text_widget.config(state="disabled")  # Deshabilitar edición nuevamente


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MetadataViewerApp(root)
    root.mainloop()
