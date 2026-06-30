import os
import tempfile
import unittest
from unittest.mock import patch

import funciones
from clases import PDF


class ChecklistParsingTests(unittest.TestCase):
    def test_parse_checklist_items_with_pipe_separator(self):
        items = funciones.parsear_checklist("Revisar filtros|Limpiar equipo|Verificar cableado")

        self.assertEqual(
            items,
            [
                {"accion": "Revisar filtros", "realizado": False},
                {"accion": "Limpiar equipo", "realizado": False},
                {"accion": "Verificar cableado", "realizado": False},
            ],
        )

    def test_sanitize_checkmark_for_pdf(self):
        pdf = PDF()

        self.assertEqual(pdf._texto_seguro("✔ Hecho"), "[X] Hecho")
        self.assertEqual(pdf._texto_seguro("☐ Pendiente"), "[ ] Pendiente")

    def test_checklist_section_is_attached_to_previous_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "arch", "planilla"), exist_ok=True)
            with open(os.path.join(tmpdir, "arch", "planilla", "TEST.txt"), "w", encoding="utf-8") as fh:
                fh.write("[INSPECCIÓN VISUAL Y FUNCIONAL]\n")
                fh.write("ENCABEZADOS: Ítem | Evaluación\n")
                fh.write("Chasis | OK\n")
                fh.write("[CHECKLIST]\n")
                fh.write("CHECKLIST: Revisar filtros|Limpiar equipo\n")

            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with patch("questionary.select", return_value=type("Resp", (), {"ask": lambda self: "n"})()):
                    secciones = funciones.cargar_planilla("TEST")
            finally:
                os.chdir(old_cwd)

        self.assertIn("INSPECCIÓN VISUAL Y FUNCIONAL", secciones)
        self.assertNotIn("CHECKLIST", secciones)
        self.assertEqual(len(secciones["INSPECCIÓN VISUAL Y FUNCIONAL"]["checklist"]), 2)


if __name__ == "__main__":
    unittest.main()
