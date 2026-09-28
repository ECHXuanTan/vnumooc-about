/* Slideshow "Giảng viên tiêu biểu" ở trang giới thiệu.
   Đọc data/featured.json (biên tập tay), data/instructors.json (môn, tổ) và data/instructors_profiles.json (ảnh). */
(() => {
  'use strict';
  const root = document.getElementById('giang-vien-tieu-bieu');
  if (!root) return;
  const track = document.getElementById('star-track');
  const count = document.getElementById('star-count');
  const dots = document.getElementById('star-dots');
  const toggle = root.querySelector('.star-toggle');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const LOGO = {hcmut:'hcmut.png', hcmus:'hcmus.png', ussh:'ussh.png', uit:'uit.png', iu:'iu.png', uel:'uel.svg', agu:'agu.png'};
  const DELAY = 7000;

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fold = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
  const slugOf = n => fold(n).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const ini = n => { const w = n.trim().split(/\s+/); return (w[0][0] + (w.length > 1 ? w[w.length - 1][0] : '')).toUpperCase(); };
  const shortMon = m => m.replace('Khối học phần ', '');
  const https = u => /^https:\/\//.test(u || '');
  // "2024" → "năm 2024", "2025 đợt 1" → "đợt 1 năm 2025"
  const fmtDot = d => { const m = /^(\d{4}) (đợt \d+)$/.exec(d || ''); return m ? `${m[2]} năm ${m[1]}` : `năm ${d}`; };

  let slides = [], index = 0, timer = null, paused = motion.matches, hovering = false, offscreen = false;

  function courseLine(p, m, all) {
    const team = all.filter(a => a.mon.includes(m)).length;
    const parts = [`tổ ${team} giảng viên`];
    if (p.lead_mon?.includes(m)) parts.push('trưởng nhóm');
    if (p.dot?.[m]) parts.push(`tham gia từ ${fmtDot(p.dot[m])}`);
    return `<li><b>${esc(shortMon(m))}</b><small>${esc(parts.join(', '))}</small></li>`;
  }

  function render(items, all, profiles) {
    track.innerHTML = items.map(({f, p, slug}, i) => {
      const photo = profiles[f.person_id]?.photo;
      const img = typeof photo === 'string' && (https(photo) || /^assets\//.test(photo))
        ? `<img src="${esc(photo)}" alt="Ảnh ${esc(p.n)}" loading="lazy" decoding="async">` : '';
      const src = (f.sources || []).filter(s => https(s.url))
        .map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)} ↗</a>`).join(', ');
      return `<article class="star-slide" role="group" aria-roledescription="slide" aria-label="${i + 1} / ${items.length}: ${esc(p.n)}">
        <div class="star-photo" aria-hidden="${img ? 'false' : 'true'}">${esc(ini(p.n))}${img}</div>
        <div class="star-body">
          <span class="star-mark">${esc(f.mark)}</span>
          <p class="star-line">${esc(f.headline)}</p>
          <p class="star-who"><b><small>${esc(f.t || p.t)}</small>${esc(p.n)}</b><span><img src="assets/about/logos/${LOGO[p.u]}" alt="">${esc(p.us)}</span></p>
          <p class="star-detail">${esc(f.detail)}</p>
          <div class="star-course"><div class="sub">Môn học xây dựng trên VNU-MOOC</div><ul>${p.mon.map(m => courseLine(p, m, all)).join('')}</ul></div>
          <p class="star-foot"><a class="star-more" href="giang-vien.html#gv/${esc(slug)}">Xem hồ sơ giảng viên</a>${src ? `<span>Nguồn: ${src}</span>` : ''}</p>
        </div></article>`;
    }).join('');
    dots.innerHTML = items.map(({p}, i) => `<button type="button" data-i="${i}" aria-label="Xem ${esc(p.n)}"></button>`).join('');
    slides = [...track.children];
    track.querySelectorAll('.star-photo img').forEach(img => img.addEventListener('error', () => {
      img.parentElement.setAttribute('aria-hidden', 'true'); img.remove();
    }));
  }

  function mark(i) {
    index = i;
    count.textContent = `${i + 1} / ${slides.length}`;
    [...dots.children].forEach((d, k) => d.setAttribute('aria-current', k === i ? 'true' : 'false'));
    slides.forEach((s, k) => s.inert = k !== i);
  }
  function go(i) {
    i = (i + slides.length) % slides.length;
    track.scrollTo({left: i * track.clientWidth, behavior: motion.matches ? 'auto' : 'smooth'});
    mark(i);
  }

  function schedule() {
    clearTimeout(timer);
    if (!paused && !hovering && !offscreen && slides.length > 1) timer = setTimeout(() => { go(index + 1); schedule(); }, DELAY);
  }
  function setPaused(v) {
    paused = v;
    toggle.textContent = v ? 'Tự chạy' : 'Tạm dừng';
    toggle.setAttribute('aria-pressed', v ? 'true' : 'false');
    schedule();
  }

  function init([featured, all, profiles]) {
    const seen = new Set();
    const bySlugKey = new Map();
    for (const a of all) {
      let slug = slugOf(a.n);
      if (seen.has(slug)) slug += '-' + a.u;
      seen.add(slug);
      bySlugKey.set(`${a.u}:${slugOf(a.n)}`, {p:a, slug});
    }
    const items = (featured?.items || []).map(f => ({f, ...bySlugKey.get(f.person_id)})).filter(x => x.p);
    if (!items.length) return;
    render(items, all, profiles || {});
    root.querySelector('.star-note').hidden = featured.status !== 'pending';
    root.hidden = false;
    mark(0);
    setPaused(motion.matches);

    root.querySelector('.star-prev').addEventListener('click', () => { go(index - 1); schedule(); });
    root.querySelector('.star-next').addEventListener('click', () => { go(index + 1); schedule(); });
    toggle.addEventListener('click', () => setPaused(!paused));
    dots.addEventListener('click', e => { const b = e.target.closest('[data-i]'); if (b) { go(+b.dataset.i); schedule(); } });
    track.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); schedule(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); schedule(); }
    });
    // vuốt tay trên điện thoại: đồng bộ chỉ số theo vị trí cuộn
    let settle;
    track.addEventListener('scroll', () => {
      clearTimeout(settle);
      settle = setTimeout(() => {
        const i = Math.round(track.scrollLeft / track.clientWidth);
        if (i !== index && slides[i]) { mark(i); schedule(); }
      }, 120);
    }, {passive:true});
    root.addEventListener('pointerenter', () => { hovering = true; schedule(); });
    root.addEventListener('pointerleave', () => { hovering = false; schedule(); });
    root.addEventListener('focusin', () => { hovering = true; schedule(); });
    root.addEventListener('focusout', e => { if (!root.contains(e.relatedTarget)) { hovering = false; schedule(); } });
    addEventListener('resize', () => track.scrollTo({left: index * track.clientWidth, behavior:'auto'}));
    // chỉ tự chạy khi slideshow nằm trong màn hình
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(es => { offscreen = !es[0].isIntersecting; schedule(); }, {threshold:.4}).observe(track);
    }
  }

  const json = (url, fallback) => fetch(url).then(r => r.ok ? r.json() : fallback).catch(() => fallback);
  Promise.all([json('data/featured.json', null), json('data/instructors.json', []), json('data/instructors_profiles.json', {})]).then(init);
})();
