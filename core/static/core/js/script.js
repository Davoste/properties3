const hamburger = document.getElementById('hamburger');
const navList = document.querySelector('.nav_list');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('is-active');
  navList.classList.toggle('nav-open');
});


document.querySelectorAll('.nav_list li a').forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('nav-open');
      hamburger.classList.remove('is-active');
    });
  });
  