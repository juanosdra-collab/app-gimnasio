import flet as ft
import requests

FIREBASE_URL = "https://listacompracasa-default-rtdb.firebaseio.com/gimnasio"

def main(page: ft.Page):
    page.title = "Rutina de Gimnasio"
    page.padding = 15
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

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

    txt_ejercicio = ft.TextField(label="Ejercicio (ej: Banco Inclinado)", expand=True)
    
    dropdown_serie = ft.Dropdown(
        value="Serie 1",
        width=110,
        options=[
            ft.dropdown.Option("Calentamiento"),
            ft.dropdown.Option("Serie 1"),
            ft.dropdown.Option("Serie 2"),
            ft.dropdown.Option("Serie 3"),
            ft.dropdown.Option("Serie 4"),
            ft.dropdown.Option("Serie 5"),
        ]
    )

    txt_reps = ft.TextField(label="Reps", width=80, keyboard_type=ft.KeyboardType.NUMBER)
    txt_peso = ft.TextField(label="Peso (kg)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    txt_notas = ft.TextField(label="Notas / Detalles (ej: punto 2, al fallo)", expand=True)

    lista_ejercicios = ft.Column()

    def cargar_datos(e=None):
        lista_ejercicios.controls.clear()
        usuario = dropdown_usuario.value
        dia = dropdown_dia.value

        try:
            res = requests.get(f"{FIREBASE_URL}/{usuario}/{dia}.json")
            datos = res.json()

            if datos:
                for key, val in datos.items():
                    ejercicio = val.get("ejercicio", "")
                    tipo_serie = val.get("serie", "Serie")
                    reps = val.get("reps", "")
                    peso = val.get("peso", "")
                    notas = val.get("notas", "")

                    texto_item = f"• {ejercicio} | {tipo_serie}: {peso} kg x {reps} reps"
                    if notas:
                        texto_item += f" ({notas})"

                    def borrar_item(e, item_id=key):
                        requests.delete(f"{FIREBASE_URL}/{usuario}/{dia}/{item_id}.json")
                        cargar_datos()

                    lista_ejercicios.controls.append(
                        ft.Card(
                            content=ft.Container(
                                padding=10,
                                content=ft.Row([
                                    ft.Text(texto_item, expand=True, size=15),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color="red",
                                        on_click=borrar_item
                                    )
                                ])
                            )
                        )
                    )
            else:
                lista_ejercicios.controls.append(
                    ft.Text("No hay registros guardados para este día.", italic=True, color="gray")
                )
        except Exception as ex:
            lista_ejercicios.controls.append(
                ft.Text(f"Error al cargar datos: {ex}", color="red")
            )
        
        page.update()

    def agregar_ejercicio(e):
        if not txt_ejercicio.value or not txt_reps.value or not txt_peso.value:
            page.snack_bar = ft.SnackBar(ft.Text("Rellena Ejercicio, Reps y Peso"))
            page.snack_bar.open = True
            page.update()
            return

        usuario = dropdown_usuario.value
        dia = dropdown_dia.value

        nuevo_registro = {
            "ejercicio": txt_ejercicio.value.strip(),
            "serie": dropdown_serie.value,
            "reps": txt_reps.value.strip(),
            "peso": txt_peso.value.strip(),
            "notas": txt_notas.value.strip()
        }

        try:
            requests.post(f"{FIREBASE_URL}/{usuario}/{dia}.json", json=nuevo_registro)
            
            # Limpiar campos de entrada (mantenemos el nombre del ejercicio para facilitar meter la siguiente serie)
            txt_reps.value = ""
            txt_peso.value = ""
            txt_notas.value = ""
            
            # Avanzar automáticamente el desplegable a la siguiente serie
            if dropdown_serie.value == "Serie 1":
                dropdown_serie.value = "Serie 2"
            elif dropdown_serie.value == "Serie 2":
                dropdown_serie.value = "Serie 3"
            elif dropdown_serie.value == "Serie 3":
                dropdown_serie.value = "Serie 4"

            cargar_datos()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
            page.snack_bar.open = True
            page.update()

    dropdown_usuario.on_change = cargar_datos
    dropdown_dia.on_change = cargar_datos

    btn_guardar = ft.FloatingActionButton(
        icon=ft.icons.ADD,
        on_click=agregar_ejercicio,
        bgcolor="green"
    )

    page.add(
        ft.Row([ft.Text("💪 Registro Gym", size=22, weight="bold"), dropdown_usuario, ft.IconButton(ft.icons.REFRESH, on_click=cargar_datos)]),
        ft.Divider(),
        ft.Row([dropdown_dia, txt_ejercicio]),
        ft.Row([dropdown_serie, txt_reps, txt_peso]),
        ft.Row([txt_notas, btn_guardar]),
        ft.Divider(),
        ft.Text("Progreso registrado:", size=16, weight="bold"),
        lista_ejercicios
    )

    cargar_datos()

ft.app(target=main)