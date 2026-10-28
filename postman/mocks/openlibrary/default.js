const http = require('http');
// Contrato público: https://openlibrary.org/dev/docs/api/search y /dev/docs/api/books.
http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  res.setHeader('Content-Type', 'application/json');
  if (url.pathname === '/search.json') {
    if (url.searchParams.get('q') === 'upstream-error') {
      res.writeHead(503); return res.end(JSON.stringify({ error: 'Service unavailable' }));
    }
    return res.end(JSON.stringify({ docs: [{ key: '/works/OL45804W', title: 'Fantastic Mr. Fox', author_name: ['Roald Dahl'], first_publish_year: 1970 }] }));
  }
  if (url.pathname === '/works/OL45804W.json') return res.end(JSON.stringify({ title: 'Fantastic Mr. Fox', key: '/works/OL45804W' }));
  if (url.pathname.startsWith('/works/')) {
    res.writeHead(404); return res.end(JSON.stringify({ error: 'Not found' }));
  }
  res.writeHead(501); res.end(JSON.stringify({ error: 'Not modeled' }));
}).listen(process.env.PORT);
