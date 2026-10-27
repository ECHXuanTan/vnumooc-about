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
  // Đơn vị thành viên: slideshow lặp vô tận, mỗi lần dịch một ô sang trái (ô mới vào từ mép phải),
  // sau ô cuối là ô đầu (danh sách được nhân đôi để nối vòng). Mỗi đơn vị một nút như slideshow đầu trang.
  // Dừng khi rê chuột/focus; vuốt ngang để chuyển; không tự chạy khi người dùng chọn giảm chuyển động.
  const slider = document.querySelector('.member-slider');
  const sliderDots = document.querySelector('.member-dots');
  if (slider && sliderDots) {
    const strip = slider.querySelector('.member-track');
    const originals = [...strip.children];
    const total = originals.length;
    originals.forEach(item => {
      const copy = item.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      copy.querySelectorAll('a, button').forEach(el => el.setAttribute('tabindex', '-1'));
      strip.append(copy);
    });
    let pos = 0, step = 0, sliderTimer, hold = false;
    const measure = () => { step = strip.children[1].offsetLeft - strip.children[0].offsetLeft; };
    const place = animate => {
      strip.classList.toggle('no-anim', !animate);
      strip.style.transform = `translateX(${-pos * step}px)`;
    };
    const unitDots = originals.map((item, i) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'scene-dot';
      dot.setAttribute('aria-label', sliderDots.dataset.dotLabel.replace('{i}', i + 1).replace('{n}', total).replace('{name}', item.querySelector('.member-name').textContent));
      dot.append(document.createElement('span'));
      dot.addEventListener('click', () => { goTo(i); startSlider(); });
      return dot;
    });
    sliderDots.replaceChildren(...unitDots);
    const mark = () => unitDots.forEach((dot, i) => {
      const on = i === pos % total;
      dot.classList.toggle('on', on);
      dot.setAttribute('aria-pressed', String(on));
    });
    // Đi quá ô cuối thì đang đứng ở bản sao: nhảy về ô thật tương ứng, không hiệu ứng.
    const normalize = () => { if (pos >= total) { pos -= total; place(false); } };
    function goTo(next, animate = !motion.matches) {
      pos = next;
      place(animate);
      mark();
      if (!animate) normalize();
    }
    const forward = () => goTo(pos + 1);
    const backward = () => {
      if (pos === 0) { pos = total; place(false); void strip.offsetWidth; }
      goTo(pos - 1);
    };
    strip.addEventListener('transitionend', event => { if (event.target === strip) normalize(); });
    function startSlider() {
      clearInterval(sliderTimer);
      if (motion.matches || document.hidden) return;
      sliderTimer = setInterval(() => { if (!hold) forward(); }, 3000);
    }
    slider.addEventListener('pointerenter', () => { hold = true; });
    slider.addEventListener('pointerleave', () => { hold = false; });
    // Tab tới một ô đang khuất thì kéo ô đó vào khung.
    slider.addEventListener('focusin', event => {
      hold = true;
      slider.scrollLeft = 0;
      const item = event.target.closest('li'), i = originals.indexOf(item);
      if (i < 0) return;
      const box = item.getBoundingClientRect(), view = slider.getBoundingClientRect();
      if (box.left < view.left || box.right > view.right) goTo(i);
    });
    slider.addEventListener('focusout', () => { hold = false; });
    let startX = null, swiped = false;
    slider.addEventListener('pointerdown', event => { startX = event.clientX; swiped = false; });
    slider.addEventListener('pointerup', event => {
      if (startX === null) return;
      const dx = event.clientX - startX;
      startX = null;
      if (Math.abs(dx) < 40) return;
      swiped = true;
      dx < 0 ? forward() : backward();
      startSlider();
    });
    slider.addEventListener('pointercancel', () => { startX = null; });
    slider.addEventListener('click', event => { if (swiped) { event.preventDefault(); swiped = false; } }, true);
    let resizeTimer;
    addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { measure(); place(false); }, 150); });
    document.addEventListener('visibilitychange', startSlider);
    motion.addEventListener('change', startSlider);
    measure();
    place(false);
    mark();
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
