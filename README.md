# chatgpt-assistant

## Client-side setup

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
    "start": "npx parcel -p 8000",
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
python3 -m venv .venv
source .venv/bin/activate

# mypy.
python3 -m pip install mypy

# FastAPI.
python3 -m pip install "fastapi[all]" "uvicorn[standard]" httpx
```
