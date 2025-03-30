/**
 * TCM Türkiye Detay Sayfası JavaScript Dosyası
 * İçerik detay sayfalarındaki ilgili içerikler ve paylaşım işlevleri için
 */

document.addEventListener('DOMContentLoaded', () => {
  // İlgili içerikleri yükle
  loadRelatedContent();
  
  // Paylaşım butonlarını ayarla
  setupSharingButtons();
});

/**
 * İlgili içerikleri yükler
 */
function loadRelatedContent() {
  const relatedContentList = document.getElementById('related-content-list');
  if (!relatedContentList) return;
  
  // Mevcut sayfanın URL'sinden kategori ve içerik ID'sini al
  const currentUrl = window.location.pathname;
  const urlParts = currentUrl.split('/');
  
  // URL formatı: /content/html/category/item_id.html
  if (urlParts.length < 5) return;
  
  const category = urlParts[urlParts.length - 2];
  const itemId = urlParts[urlParts.length - 1].replace('.html', '');
  
  // Kategori içeriklerini al
  fetch(`/content/json/${category}_tracking.json`)
    .then(response => response.json())
    .then(data => {
      const items = data.items || {};
      
      // Mevcut içerik dışındaki içerikleri al
      const otherItems = Object.keys(items)
        .filter(id => id !== itemId)
        .map(id => ({
          id,
          title: items[id].title,
          date: items[id].date_added,
          source: items[id].source
        }));
      
      // En fazla 5 ilgili içerik göster
      const relatedItems = otherItems.slice(0, 5);
      
      if (relatedItems.length === 0) {
        relatedContentList.innerHTML = '<li>İlgili içerik bulunamadı.</li>';
        return;
      }
      
      // İlgili içerikleri HTML olarak oluştur
      let html = '';
      
      relatedItems.forEach(item => {
        html += `
          <li>
            <a href="/content/html/${category}/${item.id}.html">${item.title}</a>
            <small>${item.source}</small>
          </li>
        `;
      });
      
      relatedContentList.innerHTML = html;
    })
    .catch(error => {
      console.error('İlgili içerikler yüklenirken hata:', error);
      relatedContentList.innerHTML = '<li>İlgili içerikler yüklenemedi.</li>';
    });
}

/**
 * Paylaşım butonlarını ayarlar
 */
function setupSharingButtons() {
  const shareButtons = document.querySelectorAll('.social-share a');
  if (!shareButtons.length) return;
  
  const pageUrl = encodeURIComponent(window.location.href);
  const pageTitle = encodeURIComponent(document.title);
  
  shareButtons.forEach(button => {
    if (button.classList.contains('facebook')) {
      button.href = `https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`;
    } else if (button.classList.contains('twitter')) {
      button.href = `https://twitter.com/intent/tweet?url=${pageUrl}&text=${pageTitle}`;
    } else if (button.classList.contains('linkedin')) {
      button.href = `https://www.linkedin.com/sharing/share-offsite/?url=${pageUrl}`;
    } else if (button.classList.contains('whatsapp')) {
      button.href = `https://api.whatsapp.com/send?text=${pageTitle} ${pageUrl}`;
    } else if (button.classList.contains('email')) {
      button.href = `mailto:?subject=${pageTitle}&body=${pageUrl}`;
    }
    
    button.target = '_blank';
    button.rel = 'noopener noreferrer';
  });
}
