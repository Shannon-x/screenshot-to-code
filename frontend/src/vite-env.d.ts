/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_IS_DEPLOYED?: string;
  readonly VITE_WS_BACKEND_URL?: string;
  readonly VITE_HTTP_BACKEND_URL?: string;
  readonly VITE_PICO_BACKEND_FORM_SECRET?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
