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
from flask import Flask, render_template, request, redirect

class seguimientoDeVacunas:

    def __init__(self):
        self.listadoDeMascotas = {}
        carpeta = os.path.dirname(__file__)
        self.data_file = os.path.join(carpeta, "registro visible.json")
        self.cargasrTodo()
    
    def guardarAimal (self):
        
        with open(self.data_file, "w") as f:
            json.dump(self.listadoDeMascotas, f)

    def cargasrTodo (self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.listadoDeMascotas = json.load(f)
        else:
            self.listadoDeMascotas = {}

# 🔥 AQUÍ EMPIEZA FLASK

app = Flask(__name__)
gestor = seguimientoDeVacunas()

# Página principal
@app.route("/")
def inicio():
    print(gestor.listadoDeMascotas)
    return render_template("index.html", mascotas=gestor.listadoDeMascotas)

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
    app.run(debug=True)