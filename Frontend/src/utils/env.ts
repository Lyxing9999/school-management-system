export const isDev = import.meta.dev;
export const isProd = process.env.NODE_ENV === "production";

export const isClient = import.meta.client;
export const isServer = import.meta.server;
