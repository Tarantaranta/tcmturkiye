/**
 * TCM Türkiye Kategori Sayfası JavaScript Dosyası
 * Kategori sayfalarındaki filtreleme ve sıralama işlevleri için
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM elementleri
  const sortBySelect = document.getElementById('sort-by');
  const contentSearchInput = document.getElementById('content-search');
  const contentGrid = document.querySelector('.content-grid');
  const prevPageButton = document.querySelector('.prev-page');
  const nextPageButton = document.querySelector('.next-page');
  const currentPageSpan = document.querySelector('.current-page');
  const totalPagesSpan = document.querySelector('.total-pages');
  
  // Sayfalama değişkenleri
  let currentPage = 1;
  let itemsPerPage = 9;
  let totalPages = 1;
  
  // Tüm içerik kartlarını al
  const allContentCards = Array.from(document.querySelectorAll('.content-card'));
  
  // Toplam sayfa sayısını hesapla
  totalPages = Math.ceil(allContentCards.length / itemsPerPage);
  if (totalPagesSpan) totalPagesSpan.textContent = totalPages;
  
  // Sayfalama butonlarını güncelle
  function updatePaginationButtons() {
    if (prevPageButton) prevPageButton.disabled = currentPage <= 1;
    if (nextPageButton) nextPageButton.disabled = currentPage >= totalPages;
    if (currentPageSpan) currentPageSpan.textContent = currentPage;
  }
  
  // İçerikleri filtrele ve göster
  function filterAndDisplayContent() {
    // Arama filtresi
    const searchTerm = contentSearchInput ? contentSearchInput.value.toLowerCase() : '';
    
    // Filtrelenmiş içerikleri al
    const filteredCards = allContentCards.filter(card => {
      const title = card.querySelector('h3 a').textContent.toLowerCase();
      const description = card.querySelector('.card-body p').textContent.toLowerCase();
      return title.includes(searchTerm) || description.includes(searchTerm);
    });
    
    // Sıralama seçeneğine göre sırala
    const sortBy = sortBySelect ? sortBySelect.value : 'newest';
    
    filteredCards.sort((a, b) => {
      const titleA = a.querySelector('h3 a').textContent;
      const titleB = b.querySelector('h3 a').textContent;
      const dateA = a.querySelector('.card-date').textContent;
      const dateB = b.querySelector('.card-date').textContent;
      
      if (sortBy === 'newest') {
        return new Date(dateB) - new Date(dateA);
      } else if (sortBy === 'oldest') {
        return new Date(dateA) - new Date(dateB);
      } else if (sortBy === 'a-z') {
        return titleA.localeCompare(titleB);
      } else if (sortBy === 'z-a') {
        return titleB.localeCompare(titleA);
      }
      
      return 0;
    });
    
    // Toplam sayfa sayısını güncelle
    totalPages = Math.ceil(filteredCards.length / itemsPerPage);
    if (totalPagesSpan) totalPagesSpan.textContent = totalPages;
    
    // Geçerli sayfa numarasını kontrol et
    if (currentPage > totalPages) {
      currentPage = totalPages || 1;
    }
    
    // Sayfalama butonlarını güncelle
    updatePaginationButtons();
    
    // Geçerli sayfadaki içerikleri göster
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const visibleCards = filteredCards.slice(startIndex, endIndex);
    
    // Tüm kartları gizle
    allContentCards.forEach(card => {
      card.style.display = 'none';
    });
    
    // Görünür kartları göster
    visibleCards.forEach(card => {
      card.style.display = 'block';
    });
    
    // İçerik yoksa bilgi mesajı göster
    if (filteredCards.length === 0 && contentGrid) {
      contentGrid.innerHTML = '<div class="no-content">Aramanızla eşleşen içerik bulunamadı.</div>';
    } else if (contentGrid && filteredCards.length > 0 && visibleCards.length === 0) {
      // Sayfa boşsa önceki sayfaya git
      currentPage--;
      filterAndDisplayContent();
    }
  }
  
  // Olay dinleyicileri
  if (sortBySelect) {
    sortBySelect.addEventListener('change', () => {
      currentPage = 1;
      filterAndDisplayContent();
    });
  }
  
  if (contentSearchInput) {
    contentSearchInput.addEventListener('input', () => {
      currentPage = 1;
      filterAndDisplayContent();
    });
  }
  
  if (prevPageButton) {
    prevPageButton.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        filterAndDisplayContent();
      }
    });
  }
  
  if (nextPageButton) {
    nextPageButton.addEventListener('click', () => {
      if (currentPage < totalPages) {
        currentPage++;
        filterAndDisplayContent();
      }
    });
  }
  
  // Sayfa yüklendiğinde içerikleri göster
  filterAndDisplayContent();
});
