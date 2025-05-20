// ============================
// index.js
// ============================
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const loader = document.getElementById('loader');
    const submitButton = form.querySelector('button[type="submit"]');
  
    form.addEventListener('submit', () => {
      const pd = document.getElementById('problem_description').value.trim();
      const sc = document.getElementById('source_code').value.trim();
      if (!pd || !sc) return;
      loader && (loader.style.display = 'flex');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Đang xử lý...';
      }
    });
  
    window.addEventListener('pageshow', () => {
      if (loader && loader.style.display === 'flex') {
        loader.style.display = 'none';
      }
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = 'Phân tích Mã nguồn';
      }
    });
  });
  