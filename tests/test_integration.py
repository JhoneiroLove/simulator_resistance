import pytest # type: ignore
from src.gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

@pytest.fixture
def app():
    return QApplication([])

def test_simulation_flow(app, mocker):
    window = MainWindow()

    # Mockear la base de datos
    mock_session = mocker.patch("src.data.database.get_session")
    mock_genes = [mocker.Mock(id=1, nombre="blaVIM", peso_resistencia=2.5)]
    mock_session.return_value.query.return_value.all.return_value = mock_genes

    # Simular selección de genes y antibiótico
    window.input_tab.antibiotico_combo.setCurrentIndex(0)
    for cb in window.input_tab.gene_checkboxes.values():
        cb.setChecked(True)

    # Ejecutar simulación
    window.input_tab.simular_btn.click()

    # Verificar resultados
    assert "Resistencia predicha" in window.status_bar.currentMessage()
