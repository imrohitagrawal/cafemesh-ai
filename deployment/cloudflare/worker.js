const ORIGIN = "https://cafemesh-ai-lbqubrb5jq-el.a.run.app";

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    const upstream = new URL(ORIGIN);
    upstream.pathname = incoming.pathname;
    upstream.search = incoming.search;
    return fetch(new Request(upstream, request));
  },
};
