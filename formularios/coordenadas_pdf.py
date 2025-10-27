import fitz  # PyMuPDF
import os

def marcar_coordenadas_pdf(input_pdf, output_pdf, coordenadas_marcas):
    """
    Marca coordenadas específicas en el PDF con círculos o texto para identificar posiciones.

    coordenadas_marcas: lista de dicts con:
      {
        "x": 80, "y": 200,
        "label": "Posición 1",  # opcional
        "color": (1, 0, 0),    # rojo por defecto
        "size": 5              # tamaño del círculo
      }
    """
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        page = doc[page_num]

        for marca in coordenadas_marcas:
            x, y = marca["x"], marca["y"]
            color = marca.get("color", (1, 0, 0))  # rojo
            size = marca.get("size", 5)
            label = marca.get("label", f"({x},{y})")

            # Dibuja un círculo en la coordenada
            center_x, center_y = x, y
            page.draw_circle((center_x, center_y), size, color=color, fill=color)

            # Agrega etiqueta de texto cerca del círculo
            text_rect = fitz.Rect(x + size + 2, y - size, x + size + 100, y + size)
            page.insert_textbox(
                text_rect,
                label,
                fontsize=8,
                color=(0, 0, 0)
            )

    doc.save(output_pdf)
    doc.close()
    print(f"Marcas agregadas al PDF: {output_pdf}")

def crear_guia_coordenadas(input_pdf, output_pdf="guia_coordenadas.pdf"):
    """
    Crea un PDF con marcas en posiciones comunes para usar como guía.
    """
    # Marcas en posiciones estratégicas
    marcas = [
        {"x": 50, "y": 50, "label": "Esquina superior izquierda", "color": (1, 0, 0)},
        {"x": 300, "y": 50, "label": "Centro superior", "color": (0, 1, 0)},
        {"x": 550, "y": 50, "label": "Esquina superior derecha", "color": (0, 0, 1)},

        {"x": 50, "y": 300, "label": "Centro izquierda", "color": (1, 1, 0)},
        {"x": 300, "y": 300, "label": "Centro", "color": (1, 0, 1)},
        {"x": 550, "y": 300, "label": "Centro derecha", "color": (0, 1, 1)},

        {"x": 50, "y": 550, "label": "Esquina inferior izquierda", "color": (0.5, 0.5, 0.5)},
        {"x": 300, "y": 550, "label": "Centro inferior", "color": (0.5, 0, 0.5)},
        {"x": 550, "y": 550, "label": "Esquina inferior derecha", "color": (0, 0.5, 0.5)},

        # Más marcas específicas para formularios
        {"x": 100, "y": 100, "label": "Campo superior", "color": (1, 0.5, 0)},
        {"x": 100, "y": 200, "label": "Campo medio", "color": (0.5, 1, 0)},
        {"x": 100, "y": 400, "label": "Campo inferior", "color": (0, 0.5, 1)},
    ]

    marcar_coordenadas_pdf(input_pdf, output_pdf, marcas)

def probar_coordenada(input_pdf, x, y, output_pdf=None):
    """
    Prueba una coordenada específica agregando una marca visible.
    """
    if output_pdf is None:
        output_pdf = f"prueba_{x}_{y}.pdf"

    marca = [{"x": x, "y": y, "label": f"Prueba: ({x},{y})", "color": (1, 0, 0), "size": 8}]
    marcar_coordenadas_pdf(input_pdf, output_pdf, marca)
    print(f"PDF de prueba creado: {output_pdf}")

# ------------------ EJECUCIÓN ------------------
if __name__ == "__main__":
    import sys

    pdf_original = "formatos/formulario_de_afiliacion_eps_delagente_comfenalco_valle.pdf"

    if not os.path.exists(pdf_original):
        print(f"Error: No se encuentra el archivo {pdf_original}")
        exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--probar":
        if len(sys.argv) >= 4:
            try:
                x = float(sys.argv[2])
                y = float(sys.argv[3])
                print(f"Probando coordenada: ({x}, {y})")
                probar_coordenada(pdf_original, x, y)
            except ValueError:
                print("Coordenadas inválidas. Usa números.")
        else:
            print("Uso: python coordenadas_pdf.py --probar x y")
    else:
        # Ejecutar opción por defecto: crear guía de coordenadas
        print("Creando guía de coordenadas...")
        crear_guia_coordenadas(pdf_original)

        # Mostrar tamaño de página
        doc = fitz.open(pdf_original)
        page = doc[0]
        print(f"Tamaño de página: {page.rect.width} x {page.rect.height} puntos")
        doc.close()

        print("\nPara probar coordenadas específicas, ejecuta:")
        print("python coordenadas_pdf.py --probar x y")
        print("Ejemplo: python coordenadas_pdf.py --probar 100 200")