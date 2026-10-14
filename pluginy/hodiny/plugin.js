/* Hodiny v liště — ukázkový plugin z Paluba Marketu.
 * API: HubPluginy.registruj (hub/static/pluginy.js v repu Paluby). */
HubPluginy.registruj('hodiny', (api) => {
  const box = document.createElement('span');
  box.className = 'hodiny-plugin';
  const prace = document.createElement('span');
  prace.className = 'hodiny-prace';
  prace.hidden = true;
  prace.title = 'Jak dlouho Claude v aktivním chatu pracuje';
  const cas = document.createElement('span');
  box.append(prace, cas);

  // Do horní lišty před ikonky; kdyby lišta ještě nebyla, zkusí se to znovu.
  const vloz = () => {
    const lista = document.querySelector('.topbar-actions');
    if (!lista) return setTimeout(vloz, 500);
    lista.parentNode.insertBefore(box, lista);
  };
  vloz();

  const dvoj = (n) => String(n).padStart(2, '0');
  const zacatky = new Map();          // tab → kdy Claude začal pracovat
  let aktivni = (api.aktivniTab() || {}).id || null;

  function tik() {
    const d = new Date();
    const sekundy = !!api.uloziste.get('sekundy');
    cas.textContent = dvoj(d.getHours()) + ':' + dvoj(d.getMinutes()) + (sekundy ? ':' + dvoj(d.getSeconds()) : '');
    const od = aktivni != null ? zacatky.get(aktivni) : null;
    prace.hidden = !od;
    if (od) {
      const s = Math.floor((Date.now() - od) / 1000);
      prace.textContent = '⏱ ' + Math.floor(s / 60) + ':' + dvoj(s % 60);
    }
  }
  setInterval(tik, 1000);
  tik();

  api.on('prace', (e) => {
    if (e.on) { if (!zacatky.has(e.tab)) zacatky.set(e.tab, Date.now()); }
    else zacatky.delete(e.tab);
    tik();
  });
  api.on('tab', (e) => { aktivni = e.id || e.tab || (api.aktivniTab() || {}).id || null; tik(); });

  api.nastaveni((nastaveni) => {
    const label = document.createElement('label');
    const check = document.createElement('input');
    check.type = 'checkbox';
    check.checked = !!api.uloziste.get('sekundy');
    check.onchange = () => { api.uloziste.set('sekundy', check.checked); tik(); };
    label.append(check, ' Ukazovat sekundy');
    nastaveni.append(label);
  });
});
