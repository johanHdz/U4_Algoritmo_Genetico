import tkinter as tk
from tkinter import colorchooser, messagebox
from tkinter.font import Font
import os
import numpy
import pygad
import gari
from PIL import Image, ImageTk


class Ventana:
    def __init__(self):
        # Creación de la ventana principal
        self.ventana = tk.Tk()
        # Color de fondo de la ventana
        colorFondo = "#e8e8e8"
        # Obtenemos las medidas de la pantalla para centrar la ventana
        ancho = self.ventana.winfo_screenwidth()
        alto = self.ventana.winfo_screenheight()
        x = (ancho - 800) // 2
        y = (alto - 700) // 2
        # Imagenes auxiliares
        self.imagenNueva = None
        self.imagenNuevaTk = None
        self.img_current_sol = None
        self.imagenReplicaTk = None
        # Número de gen. ini.
        self.iteraciones = 1000
        # Tamaño de imagenes
        self.tam = 150

        # Título
        self.ventana.title("Proyecto Algoritmos Genéticos")
        self.ventana.geometry('{}x{}+{}+{}'.format(800, 450, x, y))
        # Deshabilitar manipulación ancho y largo
        self.ventana.resizable(False, False)
        # Establecemos el color de fondo
        self.ventana.config(bg=colorFondo)
        # Fuente predeterminada
        fuente = Font(family="Arial Rounded MT Bold", size=14)

        # Graficación de la aplicación
        # Primer Frame para la imagen fuente
        frame1 = tk.Frame(self.ventana,
                          bd=5,
                          bg="#000")
        frame1.place(x=50, y=20)

        # Label de origen
        lbFuente = tk.Label(frame1,
                            text="Color origen",
                            font=fuente,
                            bg=colorFondo,
                            width=25)
        lbFuente.pack()

        # Imagen fuente
        imagenFuente = Image.new('RGB', (self.tam, self.tam), (255, 255, 255))
        imagenFuente = ImageTk.PhotoImage(imagenFuente)
        self.labelImgFuente = tk.Label(frame1, image=imagenFuente)
        self.labelImgFuente.pack()


        # Segundo frame para imagen resultante
        frame2 = tk.Frame(self.ventana,
                          bd=8,
                          bg="#000")
        frame2.place(x=430, y=20)

        # Label réplica
        lbReplica = tk.Label(frame2,
                             text="Imagen Replicada",
                             font=fuente,
                             fg="#000",
                             bg=colorFondo,
                             width=25)
        lbReplica.pack()

        # Imagen resultante
        imagenReplica = Image.new('RGB', (self.tam, self.tam), (255, 255, 255))
        imagenReplica = ImageTk.PhotoImage(imagenReplica)
        self.labelImgReplica = tk.Label(frame2, image=imagenReplica)
        self.labelImgReplica.pack()


        # Tercer frame para los botones e ingreso de datos
        frame3 = tk.Frame(self.ventana,
                          background=colorFondo)
        frame3.place(x=240, y=250)

        # Boton para seleccionar cualquier color
        btnSeleccionarColor = tk.Button(frame3,
                                        text="Seleccionar color",
                                        font=fuente,
                                        command=self.seleccionar_color)
        btnSeleccionarColor.pack(side="top")

        # Botón para ejecutar el algoritmo genetico
        btnEjecutarAlgoritmo = tk.Button(frame3,
                                         text="Ejecutar algoritmo genético",
                                         font=fuente,
                                         command=self.ejecutar_algoritmo)
        btnEjecutarAlgoritmo.pack(side="bottom")

        # Label Iteraciones
        lbIteraciones = tk.Label(frame3,
                                 text="Núm. de Generaciones:",
                                 font=fuente,
                                 background=colorFondo)
        lbIteraciones.pack(side="left", pady=10)

        # Entry
        self.entryIteraciones = tk.Entry(frame3,
                                         font=fuente,
                                         validate="key",
                                         validatecommand=(frame3.register(self.validar_entrada), '%P'),
                                         width=10)
        self.entryIteraciones.pack(side="right", pady=10)

        # Label numero de generaciones
        self.lbGeneraciones = tk.Label(self.ventana,
                                       text="Generación: 0",
                                       font=fuente,
                                       background=colorFondo)
        self.lbGeneraciones.place(x=340, y=390)

        # Evento principal del programa
        self.ventana.mainloop()

    # Función para que la entrada de datos sea solo númerica
    def validar_entrada(self, valor):
        if valor == "":
            return True
        try:
            int(valor)
            return True
        except ValueError:
            return False

    def seleccionar_color(self):
        try:
            color = colorchooser.askcolor(title="Selecciona un color")
            self.imagenNueva = Image.new('RGB', (self.tam, self.tam), color[0])
            self.crear_imagen(self.imagenNueva)
            self.imagenNuevaTk = ImageTk.PhotoImage(self.imagenNueva)
            self.labelImgFuente.configure(image=self.imagenNuevaTk)
            print("Hex:{} RGB:{}".format(color[1], color[0]))
        except Exception as e:
            print("Error: ", e)

    def ejecutar_algoritmo(self):
        try:
            # Obtenemos el número de generaciones
            self.iteraciones = int(self.entryIteraciones.get())
            # Inicializamos el algoritmo
            self.inicializar_algoritmo()
        except Exception as err:
            messagebox.showerror("Error", "Ingrese un número")

    def crear_imagen(self, imagen):
        imagen.save("color.png")

    # Función para evaluar la aptitud o "fitness" de una solución candidata en función de
    # cómo se adapta a la solución deseada o al problema a resolver
    def fitness_fun(self, solution, solution_idx):
        """
        El valor de aptitud se calcula utilizando la suma de la diferencia absoluta entre los valores de los genes en
        los cromosomas originales y reproducidos.

        solution: Solución actual en la población para calcular su aptitud.
        solution_idx: Índice de la solución en la población.
        """
        # Convertir la solución a una matriz de píxeles
        # arr_solucion = numpy.array(solution.reshape((self.tam, self.tam, 3)), dtype=numpy.uint8)
        fitness = numpy.sum(numpy.abs(self.target_chromosome - solution))
        # Calcular la diferencia entre la solución y la imagen objetivo
        # diferencia = numpy.sum(numpy.abs(arr_solucion - self.target_im))
        fitness = numpy.sum(self.target_chromosome) - fitness
        # Devolver el valor de evaluación (mayor valor = solución más lejana de la imagen objetivo)
        return fitness

    # Esta función se llama automáticamente después de cada generación en el proceso de optimización.
    def callback(self, ga_instance):
        # Imprimimos la generación actual y su aptitud
        gen = "Generación: {}".format(ga_instance.generations_completed)
        self.lbGeneraciones.config(text=gen)

        # Se muestra la imagen de la generación cada 10 generaciones
        if ga_instance.generations_completed % 10 == 0:
            current_sol = self.ga_instance.best_solution()[0]
            self.img_current_sol = current_sol.reshape(self.target_im.shape).astype(numpy.uint8)
            self.img_current_sol = Image.fromarray(self.img_current_sol)
            self.imagenReplicaTk = ImageTk.PhotoImage(self.img_current_sol)
            self.labelImgReplica.configure(image=self.imagenReplicaTk)
            self.ventana.update()

        # Actualizamos la ventana
        self.ventana.update_idletasks()

    # Función para inicializar todos las variables y parámetros necesarios para utilizar Pygad
    def inicializar_algoritmo(self):
        # Lectura de una imagen que se quiere reproducir usando un algoritmo genético.

        try:
            # Convertimos la solución a una matriz de píxeles
            self.target_im = numpy.array(self.imagenNueva)

            self.target_chromosome = gari.img2chromosome(self.target_im)

            # Instancia de pygad, se utiliza el constructor con los múltiples parámetros necesarios para que pygad pueda
            # trabajar con su algoritmo genetico.
            # Pygad tiene una gran variedad de parámetros que sirven para personalizar el algoritmo genético dependiendo
            # de la aplicación que nosotros le quedamos dar.
            self.ga_instance = pygad.GA(num_generations=self.iteraciones,  # Número de generaciones
                                        num_parents_mating=4,  # Número de padres seleccionados para el cruce
                                        fitness_func=self.fitness_fun,  # Función de aptitud
                                        sol_per_pop=8,  # Tamaño de la población
                                        num_genes=self.tam*self.tam*3,  # Número de genes
                                        # Valor mínimo del intervalo aleatorio del que se seleccionan los valores
                                        # genéticos de la población inicial.
                                        init_range_low=0.0,
                                        # Valor máximo del intervalo aleatorio del que se seleccionan los valores
                                        # genéticos de la población inicial.
                                        init_range_high=255.0,
                                        mutation_percent_genes=0.5,  # Porcentaje de genes que mutan
                                        mutation_type="random",  # Tipo de mutación
                                        # Sustituye el gen por el valor generado aleatoriamente
                                        mutation_by_replacement=True,
                                        # Especifica el valor inicial del intervalo a partir del cual se selecciona
                                        # un valor aleatorio que se añade al gen
                                        random_mutation_min_val=0.0,
                                        # Especifica el valor final del intervalo a partir del cual se selecciona un
                                        # valor aleatorio que se añade al gen
                                        random_mutation_max_val=255.0,
                                        # Función que se llama automáticamente después de cada generación
                                        callback_generation=self.callback)
            # Se inicia el algoritmo genético
            self.ga_instance.run()
        except Exception as err:
            messagebox.showerror("Error", "Ha ocurrido un error")
            print("Error: ", err)


# Programa principal
if os.path.exists('./color.png'):
    os.remove('./color.png')
ventana = Ventana()
