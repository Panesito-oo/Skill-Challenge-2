import json
import os
from datetime import datetime

RUTA_DATOS = "datos.json"

GENEROS_VALIDOS = [
    "Clásico",
    "Distopía",
    "Fantasía",
    "Terror",
    "Realismo Mágico",
    "Drama",
    "Infantil",
]

ANIO_MINIMO = 1000
ANIO_MAXIMO = datetime.now().year


def cargar_datos(ruta: str = RUTA_DATOS) -> list[dict]:
    if not os.path.exists(ruta):
        return []

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError) as error:
        print(f"No se pudo leer '{ruta}' ({error}). Se iniciará un catálogo vacío.")
        return []


def guardar_datos(libros: list[dict], ruta: str = RUTA_DATOS) -> None:
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, indent=4, ensure_ascii=False)



def validar_texto_obligatorio(valor: str, nombre_campo: str) -> str:
    valor = valor.strip()
    if not valor:
        raise ValueError(f"El campo '{nombre_campo}' no puede estar vacío.")
    return valor


def validar_anio(valor: str) -> int:
    try:
        anio = int(valor)
    except ValueError:
        raise ValueError("El año debe ser un número entero.")

    if not (ANIO_MINIMO <= anio <= ANIO_MAXIMO):
        raise ValueError(f"El año debe estar entre {ANIO_MINIMO} y {ANIO_MAXIMO}.")
    return anio


def validar_genero(valor: str) -> str:
    valor = valor.strip().title()
    if valor not in GENEROS_VALIDOS:
        opciones = ", ".join(GENEROS_VALIDOS)
        raise ValueError(f"Género inválido. Opciones válidas: {opciones}")
    return valor


def validar_booleano(valor: str) -> bool:
    valor = valor.strip().lower()
    if valor in ("si"):
        return True
    if valor in ("no"):
        return False
    raise ValueError("Respuesta inválida. Usa 'si' o 'no'.")




def generar_nuevo_id(libros: list[dict]) -> int:
    if not libros:
        return 1
    return max(libro["id"] for libro in libros) + 1


def crear_libro(
    libros: list[dict],
    titulo: str,
    autor: str,
    anio_publicacion: int,
    genero: str,
    disponible: bool,
) -> dict:
    nuevo_libro = {
        "id": generar_nuevo_id(libros),
        "titulo": titulo,
        "autor": autor,
        "anio_publicacion": anio_publicacion,
        "genero": genero,
        "disponible": disponible,
    }
    libros.append(nuevo_libro)
    return nuevo_libro


def buscar_por_id(libros: list[dict], id_libro: int) -> dict | None:
    for libro in libros:
        if libro["id"] == id_libro:
            return libro
    return None


def buscar_por_titulo(libros: list[dict], texto: str) -> list[dict]:
    texto = texto.strip().lower()
    return [libro for libro in libros if texto in libro["titulo"].lower()]


def actualizar_libro(libros: list[dict], id_libro: int, **campos_nuevos) -> bool:
    libro = buscar_por_id(libros, id_libro)
    if libro is None:
        return False
    libro.update(campos_nuevos)
    return True


def eliminar_libro(libros: list[dict], id_libro: int) -> bool:
    libro = buscar_por_id(libros, id_libro)
    if libro is None:
        return False
    libros.remove(libro)
    return True

def pedir_dato(mensaje: str, funcion_validadora):
    while True:
        valor = input(mensaje)
        try:
            return funcion_validadora(valor)
        except ValueError as error:
            print(f"Error: {error}")



def mostrar_libro(libro: dict) -> None:
    disponibilidad = "Disponible" if libro["disponible"] else "No disponible"
    print(
        f"[{libro['id']:>3}] {libro['titulo']} — {libro['autor']} "
        f"({libro['anio_publicacion']}) | {libro['genero']} | {disponibilidad}"
    )


def listar_libros(libros: list[dict]) -> None:
    if not libros:
        print("El catálogo está vacío.")
        return
    for libro in libros:
        mostrar_libro(libro)


