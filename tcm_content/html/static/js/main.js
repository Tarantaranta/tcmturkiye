/**
 * TCM Türkiye Ana JavaScript Dosyası
 * Firebase kimlik doğrulama ve genel site işlevselliği için
 */

// DOM elementleri
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const profileButton = document.getElementById('profile-button');
const userAvatar = document.getElementById('user-avatar');
const avatarImg = document.getElementById('avatar-img');

// Kimlik doğrulama durumu değişikliklerini dinle
firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    // Kullanıcı giriş yapmış
    loginButton.style.display = 'none';
    logoutButton.style.display = 'block';
    profileButton.style.display = 'block';
    
    // Profil butonuna kullanıcı adını ekle
    if (user.displayName) {
      profileButton.textContent = user.displayName;
    }
    
    // Kullanıcı avatarını göster
    if (user.photoURL) {
      userAvatar.style.display = 'block';
      avatarImg.src = user.photoURL;
    } else {
      userAvatar.style.display = 'none';
    }
    
    console.log('Giriş yapan kullanıcı:', user.displayName || user.email);
  } else {
    // Kullanıcı çıkış yapmış
    loginButton.style.display = 'block';
    logoutButton.style.display = 'none';
    profileButton.style.display = 'none';
    userAvatar.style.display = 'none';
    console.log('Kullanıcı çıkış yaptı');
  }
});

// Giriş yap butonu tıklama olayı
if (loginButton) {
  loginButton.addEventListener('click', () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('profile');
    provider.addScope('email');
    
    // Popup yerine redirect yöntemini kullan
    firebase.auth().signInWithRedirect(provider)
      .catch((error) => {
        console.error('Giriş hatası:', error);
        alert('Giriş yapılırken bir hata oluştu: ' + error.message);
      });
  });
  
  // Redirect sonrası sonucu işle
  firebase.auth().getRedirectResult().then((result) => {
    if (result.user) {
      console.log('Giriş başarılı:', result.user.displayName);
    }
  }).catch((error) => {
    console.error('Redirect sonrası hata:', error);
  });
}

// Çıkış yap butonu tıklama olayı
if (logoutButton) {
  logoutButton.addEventListener('click', () => {
    firebase.auth().signOut()
      .catch((error) => {
        console.error('Çıkış hatası:', error);
        alert('Çıkış yapılırken bir hata oluştu: ' + error.message);
      });
  });
}

// Profil butonu tıklama olayı
if (profileButton) {
  profileButton.addEventListener('click', () => {
    // Profil sayfasına yönlendir (henüz oluşturulmadı)
    alert('Profil sayfası yakında eklenecek!');
  });
}

// Son eklenen içerikleri yükle (Ana sayfa için)
function loadLatestContent() {
  const latestContentElement = document.getElementById('latest-content');
  if (!latestContentElement) return;
  
  // Son eklenen içerikleri almak için API çağrısı
  fetch('/content/json/content_index.json')
    .then(response => response.json())
    .then(data => {
      // Her kategoriden son eklenen içeriği al
      const latestItems = [];
      
      for (const category in data.categories) {
        const categoryData = data.categories[category];
        const categoryFile = categoryData.file;
        
        // Kategori dosyasını oku
        fetch(`/content/json/${categoryFile}`)
          .then(response => response.json())
          .then(categoryContent => {
            // Kategoriye göre içerik listesini al
            let items = [];
            if (category === 'research') items = categoryContent.articles || [];
            else if (category === 'theory') items = categoryContent.theories || [];
            else if (category === 'mechanism') items = categoryContent.mechanisms || [];
            else if (category === 'clinical_case') items = categoryContent.cases || [];
            else if (category === 'event') items = categoryContent.events || [];
            else if (category === 'education') items = categoryContent.education || [];
            
            // En son eklenen içeriği al
            if (items.length > 0) {
              const latestItem = items[0];
              latestItem.category = category;
              latestItem.categoryName = categoryData.name;
              latestItem.categoryColor = categoryData.color || '#4285F4';
              latestItems.push(latestItem);
              
              // Tüm kategoriler tamamlandıysa içerikleri göster
              if (latestItems.length === Object.keys(data.categories).length) {
                displayLatestItems(latestItems);
              }
            }
          })
          .catch(error => console.error(`${category} içeriği yüklenirken hata:`, error));
      }
    })
    .catch(error => console.error('İçerik indeksi yüklenirken hata:', error));
}

// Son eklenen içerikleri göster
function displayLatestItems(items) {
  const latestContentElement = document.getElementById('latest-content');
  if (!latestContentElement) return;
  
  // İçerikleri tarihe göre sırala (en yeni en üstte)
  items.sort((a, b) => {
    const dateA = new Date(a.publication_date || a.start_date || '2000-01-01');
    const dateB = new Date(b.publication_date || b.start_date || '2000-01-01');
    return dateB - dateA;
  });
  
  // En fazla 6 içerik göster
  const displayItems = items.slice(0, 6);
  
  // İçerikleri HTML olarak oluştur
  let html = '';
  
  displayItems.forEach(item => {
    const itemId = item.id || generateUniqueId(item);
    const itemTitle = item.title || 'Başlıksız';
    const itemDesc = item.content || item.description || '';
    const shortDesc = itemDesc.length > 150 ? itemDesc.substring(0, 150) + '...' : itemDesc;
    const itemDate = item.publication_date || item.start_date || '';
    const itemSource = item.source_name || '';
    const itemUrl = `/content/html/${item.category}/${itemId}.html`;
    const categoryColor = item.categoryColor;
    
    html += `
      <div class="content-card">
        <div class="card-header" style="background-color: ${categoryColor};">
          <span class="card-date">${itemDate}</span>
        </div>
        <div class="card-body">
          <h3><a href="${itemUrl}">${itemTitle}</a></h3>
          <p>${shortDesc}</p>
        </div>
        <div class="card-footer">
          <span class="card-source">${itemSource}</span>
          <a href="${itemUrl}" class="read-more">Devamını Oku <i class="fas fa-arrow-right"></i></a>
        </div>
      </div>
    `;
  });
  
  latestContentElement.innerHTML = html;
}

// Benzersiz ID oluştur
function generateUniqueId(content) {
  // Basit bir hash fonksiyonu
  let hash = 0;
  const str = content.title + (content.source_url || content.url || '');
  
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 32bit integer'a dönüştür
  }
  
  return Math.abs(hash).toString(16);
}

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', () => {
  // Ana sayfada son eklenen içerikleri yükle
  if (document.getElementById('latest-content')) {
    loadLatestContent();
  }
});
