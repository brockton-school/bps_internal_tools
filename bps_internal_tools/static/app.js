function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }

function setupTeacherSearch({inputId, listId, clearId, searchUrl, onPick}){
  const $i = document.getElementById(inputId);
  const $list = document.getElementById(listId);
  const $clear = document.getElementById(clearId);

  const render = (items)=>{
    $list.innerHTML = '';
    if (!items.length){ $list.style.display='none'; return; }
    items.forEach((u,idx)=>{
      const row = document.createElement('div');
      row.className = 'ac-item';
      row.role = 'option';
      row.tabIndex = 0;
      row.dataset.id = u.id;
      row.textContent = u.name;
      row.addEventListener('click', ()=> onPick(u));
      row.addEventListener('keydown', (e)=>{ if(e.key==='Enter' || e.key===' '){ e.preventDefault(); onPick(u); }});
      $list.appendChild(row);
    });
    $list.style.display = 'block';
    $i.setAttribute('aria-expanded','true');
  };

  const search = debounce(async (q)=>{
    if (q.trim().length < 2){ render([]); return; }
    try{
      const res = await fetch(`${searchUrl}?q=${encodeURIComponent(q)}`);
      if (!res.ok) throw new Error('HTTP '+res.status);
      const data = await res.json();
      render(data);
    }catch(err){
      console.error('Autocomplete error:', err);
      render([]);
    }
  }, 160);

  $i.addEventListener('input', (e)=> search(e.target.value));
  $i.addEventListener('focus', ()=> { if($list.children.length) $list.style.display='block'; });
  document.addEventListener('click', (e)=>{ if(!e.target.closest('.ac-wrap')){ $list.style.display='none'; $i.setAttribute('aria-expanded','false'); }});

  $clear.addEventListener('click', ()=>{
    $i.value = ''; $i.focus(); render([]);
    $clear.style.display='none';
  });
  $i.addEventListener('input', ()=> $clear.style.display = $i.value ? 'inline-flex' : 'none');
}
