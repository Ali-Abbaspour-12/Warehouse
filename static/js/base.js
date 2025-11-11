
const divs = document.querySelectorAll('.navItem');

divs.forEach(div => {
  div.addEventListener('click', () => {
    // حذف کلاس active از همه divها
    divs.forEach(d => d.classList.remove('active'));
    // اضافه کردن کلاس active فقط به div کلیک شده
    div.classList.add('active');
  });
});
