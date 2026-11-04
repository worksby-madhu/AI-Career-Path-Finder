/* Shared accessible autocomplete for inputs backed by datalist or nearby select options. */
(() => {
  const norm = s => (s || '').trim().toLocaleLowerCase();
  document.querySelectorAll('input[list]').forEach(input => {
    if (input.dataset.customAutocomplete === 'true') return;
    const listId = input.getAttribute('list');
    const source = document.getElementById(listId);
    if (!source) return;
    const values = [...source.querySelectorAll('option')].map(o => o.value || o.textContent.trim()).filter(Boolean);
    if (!values.length) return;
    input.dataset.customAutocomplete = 'true';
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    const wrap = document.createElement('div'); wrap.className = 'autocomplete-wrap';
    input.parentNode.insertBefore(wrap, input); wrap.appendChild(input);
    const menu = document.createElement('div'); menu.className = 'generic-suggestions'; menu.setAttribute('role','listbox'); menu.id = `suggestions-${Math.random().toString(36).slice(2,9)}`; wrap.appendChild(menu);
    input.setAttribute('aria-controls', menu.id);
    let active = -1, shown = [];
    const close = () => { menu.replaceChildren(); shown=[]; active=-1; input.setAttribute('aria-expanded','false'); input.removeAttribute('aria-activedescendant'); };
    const render = () => {
      const q = norm(input.value); close(); if (!q) return;
      shown = values.filter(v => norm(v).includes(q) && norm(v) !== q)
        .sort((a,b)=>(Number(norm(b).startsWith(q))-Number(norm(a).startsWith(q))) || a.localeCompare(b)).slice(0,5);
      shown.forEach((value,i)=>{
        const option=document.createElement('button'); option.type='button'; option.className='generic-suggestion'; option.setAttribute('role','option'); option.id=`${menu.id}-opt-${i}`; option.setAttribute('aria-selected','false');
        const at=norm(value).indexOf(q); option.append(document.createTextNode(value.slice(0,at)), Object.assign(document.createElement('mark'),{textContent:value.slice(at,at+q.length)}), document.createTextNode(value.slice(at+q.length)));
        option.addEventListener('mousedown',e=>{e.preventDefault();input.value=value;input.dispatchEvent(new Event('change',{bubbles:true}));input.dispatchEvent(new Event('input',{bubbles:true}));close();}); menu.appendChild(option);
      });
      input.setAttribute('aria-expanded',String(shown.length>0));
    };
    input.addEventListener('input',render);
    input.addEventListener('keydown',e=>{
      const opts=[...menu.querySelectorAll('[role=option]')];
      if(!opts.length) return;
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();active=(active+(e.key==='ArrowDown'?1:-1)+opts.length)%opts.length;opts.forEach((o,i)=>{o.classList.toggle('active',i===active);o.setAttribute('aria-selected',String(i===active));});input.setAttribute('aria-activedescendant',opts[active].id);opts[active].scrollIntoView({block:'nearest'});}
      else if(e.key==='Enter'&&active>=0){e.preventDefault();opts[active].dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true}));}
      else if(e.key==='Escape')close();
    });
    input.addEventListener('blur',()=>setTimeout(close,120));
  });
})();
