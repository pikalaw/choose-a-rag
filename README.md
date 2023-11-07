# chatgpt-assistant

## Setup

```bash
npm init
npm i -D typescript
npx tsc --init
npm i -D gts
# Answer yes to write into package.json and tsconfig.json.
npx gts init
npm i -D parcel

npm i showdown
npm i -D @types/showdown
npm i vector-storage
npm i openai
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
    "module": "esnext",
    "moduleResolution": "nodenext",
    "inlineSources": true,
    "experimentalDecorators": true,
  },
  "include": ["src/**/*.ts", "test/**/*.ts"],
  "exclude": ["node_modules"],
```

Rename `.prettierrc.js` to `.prettierrc.cjs`, because Prettier cannot import
ESM.
