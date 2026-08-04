export default async function handler(req, res) {
  // Set CORS headers to allow requests from any origin/browser
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxao38I7sKqWtCHOHMB4TzHZRSa42v7OXoOFSdLdse5SsLdEedfO2oib5wD64XdDErTnw/exec';

  try {
    if (req.method === 'GET') {
      const googleRes = await fetch(GOOGLE_SCRIPT_URL, { cache: 'no-store' });
      const data = await googleRes.json();
      return res.status(200).json(data);
    } 
    
    if (req.method === 'POST') {
      const bodyData = typeof req.body === 'string' ? req.body : JSON.stringify(req.body || {});
      const googleRes = await fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: bodyData
      });
      const data = await googleRes.json();
      return res.status(200).json(data);
    }
  } catch (err) {
    console.error('Vercel Sheet Proxy Error:', err);
    return res.status(500).json({ status: 'error', message: err.message });
  }

  return res.status(405).json({ status: 'error', message: 'Method not allowed' });
}