def menu_crear(libros: list[dict]) -> None:
    print("\n-----Nuevo libro-----")
    titulo = pedir_dato("Título: ", lambda v: validar_texto_obligatorio(v, "título"))
    autor = pedir_dato("Autor: ", lambda v: validar_texto_obligatorio(v, "autor"))
    anio = pedir_dato(f"Año de publicación ({ANIO_MINIMO}-{ANIO_MAXIMO}): ", validar_anio)
    genero = pedir_dato(f"Género ({', '.join(GENEROS_VALIDOS)}): ", validar_genero)
    disponible = pedir_dato("¿Disponible? (si/no): ", validar_booleano)

    libro = crear_libro(libros, titulo, autor, anio, genero, disponible)
    guardar_datos(libros)
    print(f"Libro creado con id {libro['id']}.")


def menu_buscar(libros: list[dict]) -> None:
    texto = input("Buscar por título: ")
    resultados = buscar_por_titulo(libros, texto)
    if not resultados:
        print("No se encontraron coincidencias.")
        return
    for libro in resultados:
        mostrar_libro(libro)


def menu_actualizar(libros: list[dict]) -> None:
    id_libro = pedir_dato("Id del libro a actualizar: ", lambda v: int(v))
    libro = buscar_por_id(libros, id_libro)
    if libro is None:
        print("No existe un libro con ese id.")
        return

    print("Deja un campo vacío para conservar el valor actual.")
    mostrar_libro(libro)

    campos_nuevos = {}

    titulo = input(f"Título [{libro['titulo']}]: ")
    if titulo.strip():
        campos_nuevos["titulo"] = validar_texto_obligatorio(titulo, "título")

    autor = input(f"Autor [{libro['autor']}]: ")
    if autor.strip():
        campos_nuevos["autor"] = validar_texto_obligatorio(autor, "autor")

    anio = input(f"Año [{libro['anio_publicacion']}]: ")
    if anio.strip():
        try:
            campos_nuevos["anio_publicacion"] = validar_anio(anio)
        except ValueError as error:
            print(f"Error: {error}. No se actualizó el año.")

    genero = input(f"Género [{libro['genero']}]: ")
    if genero.strip():
        try:
            campos_nuevos["genero"] = validar_genero(genero)
        except ValueError as error:
            print(f"Error: {error}. No se actualizó el género.")

    disponible = input(f"¿Disponible? [{'si' if libro['disponible'] else 'no'}]: ")
    if disponible.strip():
        try:
            campos_nuevos["disponible"] = validar_booleano(disponible)
        except ValueError as error:
            print(f"Error: {error}. No se actualizó la disponibilidad.")

    actualizar_libro(libros, id_libro, **campos_nuevos)
    guardar_datos(libros)
    print("Libro actualizado.")


def menu_eliminar(libros: list[dict]) -> None:
    id_libro = pedir_dato("Id del libro a eliminar: ", lambda v: int(v))
    libro = buscar_por_id(libros, id_libro)
    if libro is None:
        print("No existe un libro con ese id.")
        return

    mostrar_libro(libro)
    confirmacion = pedir_dato("¿Confirmas que deseas eliminarlo? (si/no): ", validar_booleano)
    if confirmacion:
        eliminar_libro(libros, id_libro)
        guardar_datos(libros)
        print("Libro eliminado.")
    else:
        print("Operación cancelada.")


def mostrar_menu() -> None:
    print("\n-----CATÁLOGO DE LIBROS-----")
    print("1. Listar libros")
    print("2. Buscar por título")
    print("3. Crear libro")
    print("4. Actualizar libro")
    print("5. Eliminar libro")
    print("6. Salir")


def main() -> None:
    libros = cargar_datos()
    print(f"Catálogo cargado: {len(libros)} libro(s).")

    opciones = {
        "1": listar_libros,
        "2": menu_buscar,
        "3": menu_crear,
        "4": menu_actualizar,
        "5": menu_eliminar,
    }

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "6":
            print("Has salido de la ejecución.")
            break

        accion = opciones.get(opcion)
        if accion is None:
            print("Opción no válida.")
            continue

        accion(libros)


if __name__ == "__main__":
    main()
