Sentry.init({
    dsn: "https://60cdb6007a834f9cb0929c55a4f1bc6a@o996412.ingest.sentry.io/6630137",
    integrations: [new Sentry.BrowserTracing()],
  
    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 1.0,
  });