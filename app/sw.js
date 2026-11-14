// 서비스 워커: 홈 화면에 설치한 뒤 인터넷이 없어도 열리게 한다.
// - 첫 화면(index.html)은 네트워크 먼저(항상 최신 데이터), 4초 안에 못 받거나 오프라인이면 저장본.
// - 그 밖의 자원(아이콘, jsDelivr의 Pretendard 글꼴)은 저장본을 먼저 주고 뒤에서 새로 받는다.
// 캐시는 같은 주소(github.io)의 다른 사이트와 함께 쓰이므로 이름 앞머리 'matrix-'인 것만 지운다.
const CACHE = 'matrix-v2';
const HOME = new URL('./', self.registration.scope).href;
const SHELL = [HOME, 'manifest.webmanifest', 'icons/icon-192.png', 'ios-hint.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => Promise.allSettled(SHELL.map(u => c.add(new Request(u, { cache: 'reload' })))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('matrix-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const put = (key, res) => {
  if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)); }
  return res;
};

self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || (u.origin !== location.origin && u.hostname !== 'cdn.jsdelivr.net')) return; // 같은 주소와 글꼴(jsDelivr)만 저장
  if (r.mode === 'navigate') {
    e.respondWith((async () => {
      const cached = await caches.match(HOME, { cacheName: CACHE });
      const net = fetch(r).then(res => put(HOME, res));
      if (!cached) return net;
      const late = new Promise(ok => setTimeout(ok, 4000, cached));
      return Promise.race([net.catch(() => cached), late]);
    })());
    return;
  }
  e.respondWith((async () => {
    const cached = await caches.match(r, { cacheName: CACHE });
    const net = fetch(r).then(res => put(r, res));
    if (cached) { e.waitUntil(net.catch(() => {})); return cached; }
    return net;
  })());
});
