const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
if (!fs.existsSync(src)) {
  console.error('frontend/dist not found. Did you run npm run build?');
  process.exit(1);
}
console.log('Build present:', src);
