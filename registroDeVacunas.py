# registro de vacunas 

# ideas:

# mejorar la visualizacion de los animales 
# hacer la interface 
# hacer que los mas sercanos a la fecha actual se pongan en una mini lista de 5 
# que se almacene exel si se puede (que se mantenga todo local para que sea mas seguro)

# ideas hacer que todo este en una sola paguina exepto la lista 
# que se pueda ver todod en un exel

import json
import os
# esto es para correrlo con un html(tambien se usa el venv)
from flask import Flask, render_template, request, redirect
#esto es para crear un exel
from openpyxl import Workbook, load_workbook
# esto es para abrir el navegadro
import webbrowser
# esto es para crear un dilay al ejecutar el ejecutable
import threading

import sys

class seguimientoDeVacunas:

    def __init__(self):
        self.listadoDeMascotas = {}

        import os

        base_path = os.path.join(os.getenv("APPDATA"), "GestorVacunas")
        data_folder = os.path.join(base_path, "data")
        os.makedirs(data_folder, exist_ok=True)

        self.data_file = os.path.join(data_folder, "registro_visible.json")
        self.exel_file = os.path.join(data_folder, "backup.xlsx")

        print("Ruta JSON:", self.data_file)

        self.cargasrTodo()
    
    def guardarAimal (self):
        
        with open(self.data_file, "w") as f:
            json.dump(self.listadoDeMascotas, f, indent=4)

    def cargasrTodo (self):

        print("Ruta JSON:", self.data_file)

        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.listadoDeMascotas = json.load(f)
        else:
            self.listadoDeMascotas = {}

    def exportar_exel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "vacunas"

        ws.append(["Nombre", "Vacuna", "Fecha"])

        for nombre, vacunas in self.listadoDeMascotas.items():
            for v in vacunas:
                ws.append([nombre, v["vacuna"], v["fecha"]])
        
        wb.save(self.exel_file)
    
    def importar_exel(self):
        if not os.path.exists(self.exel_file):
            return
        
        wb = load_workbook(self.exel_file)
        ws = wb.active

        nuevo = {}

        for row in ws.iter_rows(min_row=2, values_only=True):
            nombre, vacuna, fecha = row

            #  validacion basica
            if not nombre or not vacuna:
                continue
            
            if nombre not in nuevo:
                nuevo[nombre] = []
            
            nuevo[nombre].append({
                "vacuna": vacuna,
                "fecha": str(fecha)
            })
        self.listadoDeMascotas = nuevo
        self.guardarAimal()

# 🔥 AQUÍ EMPIEZA FLASK

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

app = Flask(__name__, template_folder=os.path.join(base_path, "templates"))

gestor = seguimientoDeVacunas()

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

# Página principal
@app.route("/")
def inicio():

    # buscador de mascotas
    busqueda = request.args.get("buscar", "").lower()
    print("Buscando: ", busqueda)

    if busqueda:
        filtrado = {
            nombre: vacunas
            for nombre, vacunas in gestor.listadoDeMascotas.items()
            if busqueda in nombre.lower()
        }
    else:
        filtrado = gestor.listadoDeMascotas
    
    return render_template("index.html", mascotas=filtrado)


# exportar a exel
@app.route("/exportar")
def exportar():
    gestor.exportar_exel()
    return redirect("/")

#importar desde Exel
@app.route("/importar")
def importar():
    gestor.importar_exel()
    return redirect("/")

# Agregar mascota
@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    vacuna = request.form["vacuna"]
    fecha = request.form["fecha"]

    nueva = {"vacuna": vacuna, "fecha": fecha}

    if nombre in gestor.listadoDeMascotas:
        gestor.listadoDeMascotas[nombre].append(nueva)
    else:
        gestor.listadoDeMascotas[nombre] = [nueva]

    # gestor.listadoDeMascotas[nombre] = fecha
    gestor.guardarAimal()

    return redirect("/")

# Eliminar mascota
@app.route("/eliminar/<nombre>")
def eliminar(nombre):
    if nombre in gestor.listadoDeMascotas:
        del gestor.listadoDeMascotas[nombre]
        gestor.guardarAimal()

    return redirect("/")

# Actualizar vacuna
@app.route("/actualizar", methods=["POST"])
def actualizar():
    nombre = request.form["nombre"]
    vacunas = request.form["vacuna"]
    nueva_fecha = request.form["fecha"]

    if nombre in gestor.listadoDeMascotas:
        for v in gestor.listadoDeMascotas[nombre]:
            if v["vacuna"] == vacunas:
                v["fecha"] = nueva_fecha
                break
        gestor.guardarAimal()

    return redirect("/")

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    app.run(debug=True)