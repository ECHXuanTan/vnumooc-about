/* Vanilla JavaScript: no added runtime or animation dependency. */
(() => {
  'use strict';
  const nav = document.getElementById('nav');
  const menu = document.querySelector('.menu-toggle');
  const links = document.getElementById('page-nav');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = matchMedia('(max-width: 960px)');
  const navLinks = [...links.querySelectorAll('a')];
  const sectionPairs = navLinks.map(link => ({link, section: document.querySelector(link.hash)}));
  let ticking = false;
  function updateScroll() {
    nav.classList.toggle('scrolled', scrollY > 40);
    let current = null;
    sectionPairs.forEach(pair => { if (pair.section.getBoundingClientRect().top <= 150) current = pair; });
    navLinks.forEach(link => link.removeAttribute('aria-current'));
    current?.link.setAttribute('aria-current', 'location');
    ticking = false;
  }
  addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(updateScroll); ticking = true; }
  }, {passive:true});
  updateScroll();
  function closeMenu(returnFocus = false) {
    links.classList.remove('is-open'); nav.classList.remove('menu-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.querySelector('.sr-only').textContent = 'Mở menu';
    if (returnFocus) menu.focus();
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    links.classList.toggle('is-open', open); nav.classList.toggle('menu-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.querySelector('.sr-only').textContent = open ? 'Đóng menu' : 'Mở menu';
  });
  narrow.addEventListener('change', () => closeMenu());
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') closeMenu(true);
  });
  document.addEventListener('click', event => { if (!nav.contains(event.target)) closeMenu(); });
  document.addEventListener('focusin', event => { if (!nav.contains(event.target)) closeMenu(); });
  // Anchor navigation also moves keyboard focus to the destination.
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const target = document.querySelector(link.hash);
      if (!target) return;
      event.preventDefault(); closeMenu();
      target.setAttribute('tabindex', '-1'); target.focus({preventScroll:true});
      target.scrollIntoView({behavior:motion.matches ? 'instant' : 'smooth', block:'start'});
      history.replaceState(null, '', link.hash);
    });
  });
  // Stable fallback values are in HTML. Animation runs once, only on entry.
  const counted = new WeakSet();
  const locales = {vi:'vi-VN', en:'en-US'};
  const format = (n, el) => locales[el.dataset.format] ? n.toLocaleString(locales[el.dataset.format]) : String(n);
  function countUp(el) {
    if (counted.has(el)) return;
    counted.add(el);
    const total = Number(el.dataset.count);
    if (motion.matches) { el.textContent = format(total,el); return; }
    const start = performance.now();
    function frame(now) {
      const progress = motion.matches ? 1 : Math.min((now-start)/600,1);
      el.textContent = format(Math.round(total*(1-Math.pow(1-progress,3))),el);
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('in');
      observer.unobserve(entry.target);
    }), {threshold:0.08});
    document.querySelectorAll('.reveal, #timeline').forEach(el => observer.observe(el));
    const counterObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      countUp(entry.target); counterObserver.unobserve(entry.target);
    }), {threshold:0.4});
    document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));
    document.documentElement.classList.add('js-ready');
  }
  // Carousel: continuous autoplay with manual dot selection.
  const scenes = [...document.querySelectorAll('.hero .scene')];
  const dots = [...document.querySelectorAll('.hero .scene-dot')];
  let index = 0, timer;
  function showScene(next) {
    const leaving = index;
    index = next;
    scenes.forEach((scene,i) => {
      const on = i === index;
      scene.classList.toggle('active', on);
      scene.classList.toggle('prev', i === leaving && !on);
      scene.setAttribute('aria-hidden',String(!on));
      dots[i].classList.toggle('on', on);
      dots[i].setAttribute('aria-pressed',String(on));
    });
  }
  function startRotation() {
    clearInterval(timer);
    if (motion.matches || document.hidden) return;
    timer = setInterval(() => showScene((index+1)%scenes.length),2000);
  }
  dots.forEach((dot,i) => dot.addEventListener('click', () => { showScene(i); startRotation(); }));
  document.addEventListener('visibilitychange',startRotation);
  motion.addEventListener('change',startRotation);
  startRotation();
  // Đơn vị thành viên: slideshow theo nhóm ô vừa khung, đi lần lượt từ ô đầu (trái) tới ô cuối (phải)
  // rồi quay lại; thanh điều hướng giống slideshow ảnh đầu trang. Dừng khi rê chuột/focus; không tự chạy
  // khi người dùng chọn giảm chuyển động. Số nhóm tính lại theo độ rộng khung.
  const slider = document.querySelector('.member-slider');
  const sliderDots = document.querySelector('.member-dots');
  if (slider && sliderDots) {
    const strip = slider.querySelector('.member-track');
    const cards = [...strip.children];
    let stops = [0], current = 0, sliderTimer, hold = false, sliderTicking = false;
    const computeStops = () => {
      const view = strip.clientWidth, max = strip.scrollWidth - view;
      stops = [0];
      let start = 0;
      while (start < max - 1) {
        const next = cards.find(card => card.offsetLeft + card.offsetWidth > start + view + 1);
        if (!next) break;
        start = Math.min(next.offsetLeft, max);
        stops.push(start);
      }
    };
    const markDot = () => {
      current = stops.reduce((best, stop, i) => Math.abs(stop - strip.scrollLeft) < Math.abs(stops[best] - strip.scrollLeft) ? i : best, 0);
      [...sliderDots.children].forEach((dot, i) => {
        dot.classList.toggle('on', i === current);
        dot.setAttribute('aria-pressed', String(i === current));
      });
    };
    const goTo = i => strip.scrollTo({left: stops[i], behavior: motion.matches ? 'auto' : 'smooth'});
    const buildDots = () => {
      computeStops();
      sliderDots.replaceChildren(...stops.map((_, i) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'scene-dot';
        dot.setAttribute('aria-label', sliderDots.dataset.dotLabel.replace('{i}', i + 1).replace('{n}', stops.length));
        dot.append(document.createElement('span'));
        dot.addEventListener('click', () => { goTo(i); startSlider(); });
        return dot;
      }));
      sliderDots.parentElement.hidden = stops.length < 2;
      markDot();
    };
    function startSlider() {
      clearInterval(sliderTimer);
      if (motion.matches || document.hidden || stops.length < 2) return;
      sliderTimer = setInterval(() => { if (!hold) goTo((current + 1) % stops.length); }, 3500);
    }
    strip.addEventListener('scroll', () => {
      if (!sliderTicking) { requestAnimationFrame(() => { markDot(); sliderTicking = false; }); sliderTicking = true; }
    }, {passive:true});
    [slider, sliderDots].forEach(el => {
      el.addEventListener('pointerenter', () => { hold = true; });
      el.addEventListener('pointerleave', () => { hold = false; });
    });
    slider.addEventListener('focusin', () => { hold = true; });
    slider.addEventListener('focusout', () => { hold = false; });
    let resizeTimer;
    addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { buildDots(); startSlider(); }, 150); });
    document.addEventListener('visibilitychange', startSlider);
    motion.addEventListener('change', startSlider);
    buildDots();
    startSlider();
  }
  // Native modal dialogs contain only About-page information, no fake login form.
  let opener;
  document.querySelectorAll('[data-dialog]').forEach(button => button.addEventListener('click', () => {
    const dialog = document.getElementById(button.dataset.dialog);
    opener=button; dialog.showModal(); dialog.scrollTop=0;
    document.body.classList.add('dialog-open');
  }));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('keydown', event => {
      if (event.key !== 'Tab') return;
      const controls = [...dialog.querySelectorAll('button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]')];
      const first = controls[0], last = controls[controls.length-1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    dialog.addEventListener('click', event => {
      const rect=dialog.getBoundingClientRect();
      if (event.target===dialog && (event.clientX<rect.left || event.clientX>rect.right || event.clientY<rect.top || event.clientY>rect.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); opener?.focus({preventScroll:true}); });
  });
})();
