import json
import os
from datetime import datetime
from clases import Alumno, Profesor, Factura, Permiso, Anticipo

alumnos_db = []
profesores_db = []
permisos_db = []

def inicializar_datos_defecto():
    if not permisos_db:
        permisos_db.append(Permiso("B", 200.0, 10, 30.0, 50.0, 150.0))
    if not profesores_db:
        profesores_db.append(Profesor("NainDev", "Mendoza", "Vallejo", "1234-BBC", "Turismo", "01-01-2026"))

def guardar_datos():
    data = {
        "alumnos": [obj.__dict__ for obj in alumnos_db],
        "profesores": [obj.__dict__ for obj in profesores_db],
        "permisos": [obj.__dict__ for obj in permisos_db]
    }
    try:
        with open("datos_autoescuela.json", "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("\n>> DATOS GUARDADOS CORRECTAMENTE.")
    except Exception as e:
        print(f"Error al guardar: {e}")

def cargar_datos():
    global alumnos_db, profesores_db, permisos_db
    if not os.path.exists("datos_autoescuela.json"):
        inicializar_datos_defecto()
        return

    try:
        with open("datos_autoescuela.json", "r") as archivo:
            data = json.load(archivo)
            alumnos_db = [Alumno(**item) for item in data.get("alumnos", [])]
            profesores_db = [Profesor(**item) for item in data.get("profesores", [])]
            permisos_db = [Permiso(**item) for item in data.get("permisos", [])]
            print(f"\nCARGADO: {len(alumnos_db)} Alumnos, {len(profesores_db)} Profesores.")
    except Exception as e:
        print(f"Error al cargar: {e}")
        inicializar_datos_defecto()

def input_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto: return texto
        print("ERROR: El campo no puede estar vacío.")

def input_entero(mensaje):
    while True:
        try: return int(input(mensaje))
        except ValueError: print("ERROR: Por favor, introduce un número entero válido.")

def input_flotante(mensaje):
    while True:
        try:
            val = float(input(mensaje))
            if val < 0:
                print("ERROR: No puede ser negativo.")
                continue
            return val
        except ValueError: print("ERROR: Introduce un importe válido (ej. 50.5).")

def input_fecha(mensaje):
    while True:
        fecha_str = input(mensaje).strip()
        try:
            datetime.strptime(fecha_str, "%d-%m-%Y")
            return fecha_str
        except ValueError: print("ERROR: Formato incorrecto. Usa DD-MM-AAAA.")

def buscar_alumno(dni):
    for alumno in alumnos_db:
        if alumno.dni.strip().upper() == dni.strip().upper():
            return alumno
    return None

def buscar_permiso(tipo):
    for p in permisos_db:
        if p.tipo_permiso.upper() == tipo.upper():
            return p
    return permisos_db[0] if permisos_db else None

def menu():
    cargar_datos()
    
    while True:
        print("\n")
        print("GESTIÓN AUTOESCUELA NainDev")
        print("")
        print("1. Registrar Alumno")
        print("2. Ver lista de Alumnos")
        print("3. Añadir Clases a Alumno")
        print("4. Registrar Examen")
        print("5. Registrar Anticipo")
        print("6. Generar Factura")
        print("7. Ver Profesores y Permisos")
        print("8. Guardar y Salir")
        
        opcion = input("\nSeleccione opción: ")

        if opcion == "1":
            print("\nNUEVO ALUMNO")
            dni = input_texto("DNI: ")
            if buscar_alumno(dni):
                print("¡Ese DNI ya existe!")
                continue
            
            nuevo = Alumno(
                num_registro="2025/Auto",
                nombre=input_texto("Nombre: "),
                primer_apellido=input_texto("Primer Apellido: "),
                segundo_apellido=input_texto("Segundo Apellido: "),
                dni=dni,
                fecha_nacimiento=input_fecha("Fecha Nacimiento (DD-MM-AAAA): "),
                fecha_registro="Hoy",
                permiso_opta=input_texto("Permiso (B): ").upper(),
                domicilio=input_texto("Domicilio: "),
                municipio=input_texto("Municipio: "),
                provincia=input_texto("Provincia: "),
                telefono1=input_texto("Teléfono: "),
                telefono2="",
                correo=input_texto("Correo: "),
                num_clases=0,
                profesor=input_texto("Profesor asignado: ")
            )
            alumnos_db.append(nuevo)
            print("Alumno registrado.")

        elif opcion == "2":
            print("\nLISTADO")
            if not alumnos_db: print("No hay alumnos.")
            for alum in alumnos_db:
                print(alum.mostrar_info_completa())
                print("-" * 20)

        elif opcion == "3":
            alum = buscar_alumno(input_texto("DNI del alumno: "))
            if alum:
                alum.agregar_clases(input_entero("Nº Clases a añadir: "))
                print(f"Total clases: {alum.num_clases}")
            else: print("Alumno no encontrado.")

        elif opcion == "4":
            alum = buscar_alumno(input_texto("DNI del alumno: "))
            if alum:
                tipo = input_texto("Tipo (T/C): ").upper()
                if tipo in ["T", "C"]:
                    fecha = input_fecha("Fecha (DD-MM-AAAA): ")
                    if tipo == "T": alum.agregar_examen_teorico(fecha)
                    else: alum.agregar_examen_circulacion(fecha)
                    print(">> Examen registrado.")
                else: print("Tipo inválido.")
            else: print("Alumno no encontrado.")

        elif opcion == "5":
            alum = buscar_alumno(input_texto("DNI del alumno: "))
            if alum:
                alum.total_anticipos += input_flotante("Cantidad (€): ")
                print(f"Total pagado: {alum.total_anticipos}€")
            else: print("Alumno no encontrado.")

        elif opcion == "6":
            dni = input_texto("DNI del alumno: ")
            alum = buscar_alumno(dni)
            if alum:

                permiso_data = buscar_permiso(alum.permiso_opta)
                total_examenes = len(alum.examenes_teoricos) + len(alum.examenes_circulacion)

                fact = Factura(
                    dni_alumno=alum.dni,
                    precio_matricula=permiso_data.precio_matricula,
                    num_clases_incluidas=permiso_data.clases_incluidas,
                    num_clases_dadas=alum.num_clases,
                    precio_clase=permiso_data.precio_por_clase,
                    num_examenes=total_examenes,
                    precio_examen=permiso_data.precio_examen,
                    num_renovaciones=0,
                    precio_renovacion=permiso_data.precio_renovacion,
                    anticipos=alum.total_anticipos
                )
                
                clases_extra = max(0, alum.num_clases - permiso_data.clases_incluidas)
                
                texto_factura = (
                    f" \n"
                    f"         FACTURA AUTOESCUELA UAX        \n"
                    f" \n"
                    f"Alumno: {alum.nombre} {alum.primer_apellido}\n"
                    f"DNI:    {alum.dni}\n"
                    f"Fecha:  {datetime.now().strftime('%d-%m-%Y')}\n"
                    f" \n"
                    f"CONCEPTOS:\n"
                    f"- Matrícula: {fact.precio_matricula:.2f}€\n"
                    f"- Clases Extra ({clases_extra}): {clases_extra * fact.precio_clase:.2f}€\n"
                    f"- Exámenes ({fact.num_examenes}): {fact.num_examenes * fact.precio_examen:.2f}€\n"
                    f"\n"
                    f"Subtotal:  {fact.calcular_total():.2f}€\n"
                    f"IVA (21%): {fact.calcular_iva():.2f}€\n"
                    f"TOTAL: {fact.calcular_total_con_iva():.2f}€\n"
                    f"Anticipos: {fact.anticipos:.2f}€\n"
                    f"\n"
                    f"TOTAL A PAGAR:                 {fact.calcular_saldo_pendiente():.2f}€\n"
                    f""
                )

                print(texto_factura)

                try:
                    nombre_archivo = f"Factura_{dni}.txt"
                    with open(nombre_archivo, "w", encoding="utf-8") as f:
                        f.write(texto_factura)
                    print(f"\nARCHIVO GUARDADO: {nombre_archivo}")
                except Exception as e:
                    print(f"Error al crear archivo: {e}")

            else: print("Alumno no encontrado.")
        
        elif opcion == "7":
            print("\nINFO EXTRA")
            for p in profesores_db: print(p.mostrar_info_profesor())
            for perm in permisos_db: print(perm.mostrar_info_permiso())

        elif opcion == "8":
            guardar_datos()
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()