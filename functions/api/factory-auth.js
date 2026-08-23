export async function onRequest(context) {
  const target = new URL('/api/factory-auth', 'https://golden-reference.vercel.app');
  const headers = new Headers();
  const adminKey = context.request.headers.get('X-Factory-Admin-Key');
  if (adminKey) headers.set('X-Factory-Admin-Key', adminKey);
  const response = await fetch(target, { method: 'GET', headers, redirect: 'manual' });
  const out = new Response(response.body, { status: response.status, headers: new Headers(response.headers) });
  const cookie = response.headers.get('Set-Cookie');
  if (cookie) out.headers.set('Set-Cookie', cookie);
  out.headers.set('Cache-Control', 'no-store');
  return out;
}
