const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    ["/chat", "/health", "/rebuild-knowledge-base"],
    createProxyMiddleware({
      target: "http://localhost:8000",
      changeOrigin: true,
      timeout: 120000,
      proxyTimeout: 120000,
    })
  );
};
