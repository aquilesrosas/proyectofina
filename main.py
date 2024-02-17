import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from email.mime.text import MIMEText
from smtplib import SMTP
from datetime import datetime, timedelta

class RegistroGastosIngresosApp:
    def __init__(self, master):
        self.master = master

        # Crear variables de control
        self.fecha_actual = tk.StringVar()
        self.concepto = tk.StringVar()
        self.tipo_transaccion = tk.StringVar()
        self.descripcion = tk.StringVar()
        self.monto = tk.DoubleVar()

        # Establecer la fecha actual
        self.fecha_actual.set(datetime.now().strftime("%Y-%m-%d"))

        # Lista de conceptos
        self.lista_conceptos = self.cargar_conceptos()

        # Crear widgets
        tk.Label(master, text="Fecha:").grid(row=0, column=0, sticky="w")
        tk.Entry(master, textvariable=self.fecha_actual, state="readonly").grid(row=0, column=1)
        tk.Label(master, text="Concepto:").grid(row=1, column=0, sticky="w")
        self.combobox_concepto = ttk.Combobox(master, textvariable=self.concepto, values=self.lista_conceptos)
        self.combobox_concepto.grid(row=1, column=1)
        tk.Label(master, text="Tipo de Transacción:").grid(row=2, column=0, sticky="w")
        tk.Radiobutton(master, text="Gasto", variable=self.tipo_transaccion, value="Gasto").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(master, text="Ingreso", variable=self.tipo_transaccion, value="Ingreso").grid(row=2, column=2, sticky="w")
        tk.Label(master, text="Descripción:").grid(row=3, column=0, sticky="w")
        tk.Entry(master, textvariable=self.descripcion).grid(row=3, column=1)
        tk.Label(master, text="Monto:").grid(row=4, column=0, sticky="w")
        tk.Entry(master, textvariable=self.monto).grid(row=4, column=1)
        tk.Button(master, text="Registrar", command=self.registrar_transaccion).grid(row=5, column=0, columnspan=2)
        tk.Button(master, text="Agregar Concepto", command=self.agregar_concepto).grid(row=1, column=2, sticky="w")
        tk.Button(master, text="Quitar Concepto", command=self.quitar_concepto).grid(row=1, column=3, sticky="w")
        tk.Button(master, text="Ver Transacciones", command=self.ver_transacciones).grid(row=5, column=1, columnspan=2)
        tk.Button(master, text="Enviar Reporte Semanal", command=lambda: self.enviar_reporte("Semanal")).grid(row=5, column=2, columnspan=2)
        tk.Button(master, text="Enviar Reporte Quincenal", command=lambda: self.enviar_reporte("Quincenal")).grid(row=5, column=4, columnspan=2)
        tk.Button(master, text="Enviar Reporte Mensual", command=lambda: self.enviar_reporte("Mensual")).grid(row=5, column=6, columnspan=2)

    def cargar_conceptos(self):
        try:
            with open("conceptos.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            return ["Gasolina", "Comida", "Transporte", "Educación", "Otros"]

    def guardar_conceptos(self):
        with open("conceptos.txt", "w") as file:
            for concepto in self.lista_conceptos:
                file.write(concepto + "\n")

    def registrar_transaccion(self):
        fecha = self.fecha_actual.get()
        concepto = self.concepto.get()
        tipo_transaccion = self.tipo_transaccion.get()
        descripcion = self.descripcion.get()
        monto = self.monto.get()

        # Guardar los datos en un archivo de texto
        with open("registros.txt", "a") as file:
            file.write(f"Fecha: {fecha}\n")
            file.write(f"Concepto: {concepto}\n")
            file.write(f"Tipo de Transaccion: {tipo_transaccion}\n")
            file.write(f"Descripcion: {descripcion}\n")
            file.write(f"Monto: {monto}\n\n")

        # Mensaje de confirmación
        messagebox.showinfo("Registro Exitoso", "La transacción ha sido registrada con éxito.")

    def agregar_concepto(self):
        nuevo_concepto = simpledialog.askstring("Agregar Concepto", "Ingrese el nuevo concepto:")
        if nuevo_concepto:
            self.lista_conceptos.append(nuevo_concepto)
            self.combobox_concepto['values'] = self.lista_conceptos
            self.guardar_conceptos()

    def quitar_concepto(self):
        if self.combobox_concepto.get() in self.lista_conceptos:
            self.lista_conceptos.remove(self.combobox_concepto.get())
            self.combobox_concepto['values'] = self.lista_conceptos
            self.guardar_conceptos()

    def ver_transacciones(self):
        ventana = tk.Toplevel(self.master)
        ventana.title("Ver Transacciones")

        tk.Label(ventana, text="Filtro por Concepto:").grid(row=0, column=0, sticky="w")
        concepto_filtro = ttk.Combobox(ventana, values=self.lista_conceptos)
        concepto_filtro.grid(row=0, column=1)

        texto_transacciones = tk.Text(ventana, height=10, width=50)
        texto_transacciones.grid(row=1, column=0, columnspan=2)

        # Leer el archivo de registros y mostrar en el Text
        with open("registros.txt", "r") as file:
            for linea in file:
                if linea.startswith("Concepto:"):
                    concepto = linea.split(":")[1].strip()
                    if not concepto_filtro.get() or concepto == concepto_filtro.get():
                        texto_transacciones.insert(tk.END, linea)

    def enviar_reporte(self, tipo_reporte):
        total_gastos = 0
        fecha_actual = self.fecha_actual.get()  # Suponiendo que fecha_actual es algún widget de fecha

        try:
            fecha_actual = datetime.strptime(fecha_actual, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Fecha actual no válida")
            return

        # Determinar el rango de fechas según el tipo de reporte
        if tipo_reporte == "Semanal":
            fecha_inicio = fecha_actual - timedelta(days=7)
        elif tipo_reporte == "Quincenal":
            fecha_inicio = fecha_actual - timedelta(days=15)
        elif tipo_reporte == "Mensual":
            fecha_inicio = fecha_actual.replace(day=1)
        else:
            messagebox.showerror("Error", "Tipo de reporte no válido")
            return

        try:
            with open("registros.txt", "r") as file:
                for line in file:
                    if line.startswith("Fecha:"):
                        try:
                            fecha_registro = datetime.strptime(line.split(":")[1].strip(), "%Y-%m-%d")
                        except ValueError:
                            print("Error al parsear la fecha:", line.split(":")[1].strip())
                            continue  # Ignorar líneas con fechas no válidas
                        if fecha_inicio <= fecha_registro <= fecha_actual:
                            next_line = next(file, None)  # Leer la siguiente línea
                            while next_line:
                                if "Tipo de Transaccion: Gasto" in next_line:
                                    monto_line = next(file, None)  # Leer la línea del monto
                                    if monto_line and monto_line.startswith("Monto:"):
                                        try:
                                            monto = float(monto_line.split(":")[1].strip())
                                            total_gastos += monto
                                        except (IndexError, ValueError):
                                            print("Error al parsear el monto:", monto_line.strip())
                                            next_line = next(file, None)  # Leer la siguiente línea
                                            continue
                                next_line = next(file, None)

        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo de registros")
            return

        # Construir el mensaje del correo
        mensaje = f"Total de gastos para el período {tipo_reporte} hasta {fecha_actual}: ${total_gastos}"

        # Configurar cuentas
        remitente = "akilesrosas08@gmail.com"  # Correo de la cuenta que envía el mail
        destinatario = "lacrewtaqueria@gmail.com"  # Correo al que mandar el mail

        # Configurar mensaje
        mensaje_correo = MIMEText(mensaje)
        mensaje_correo["From"] = remitente
        mensaje_correo["To"] = destinatario
        mensaje_correo["Subject"] = f"Reporte de Gastos {tipo_reporte}"  # Asunto del mail

        # Conexión
        servidor = SMTP("smtp.gmail.com", 587)
        servidor.ehlo()
        servidor.starttls()

        # Inicio de sesión
        servidor.login(remitente, "uhygwpzinonrcycs")

        # Enviar correo
        servidor.sendmail(remitente, destinatario, mensaje_correo.as_string())

        # Terminar conexión
        servidor.quit()

        # Mostrar mensaje de confirmación
        messagebox.showinfo("Correo Enviado", f"El reporte de gastos {tipo_reporte} ha sido enviado por correo electrónico.")

def main():
    root = tk.Tk()
    app = RegistroGastosIngresosApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
