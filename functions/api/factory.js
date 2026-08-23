async function proxy(request) {
  const url = new URL(request.url);
  const target = new URL('/api/factory' + url.search, 'https://golden-reference.vercel.app');
  const headers = new Headers(request.headers);
  const body = request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.arrayBuffer();
  const response = await fetch(target, { method: request.method, headers, body, redirect: 'manual' });
  const outHeaders = new Headers(response.headers);
  outHeaders.set('Cache-Control', 'no-store');
  return new Response(response.body, { status: response.status, headers: outHeaders });
}
export const onRequestGet = proxy;
export const onRequestPost = proxy;
