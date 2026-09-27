import flet as ft
import requests
import os

# Base de datos en Firebase (nodo separado para el gimnasio)
FIREBASE_URL = "https://listacompracasa-default-rtdb.firebaseio.com/gimnasio"

def main(page: ft.Page):
    page.title = "Rutina de Gimnasio"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # Campos de entrada
    dropdown_usuario = ft.Dropdown(
        value="Juan",
        width=120,
        options=[
            ft.dropdown.Option("Juan"),
            ft.dropdown.Option("Gema"),
            ft.dropdown.Option("Aarón"),
            ft.dropdown.Option("Dylan"),
        ]
    )

    dropdown_dia = ft.Dropdown(
        value="Lunes",
        width=130,
        options=[
            ft.dropdown.Option("Lunes"),
            ft.dropdown.Option("Martes"),
            ft.dropdown.Option("Miércoles"),
            ft.dropdown.Option("Jueves"),
            ft.dropdown.Option("Viernes"),
            ft.dropdown.Option("Sábado"),
            ft.dropdown.Option("Domingo"),
        ]
    )

    input_ejercicio = ft.TextField(hint_text="Ejercicio (ej: Press de Banca)", expand=True)
    input_series = ft.TextField(hint_text="Series (4)", width=90)
    input_reps = ft.TextField(hint_text="Reps (10)", width=90)
    input_peso = ft.TextField(hint_text="Peso kg", width=90)

    columna_rutina = ft.Column(scroll=ft.ScrollMode.AUTO)

    def cargar_datos():
        columna_rutina.controls.clear()
        try:
            res = requests.get(f"{FIREBASE_URL}.json")
            datos = res.json() if res.status_code == 200 else {}
        except Exception:
            datos = {}

        hay_datos = False
        if datos and isinstance(datos, dict):
            for clave, item in datos.items():
                if isinstance(item, dict):
                    hay_datos = True
                    ejercicio = item.get("ejercicio", "")
                    dia = item.get("dia", "")
                    series = item.get("series", "")
                    reps = item.get("reps", "")
                    peso = item.get("peso", "")
                    usuario = item.get("usuario", "Juan")

                    def al_borrar(e, key=clave):
                        requests.delete(f"{FIREBASE_URL}/{key}.json")
                        cargar_datos()

                    tarjeta = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"🏋️ {ejercicio}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"📅 {dia} | {series} series x {reps} reps | {peso} kg", color="blueGrey"),
                                ft.Text(f"👤 {usuario}", size=12, color="grey"),
                            ], expand=True),
                            ft.IconButton(
                                icon="delete_outline",
                                icon_color="red",
                                tooltip="Eliminar ejercicio",
                                on_click=al_borrar
                            )
                        ]),
                        padding=10,
                        bgcolor="grey100",
                        border_radius=8
                    )
                    columna_rutina.controls.append(tarjeta)

        if not hay_datos:
            columna_rutina.controls.append(
                ft.Text("No hay ejercicios registrados. ¡Añade el primero!", color="grey", italic=True)
            )
        page.update()

    def agregar_ejercicio(e):
        if input_ejercicio.value.strip():
            nuevo = {
                "usuario": dropdown_usuario.value,
                "dia": dropdown_dia.value,
                "ejercicio": input_ejercicio.value.strip().capitalize(),
                "series": input_series.value.strip() or "-",
                "reps": input_reps.value.strip() or "-",
                "peso": input_peso.value.strip() or "-",
            }
            requests.post(f"{FIREBASE_URL}.json", json=nuevo)
            input_ejercicio.value = ""
            input_series.value = ""
            input_reps.value = ""
            input_peso.value = ""
            cargar_datos()

    btn_refrescar = ft.IconButton(
        icon="refresh",
        tooltip="Actualizar rutina",
        on_click=lambda e: cargar_datos()
    )

    page.add(
        ft.Row([
            ft.Text("💪 Mi Rutina de Gimnasio", size=20, weight=ft.FontWeight.BOLD, expand=True),
            dropdown_usuario,
            btn_refrescar
        ]),
        ft.Divider(),
        ft.Row([
            dropdown_dia,
            input_ejercicio,
        ]),
        ft.Row([
            input_series,
            input_reps,
            input_peso,
            ft.IconButton(
                icon="add_circle",
                icon_size=36,
                icon_color="green",
                on_click=agregar_ejercicio
            )
        ]),
        ft.Divider(),
        columna_rutina
    )

    cargar_datos()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)