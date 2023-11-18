# Choose-a-RAG

## After cloning the repo

```bash
npm i
poetry shell
poetry install
```

## Run it

```bash
# Start a shell to continuously build the frontend code
npm run watch
# Start a shell to continuously build and serve the backend code
make start
```

If you find a stale job occupying the backend port, kill it with this:

```bash
make kill-server
```

## Starting from scratch

### Client-side setup

```bash
npm init
npm i -D typescript
npx tsc --init
npm i -D gts
# Answer yes to write into package.json and tsconfig.json.
npx gts init
npm i -D parcel

npm i rxjs
npm i showdown
npm i -D @types/showdown
npm i vector-storage
```

Add these to `package.json`:

```json
  "source": "index.html",
  "scripts": {
    "watch": "npx parcel watch",
  },
  "type": "module",
```

Remove `main` field.

Change these in `tsconfig.json`:

```json
  "compilerOptions": {
    "rootDir": "src",
    "outDir": "build",
    "target": "esnext",
    "lib": ["dom"],
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "inlineSources": true,
    "experimentalDecorators": true,
  },
  "include": ["src/**/*.ts", "test/**/*.ts"],
  "exclude": ["node_modules"],
```

Rename `.prettierrc.js` to `.prettierrc.cjs`, because Prettier cannot import
ESM.

## Server-side setup

```bash
poetry init
poetry add "fastapi[all]" "uvicorn[standard]" httpx pydantic
poetry add git+https://github.com/pikalaw/llama_index.git#managed_index
poetry add  https://storage.googleapis.com/genai-testing-temp/ai-generativelanguage-v1beta-py.tar.gz
poetry add -D mypy
```

## Authorization

You need to do this one-time setup.

Follow this [guide](https://developers.generativeai.google/tutorials/oauth_quickstart) to get a local copy of your `client_secret.json`.
Make sure you enable `Generative Language API (Staging)` API.

Make sure the Application type is Desktop and then wait 5 minutes.

IMPORTANT: There is also the production version `Generative Language API`.
However, that API does not have the retriever endpoints yet!

Then run this command:

```bash
gcloud auth application-default login  --client-id-file=client_secret.json   --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.tuning'
```

NOTE: In the near future, you will need to include the scope `https://www.googleapis.com/auth/generative-language.retriever`.
But for now, you don't need that scope to access the endpoint.
