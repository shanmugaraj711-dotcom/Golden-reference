const BACKEND = 'https://golden-reference.vercel.app';

export async function onRequest(context) {
  const incoming = new URL(context.request.url);
  const path = incoming.pathname.replace(/^\/api/, '') || '/';
  const target = new URL(path + incoming.search, BACKEND);

  const headers = new Headers(context.request.headers);
  headers.delete('host');
  headers.set('x-forwarded-host', incoming.host);
  headers.set('x-forwarded-proto', incoming.protocol.replace(':', ''));

  const init = {
    method: context.request.method,
    headers,
    redirect: 'manual',
  };

  if (context.request.method !== 'GET' && context.request.method !== 'HEAD') {
    init.body = context.request.body;
  }

  const upstream = await fetch(target.toString(), init);
  const responseHeaders = new Headers(upstream.headers);

  // The upstream API sets a host-only HTTP-only session cookie. Returning the
  // Set-Cookie header through this same-origin proxy makes the browser store it
  // for golden-reference.pages.dev, so later /api calls carry the session.
  responseHeaders.delete('content-encoding');
  responseHeaders.delete('content-length');

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders,
  });
}
