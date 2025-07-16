def centrar_ventana(ventana, ventana_padre, ancho=800, alto=600):
    ventana.update_idletasks()
    x = ventana_padre.winfo_x() + (ventana_padre.winfo_width() // 2) - (ancho // 2)
    y = ventana_padre.winfo_y() + (ventana_padre.winfo_height() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")