// bci_ui.js — Funciones de interfaz del BCI
 
// Inicialmente, desactivar el botón de detener
window.addEventListener('load', function() {
  document.getElementById('btn-stop').disabled = true;
});
 
function clearCellSelection() {
  var cells = document.querySelectorAll('.vital-cell');
  cells.forEach(cell => {
    cell.classList.remove('selected');
  });
}
 
function showMessage(text, type) {
  var feedback = document.getElementById('selection-feedback');
  feedback.textContent = text;
  feedback.classList.toggle('error', type === 'error');
}
 
function updateSignalQuality(quality) {
  // Podría implementarse una barra de calidad visual
  // Por ahora, solo se log
  console.log('[Signal Quality]', quality);
}
 