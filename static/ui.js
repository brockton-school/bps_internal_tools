(function(){
  const btn = document.getElementById('userMenuBtn');
  const menu = document.getElementById('userDropdown');
  if(!btn || !menu) return;

  const close = () => { menu.classList.remove('open'); btn.setAttribute('aria-expanded','false'); };
  const open  = () => { menu.classList.add('open'); btn.setAttribute('aria-expanded','true'); };

  btn.addEventListener('click', (e)=>{
    e.stopPropagation();
    if(menu.classList.contains('open')) close(); else open();
  });
  document.addEventListener('click', (e)=>{
    if(!menu.contains(e.target) && e.target !== btn) close();
  });
  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape') close();
  });
})();
