(() => {
  const base = new URL(document.querySelector('[data-lab-base]').dataset.labBase, location.href);
  const routes = JSON.parse(document.getElementById('lab-legacy-routes').textContent);
  const followLegacy = () => {
    const hash = decodeURIComponent(location.hash.slice(1));
    if (hash && !document.getElementById(hash) && routes[hash]) location.replace(new URL(routes[hash],base).href + '#' + hash);
  };
  followLegacy();
  window.addEventListener('hashchange',followLegacy);
  const viewer = document.createElement('dialog');
  viewer.className = 'lab-zoom'; viewer.setAttribute('aria-label','Enlarged lab screenshot');
  const bar = document.createElement('div'); bar.className='lab-zoom__bar';
  const original = document.createElement('a'); original.target='_blank'; original.rel='noopener'; original.textContent='Open original image';
  const close = document.createElement('button'); close.type='button'; close.setAttribute('aria-label','Close enlarged screenshot'); close.textContent='×';
  const image = document.createElement('img');
  const caption = document.createElement('div'); caption.className='lab-zoom__caption';
  bar.append(original,close); viewer.append(bar,image,caption); document.body.append(viewer);
  close.addEventListener('click',()=>viewer.close());
  viewer.addEventListener('click',event=>{if(event.target===viewer)viewer.close();});
  document.querySelectorAll('a[data-lab-zoom]').forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault(); image.src=link.href; image.alt=link.querySelector('img').alt;
    original.href=link.href; caption.textContent=link.closest('figure').querySelector('figcaption').textContent; viewer.showModal();
  }));
  window.addEventListener('beforeprint',()=>{
    document.querySelectorAll('img[loading]').forEach(img=>img.loading='eager');
    document.querySelectorAll('details').forEach(details=>details.open=true);
  });
})();
