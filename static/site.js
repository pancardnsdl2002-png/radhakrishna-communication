document.addEventListener('DOMContentLoaded', () => {
  const main = document.getElementById('mainProductImage');
  const modal = document.getElementById('imageModal');
  const modalImage = document.getElementById('modalImage');
  if (!main) return;
  document.querySelectorAll('.thumbnail').forEach(button => {
    button.addEventListener('click', () => {
      main.src = button.dataset.image;
      document.querySelectorAll('.thumbnail').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
    });
  });
  main.addEventListener('mousemove', event => {
    const rect = main.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    main.style.transformOrigin = `${x}% ${y}%`;
  });
  main.addEventListener('click', () => {
    modalImage.src = main.src;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  });
  const close = () => { modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); document.body.classList.remove('modal-open'); };
  modal.querySelector('.modal-close').addEventListener('click', close);
  modal.addEventListener('click', event => { if (event.target === modal) close(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
});
