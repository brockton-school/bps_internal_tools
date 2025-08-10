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

    // ---- Theme handling ----
  const THEME_KEY = 'theme';
  const body = document.body;

  // Apply saved theme on load
  const saved = localStorage.getItem(THEME_KEY);
  if(saved === 'light'){ body.setAttribute('data-theme','light'); }

  // Toggle button
  const toggle = document.getElementById('themeToggleBtn');
  if(toggle){
    toggle.addEventListener('click', ()=>{
      const isLight = body.getAttribute('data-theme') === 'light';
      if(isLight){
        body.removeAttribute('data-theme');
        localStorage.setItem(THEME_KEY, 'dark');
      }else{
        body.setAttribute('data-theme','light');
        localStorage.setItem(THEME_KEY, 'light');
      }
    });
  }
})();

// Role tools checkbox mutual exclusion for "*"
document.addEventListener('change', (e)=>{
  const el = e.target;
  if (el.matches('input[type=checkbox][name="tools[]"]')) {
    const form = el.closest('form');
    if (!form) return;
    const allBox = form.querySelector('input[name="tools[]"][value="*"]');
    const others = form.querySelectorAll('input[name="tools[]"]:not([value="*"])');
    if (el.value === '*') {
      if (el.checked) others.forEach(cb => cb.checked = false);
    } else if (el.checked && allBox) {
      allBox.checked = false;
    }
  }
});