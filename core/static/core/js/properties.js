// Get elements
const track = document.querySelector('.carousel-track');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');
let currentPage = 0;           // Tracks current page number
let isLoading = false;         // Prevent multiple simultaneous requests
let hasMorePages = true;     // Whether more pages exist
const ITEMS_PER_PAGE = 6;    // Adjust based on how many items you request per page

let currentIndex = 0;

function loadMoreItems() {
  if (!hasMorePages || isLoading) return;

  isLoading = true;

  console.log("fetching.......")
  // Simulate fetch for demo purposes
  fetch(`https://23de-41-90-178-17.ngrok-free.app/get_featured_properties?page=${currentPage + 1}`)
  .then(res => res.json())
  .then(data => {
    const properties = data.properties;

    properties.forEach(property => {
      const newItem = document.createElement('li');
      newItem.className = 'carousel-item';
      newItem.innerHTML = `
        
        <h2>${property.title}</h2>
        <p>Purpose: ${property.purpose}</p>
        <p>Bedrooms: ${property.bedrooms}</p>
        <p>Location: ${property.city}, ${property.country}</p>
        <p>Type: ${property.property_type}</p>
        <p>Price: ${property.price}</p>
      `;
      track.appendChild(newItem);
    });

    hasMorePages = data.has_next;
    currentPage = data.current_page;
    isLoading = false;

    updateCarousel();
  })
  .catch(err => {
    console.error('Fetch error:', err);
    isLoading = false;
  });

}

function checkIfNearEnd() {
  const item = document.querySelector('.carousel-item');
  const container = document.querySelector('.carousel-container');
  const track = document.querySelector('.carousel-track');

  if (!item || !container || !track) return;

  const itemWidth = item.offsetWidth;
  const trackWidth = track.scrollWidth;
  const containerWidth = container.offsetWidth;

  const offset = currentIndex * itemWidth; // keep it positive!
  const visibleSlides = getVisibleSlides();
  const scrolledArea = offset + containerWidth;
  const remaining = trackWidth - scrolledArea;

  if (remaining < itemWidth * visibleSlides) {
    loadMoreItems();
  }
}


// Get number of visible slides based on screen size
function getVisibleSlides() {
  // if (window.innerWidth >= 1024) return 4;
  if (window.innerWidth >= 768) return 3;
  if (window.innerWidth >= 480) return 2;
  return 1;
}




// Update slide position
function updateCarousel() {
  const itemWidth = document.querySelector('.carousel-item').offsetWidth + 20; // include gap
  const offset = -currentIndex * itemWidth;
  track.style.transform = `translateX(${offset}px)
  `;

  // Dynamically adjust padding to remove empty space at the end
  const totalItems = document.querySelectorAll('.carousel-item').length;
  const visibleSlides = getVisibleSlides();

  // if (currentIndex >= totalItems - visibleSlides) {
  //   track.style.paddingRight = '15px'; // Remove right padding at end
  // } else {
  //   track.style.paddingRight = '20px'; // Restore normal padding
  // }


  // Update button states
  toggleButtons();

}




function toggleButtons() {
  const totalItems = document.querySelectorAll('.carousel-item').length;
  const visibleSlides = getVisibleSlides();
  console.log(`visibleslides: ${visibleSlides}`)
  console.log(`currentindex is: ${currentIndex}`)

  const sizee = '-40px'

  if (currentIndex === 0){
    prevBtn.classList.add('hidden')
  } else{
    prevBtn.classList.remove('hidden')
  }

  if (currentIndex >= totalItems - visibleSlides){
    nextBtn.classList.add('hidden')
  }else{
    nextBtn.classList.remove('hidden');

  }
}


// Handle button clicks
prevBtn.addEventListener('click', () => {
  if (currentIndex > 0) {
    currentIndex--;
    updateCarousel();
    checkIfNearEnd();
  }
});

nextBtn.addEventListener('click', () => {
  const totalItems = document.querySelectorAll('.carousel-item').length;
  const visibleSlides = getVisibleSlides();
  if (currentIndex < totalItems - visibleSlides) {
    currentIndex++;
    updateCarousel();
    checkIfNearEnd();
  }
});

// Make sure carousel updates on resize
window.addEventListener('resize', () => {
  updateCarousel();
  checkIfNearEnd();
});

// Initialize

loadMoreItems();
;

let touchStartX = 0;
let touchEndX = 0;

const carouselContainer = document.querySelector('.carousel-container');

carouselContainer.addEventListener('touchstart', (e) => {
  touchStartX = e.touches[0].clientX;
}, { passive: true });

carouselContainer.addEventListener('touchend', (e) => {
  touchEndX = e.changedTouches[0].clientX;
  handleSwipe();
});

function handleSwipe() {
  const diff = touchEndX - touchStartX;
  const threshold = 50; // Minimum swipe distance

  if (diff > threshold) {
    // Swipe right -> go to previous
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
      checkIfNearEnd();
    }
  } else if (diff < -threshold) {
    // Swipe left -> go to next
    const totalItems = document.querySelectorAll('.carousel-item').length;
    const visibleSlides = getVisibleSlides();
    if (currentIndex < totalItems - visibleSlides) {
      currentIndex++;
      updateCarousel();
      checkIfNearEnd();
    }
  }
}