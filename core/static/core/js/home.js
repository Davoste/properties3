
document.getElementById("calculator-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const P = parseFloat(document.getElementById("homePrice").value) - parseFloat(document.getElementById("downPayment").value);
    const years = parseFloat(document.getElementById("loanTerm").value);
    const r = parseFloat(document.getElementById("interestRate").value) / 100 / 12;
    const n = years * 12;

    const monthly = (P * r) / (1 - Math.pow(1 + r, -n));
    const result = isFinite(monthly) ? `$${monthly.toFixed(2)} / month` : "Please check your inputs";

    document.getElementById("monthlyPayment").textContent = `Estimated Monthly Payment: ${result}`;
});


window.scrollTestimonials = function(direction) {
  const container = document.getElementById("testimonialContainer");
  const scrollAmount = 320;
  container.scrollBy({
    left: direction * scrollAmount,
    behavior: "smooth",
  });
};



// Get current page filename 
const currentPage = window.location.pathname.split("/").pop();

// Get all navbar links
const navLinks = document.querySelectorAll(".navbar a");

navLinks.forEach(link => {
    // Get href from each link
    const linkPage = link.getAttribute("href");

    // Match filename and apply "active" class
    if (linkPage === currentPage) {
    link.classList.add("active");
    }
});


const menuToggle = document.getElementById('mobile-menu');
const navButtonsContainer = document.querySelector('.nav-buttons-container');

menuToggle.addEventListener('click', () => {
    navButtonsContainer.classList.toggle('show');
});


const dropdownToggle = document.querySelector('.dropdown-toggle');
const dropdownMenu = document.querySelector('.dropdown1-menu');

dropdownToggle.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
});

  
function toggleMenu() {
document.getElementById("navbar").classList.toggle("active");
}

const swiper = new Swiper(".featuredSwiper", {
    slidesPerView: 1,
    spaceBetween: 30,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    breakpoints: {
        768: {
        slidesPerView: 2
        },
        1024: {
        slidesPerView: 3
        }
    }
});