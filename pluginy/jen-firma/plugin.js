/* Jen firma — okno Aladina je vždycky ve firemním prostoru.
 *
 * Osobní prostor se v přepínači neukazuje a cokoli, co by do něj přepnulo
 * (i starý výběr v prohlížeči), skončí ve firmě. Opírá se o globální funkce
 * hubu z hub/static/hub.js — firmyList, prostor, setProstor, showMenu —
 * a samotnou appku nemění. Instaluje a zapíná ho server (jen_firma.py).
 */
HubPluginy.registruj('jen-firma', () => {
  const firma = () => {
    const list = typeof firmyList === 'function' ? firmyList() : [];
    const f = list.find((x) => x.zkratka === 'firma') || list[0];
    return f ? f.zkratka : '';
  };

  // Přepnutí do osobního prostoru ('') vede do firmy.
  const setProstorPuvodni = window.setProstor;
  if (typeof setProstorPuvodni === 'function') {
    window.setProstor = function (slug, keepTab) {
      return setProstorPuvodni.call(this, slug || firma(), keepTab);
    };
  }

  // Přepínač prostoru: řádek „Osobní prostor“ (ikona uživatele) pryč.
  const showMenuPuvodni = window.showMenu;
  if (typeof showMenuPuvodni === 'function') {
    window.showMenu = function (x, y, items, opts) {
      const jePrepinac = Array.isArray(items) && items.length && items[0].icon === 'i-user' &&
        /^Osobní/.test(String(items[0].label || ''));
      return showMenuPuvodni.call(this, x, y, jePrepinac ? items.slice(1) : items, opts);
    };
  }

  // Okno samo ve firmě — hned, a znovu, kdyby se stav načetl později.
  // prostor() vrací '' pro osobní prostor (i pro neznámou firmu).
  const drz = () => {
    const f = firma();
    if (f && typeof prostor === 'function' && !prostor()) window.setProstor(f);
  };
  drz();
  setInterval(drz, 2000);
});
