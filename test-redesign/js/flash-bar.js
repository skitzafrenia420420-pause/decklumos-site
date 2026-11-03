/* Shared TODAY'S BEST deal bar for non-home test pages. Same data + markup as the home hero flash. */
(function(){
  if(document.getElementById('flash'))return; // home renders its own
  var hero=document.querySelector('main > section.phero, main > section.ghero, main > section');
  if(!hero)return;
  var css='.flashbar{display:flex!important;justify-content:flex-start;margin-bottom:22px!important;position:relative;z-index:2}'+
  '.flashbar .flash{display:inline-flex;flex-wrap:wrap;align-items:center;gap:6px 12px;background:rgba(11,31,58,.72);border:1px solid rgba(255,77,77,.9);box-shadow:0 0 0 3px rgba(255,77,77,.18);color:#fff;text-decoration:none;border-radius:18px;padding:8px 18px 8px 8px;max-width:100%;box-sizing:border-box;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}'+
  '.flashbar .flash .tg{background:#FF4D4D;color:#fff;font:800 12px Inter,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;border-radius:999px;padding:6px 12px}'+
  '.flashbar .flash b{font:600 17px Fredoka,Inter,sans-serif;overflow-wrap:anywhere}'+
  '.flashbar .flash small{opacity:.8;font-size:13px;overflow-wrap:anywhere}'+
  'body.has-flash main>section.phero{padding-top:118px!important}body.has-flash main>section.ghero{padding-top:118px!important}'+
  '@media(max-width:700px){.flashbar .flash{padding:6px 14px 6px 6px;gap:4px 10px}.flashbar .flash .tg{font-size:10.5px;padding:5px 10px}.flashbar .flash b{font-size:15px}.flashbar .flash small{font-size:11.5px}body.has-flash main>section.phero,body.has-flash main>section.ghero{padding-top:104px!important}}';
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function ck(s){return new Date(s).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}
  function fresh(S){var t=new Date(S.checked).getTime();return isNaN(t)?false:(Date.now()-t)<=7*864e5}
  fetch('/test-redesign/data/sailings.json?v='+Date.now(),{cache:'no-cache'}).then(function(r){return r.json()}).then(function(S){
    var D=S.deals;if(!D||!D.regions||!D.regions.length||fresh(S)===false)return;
    var f=D.fromPerNight;if(!f)return;
    var st=document.createElement('style');st.id='flashbar-css';st.textContent=css;document.head.appendChild(st);
    var a=document.createElement('a');a.className='flash';a.id='flash';a.href=f.sailing.url;a.target='_blank';a.rel='noopener noreferrer';
    a.innerHTML='<span class="tg">Today\'s best</span><b>Cruises from $'+f.value+' a night</b><small>'+esc(f.sailing.nights)+'-night '+esc(f.sailing.title.replace(/^\d+-Day /,''))+' · carnival.com, checked '+ck(S.checked)+'</small>';
    var w=document.createElement('div');w.className='wrap flashbar';w.appendChild(a);
    hero.insertBefore(w,hero.firstChild);
    document.body.classList.add('has-flash');
  }).catch(function(){});
})();
