class Registro:
    def __init__(self, num_registro, nombre, primer_apellido, segundo_apellido, dni, fecha_nacimiento, fecha_registro, permiso_opta):
        self.num_registro = num_registro
        self.nombre = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.dni = dni
        self.fecha_nacimiento = fecha_nacimiento
        self.fecha_registro = fecha_registro
        self.permiso_opta = permiso_opta

    def mostrar_datos(self):
        return f"{self.nombre} {self.primer_apellido} | DNI: {self.dni} | Registro: {self.num_registro}"

class Alumno(Registro):
    def __init__(self, num_registro, nombre, primer_apellido, segundo_apellido, dni, fecha_nacimiento, fecha_registro, permiso_opta,
                 domicilio, municipio, provincia, telefono1, telefono2, correo, num_clases, profesor, 
                 total_anticipos=0.0, examenes_teoricos=None, examenes_circulacion=None):
        
        super().__init__(num_registro, nombre, primer_apellido, segundo_apellido, dni, fecha_nacimiento, fecha_registro, permiso_opta)
        
        self.domicilio = domicilio
        self.municipio = municipio
        self.provincia = provincia
        self.telefono1 = telefono1
        self.telefono2 = telefono2
        self.correo = correo
        self.num_clases = num_clases
        self.profesor = profesor 
        
        self.examenes_teoricos = examenes_teoricos if examenes_teoricos is not None else []
        self.examenes_circulacion = examenes_circulacion if examenes_circulacion is not None else []
        self.total_anticipos = total_anticipos

    def agregar_examen_teorico(self, fecha_hora):
        self.examenes_teoricos.append(fecha_hora)

    def agregar_examen_circulacion(self, fecha_hora):
        self.examenes_circulacion.append(fecha_hora)

    def agregar_clases(self, num):
        self.num_clases += num

    def mostrar_info_completa(self):
        base = super().mostrar_datos()
        return (f"{base}\n"
                f"Clases: {self.num_clases} | Profesor: {self.profesor}\n"
                f"Exámenes: {len(self.examenes_teoricos)} Teóricos | {len(self.examenes_circulacion)} Circulación\n"
                f"Anticipos pagados: {self.total_anticipos}€\n"
                f"Contacto: {self.telefono1} ({self.municipio})")

class Profesor:
    def __init__(self, nombre, primer_apellido, segundo_apellido, vehiculo, tipo_vehiculo, itv):
        self.nombre = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.vehiculo = vehiculo
        self.tipo_vehiculo = tipo_vehiculo
        self.itv = itv
        self.gastos_combustible = {}

    def registrar_gasto_combustible(self, fecha, costo):
        self.gastos_combustible[fecha] = costo

    def mostrar_gastos_combustible(self):
        if not self.gastos_combustible:
            return "No hay gastos registrados."
        info = "HISTORIAL COMBUSTIBLE\n"
        total = 0.0
        for fecha, costo in self.gastos_combustible.items():
            info += f"Fecha: {fecha} | Costo: {costo}€\n"
            total += costo
        info += f"TOTAL GASTADO: {total:.2f}€"
        return info

    def mostrar_info_profesor(self):
        return (f"PROFESOR: {self.nombre} {self.primer_apellido} {self.segundo_apellido}\n"
                f"Vehículo: {self.vehiculo} ({self.tipo_vehiculo})\n"
                f"ITV Caducidad: {self.itv}")

class Clase:
    def __init__(self, dni_alumno, dni_profesor, matricula_vehiculo, fecha_hora):
        self.alumno = dni_alumno
        self.profesor = dni_profesor
        self.matricula_vehiculo = matricula_vehiculo
        self.fecha_hora = fecha_hora

    def mostrar_info_clase(self):
        return f"Clase el {self.fecha_hora} | Alumno: {self.alumno} | Prof: {self.profesor}"

class Permiso:
    def __init__(self, tipo_permiso, precio_matricula, clases_incluidas, precio_por_clase, precio_examen, precio_renovacion):
        self.tipo_permiso = tipo_permiso
        self.precio_matricula = precio_matricula
        self.clases_incluidas = clases_incluidas
        self.precio_por_clase = precio_por_clase
        self.precio_examen = precio_examen
        self.precio_renovacion = precio_renovacion

    def mostrar_info_permiso(self):
        return (f"PERMISO TIPO {self.tipo_permiso}\n"
                f"Matrícula: {self.precio_matricula}€ (Incluye {self.clases_incluidas} clases)\n"
                f"Precio Clase Extra: {self.precio_por_clase}€\n"
                f"Precio Examen: {self.precio_examen}€ | Renovación: {self.precio_renovacion}€")

class Factura:
    def __init__(self, dni_alumno, precio_matricula, num_clases_incluidas, num_clases_dadas, precio_clase, num_examenes, precio_examen, num_renovaciones, precio_renovacion, anticipos):
        self.alumno = dni_alumno
        self.precio_matricula = precio_matricula
        self.num_clases_incluidas = num_clases_incluidas
        self.num_clases_dadas = num_clases_dadas
        self.precio_clase = precio_clase
        self.num_examenes = num_examenes
        self.precio_examen = precio_examen
        self.num_renovaciones = num_renovaciones
        self.precio_renovacion = precio_renovacion
        self.anticipos = anticipos

    def calcular_total(self):
        clases_extra = max(0, self.num_clases_dadas - self.num_clases_incluidas)
        subtotal = self.precio_matricula + \
                   (clases_extra * self.precio_clase) + \
                   (self.num_examenes * self.precio_examen) + \
                   (self.num_renovaciones * self.precio_renovacion)
        return subtotal

    def calcular_iva(self):
        return self.calcular_total() * 0.21

    def calcular_total_con_iva(self):
        return self.calcular_total() + self.calcular_iva()

    def calcular_saldo_pendiente(self):
        return self.calcular_total_con_iva() - self.anticipos

    def generar_factura(self):
        clases_extra = max(0, self.num_clases_dadas - self.num_clases_incluidas)
        info = (f"\nFACTURA DETALLADA ({self.alumno})\n"
                f"Matrícula: {self.precio_matricula:.2f}€\n"
                f"Clases ({self.num_clases_dadas} totales - {self.num_clases_incluidas} incluidas): {clases_extra} extra x {self.precio_clase}€\n"
                f"Exámenes: {self.num_examenes} x {self.precio_examen}€\n"
                f"Renovaciones: {self.num_renovaciones} x {self.precio_renovacion}€\n"
                f"\n"
                f"Subtotal: {self.calcular_total():.2f}€\n"
                f"IVA (21%): {self.calcular_iva():.2f}€\n"
                f"TOTAL: {self.calcular_total_con_iva():.2f}€\n"
                f"Anticipos: -{self.anticipos:.2f}€\n"
                f"A PAGAR: {self.calcular_saldo_pendiente():.2f}€")
        print(info)

class Anticipo:
    def __init__(self, alumno, fecha, concepto, cantidad):
        self.alumno = alumno
        self.fecha = fecha
        self.concepto = concepto
        self.cantidad = cantidad

    def mostrar_info_anticipo(self):
        return (f"ANTICIPO ({self.fecha})\n"
                f"Alumno: {self.alumno}\n"
                f"Concepto: {self.concepto} | Importe: {self.cantidad:.2f}€")