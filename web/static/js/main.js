// Auto-dismiss alerts
document.querySelectorAll('.alert').forEach(a => setTimeout(() => a.style.opacity='0', 4000));

// Confirm dangerous actions
document.querySelectorAll('form').forEach(f => {
  const btn = f.querySelector('.btn-danger');
  if (btn && btn.textContent.includes('Chiudi') || btn && btn.textContent.includes('Termina')) {
    f.addEventListener('submit', e => {
      if (!confirm('Sei sicuro? Questa azione non può essere annullata.')) e.preventDefault();
    });
  }
});
