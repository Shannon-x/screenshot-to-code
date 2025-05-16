# screenshot-to-code

A simple tool to convert screenshots, mockups and Figma designs into clean, functional code using AI. Now supporting Claude Sonnet 3.7!

https://github.com/abi/screenshot-to-code/assets/23818/6cebadae-2fe3-4986-ac6a-8fb9db030045

Supported stacks:

- HTML + Tailwind
- HTML + CSS
- React + Tailwind
- Vue + Tailwind
- Bootstrap
- Ionic + Tailwind
- SVG

Supported AI models:

- Claude Sonnet 3.7 - Best model!
- GPT-4o - also recommended!
- DALL-E 3 or Flux Schnell (using Replicate) for image generation

See the [Examples](#-examples) section below for more demos.

We also just added experimental support for taking a video/screen recording of a website in action and turning that into a functional prototype.

![google in app quick 3](https://github.com/abi/screenshot-to-code/assets/23818/8758ffa4-9483-4b9b-bb66-abd6d1594c33)

[Learn more about video here](https://github.com/abi/screenshot-to-code/wiki/Screen-Recording-to-Code).

[Follow me on Twitter for updates](https://twitter.com/_abi_).

## 🌍  Hosted Version

[Try it live on the hosted version (paid)](https://screenshottocode.com).

## 🛠 Getting Started

The app has a React/Vite frontend and a FastAPI backend.

Keys needed:

- [OpenAI API key with access to GPT-4](https://github.com/abi/screenshot-to-code/blob/main/Troubleshooting.md) or Anthropic key (optional)
- Both are recommended so you can compare results from both Claude and GPT4o

If you'd like to run the app with Ollama open source models (not recommended due to poor quality results), [follow this comment](https://github.com/abi/screenshot-to-code/issues/354#issuecomment-2435479853).

Run the backend (I use Poetry for package management - `pip install poetry` if you don't have it):

```bash
cd backend
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "ANTHROPIC_API_KEY=your-key" > .env
poetry install
poetry shell
poetry run uvicorn main:app --reload --port 7001
```
You can also set up the keys using the settings dialog on the front-end (click the gear icon after loading the frontend).

Run the frontend:

```bash
cd frontend
yarn
yarn dev
```

Open http://localhost:5173 to use the app.

If you prefer to run the backend on a different port, update VITE_WS_BACKEND_URL in `frontend/.env.local`

For debugging purposes, if you don't want to waste GPT4-Vision credits, you can run the backend in mock mode (which streams a pre-recorded response):

```bash
MOCK=true poetry run uvicorn main:app --reload --port 7001
```

## Docker

If you have Docker installed on your system, in the root directory, run:

```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
docker-compose up -d --build
```

The app will be up and running at http://localhost:5173. Note that you can't develop the application with this setup as the file changes won't trigger a rebuild.

## 🙋‍♂️ FAQs

- **I'm running into an error when setting up the backend. How can I fix it?** [Try this](https://github.com/abi/screenshot-to-code/issues/3#issuecomment-1814777959). If that still doesn't work, open an issue.
- **How do I get an OpenAI API key?** See https://github.com/abi/screenshot-to-code/blob/main/Troubleshooting.md
- **How can I configure an OpenAI proxy?** - If you're not able to access the OpenAI API directly (due to e.g. country restrictions), you can try a VPN or you can configure the OpenAI base URL to use a proxy: Set OPENAI_BASE_URL in the `backend/.env` or directly in the UI in the settings dialog. Make sure the URL has "v1" in the path so it should look like this: `https://xxx.xxxxx.xxx/v1`
- **How can I update the backend host that my front-end connects to?** - Configure VITE_HTTP_BACKEND_URL and VITE_WS_BACKEND_URL in front/.env.local For example, set VITE_HTTP_BACKEND_URL=http://124.10.20.1:7001
- **Seeing UTF-8 errors when running the backend?** - On windows, open the .env file with notepad++, then go to Encoding and select UTF-8.
- **How can I provide feedback?** For feedback, feature requests and bug reports, open an issue or ping me on [Twitter](https://twitter.com/_abi_).

## 🔧 Environment Variables Configuration

Before running the app, you need to configure two environment files:

1. **Backend** (`.env` in `/backend`):
   ```bash
   # Copy example and edit
   cp .env.example .env

   # .env (backend)
   OPENAI_API_KEY=sk-your-openai-key        # 必填：OpenAI API Key
   ANTHROPIC_API_KEY=an-your-anthropic-key   # 可选：Anthropic API Key
   OPENAI_BASE_URL=https://api.openai.com/v1  # 可选：自定义 OpenAI Base URL
   REPLICATE_API_KEY=rp-your-replicate-key   # 可选：Replicate API Key
   MOCK=false                                # 可选：mock 模式
   ```
   Replace `sk-your-openai-key` and other values with your actual credentials.

2. **Frontend** (`.env.local` in `/frontend`):
   ```bash
   # Copy example and edit
   cp .env.example .env.local

   # .env.local (frontend)
   # 如果前端部署在 a.com，后端位于 1.2.3.4:7001
   VITE_HTTP_BACKEND_URL=http://1.2.3.4:7001
   VITE_WS_BACKEND_URL=ws://1.2.3.4:7001
   VITE_IS_DEPLOYED=false   # 若前端通过 HTTPS (如 https://a.com) 提供，则设置为 true
   ```
   - `VITE_HTTP_BACKEND_URL`：后端 HTTP API 地址（示例：`http://<IP>:<PORT>`）
   - `VITE_WS_BACKEND_URL`：后端 WebSocket 地址（示例：`ws://<IP>:<PORT>`）
   - `VITE_IS_DEPLOYED`：如果你的前端 `a.com` 使用 HTTPS，设置为 `true`，客户端会自动改为 `wss://`。

After configuring these files, restart both the backend (`poetry run uvicorn ...`) and the frontend (`yarn dev`).

## 📚 Examples

**NYTimes**

| Original                                                                                                                                                        | Replica                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <img width="1238" alt="Screenshot 2023-11-20 at 12 54 03 PM" src="https://github.com/abi/screenshot-to-code/assets/23818/3b644dfa-9ca6-4148-84a7-3405b6671922"> | <img width="1414" alt="Screenshot 2023-11-20 at 12 59 56 PM" src="https://github.com/abi/screenshot-to-code/assets/23818/26201c9f-1a28-4f35-a3b1-1f04e2b8ce2a"> |

**Instagram page (with not Taylor Swift pics)**

https://github.com/abi/screenshot-to-code/assets/23818/503eb86a-356e-4dfc-926a-dabdb1ac7ba1

**Hacker News** but it gets the colors wrong at first so we nudge it

https://github.com/abi/screenshot-to-code/assets/23818/3fec0f77-44e8-4fb3-a769-ac7410315e5d
