# Deployment Guide - Nuclear Biology Reviews

This guide covers deployment options for the Nuclear Biology Reviews website across multiple hosting platforms.

## 📋 Table of Contents

1. [GitHub Pages (Recommended)](#github-pages)
2. [Netlify](#netlify)
3. [Vercel](#vercel)
4. [Local Development](#local-development)
5. [Custom Server](#custom-server)
6. [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 GitHub Pages (Recommended)

GitHub Pages is the recommended hosting solution for this academic research website.

### Automatic Deployment

1. **Fork or create repository:**
   ```bash
   git clone https://github.com/nuclear-biology/reviews.git
   cd reviews
   ```

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main` / `root`
   - Click "Save"

4. **Access your site:**
   - URL: `https://yourusername.github.io/repository-name`
   - Custom domain supported via CNAME

### Manual Deployment with GitHub Actions

The repository includes automated GitHub Actions workflow (`.github/workflows/deploy.yml`):

- **Triggers:** Push to main/master branch
- **Features:** HTML validation, CSS/JS linting, automated deployment
- **Requirements:** Enable Pages in repository settings

---

## 🌐 Netlify

### Option 1: Git Integration (Recommended)

1. **Connect to Netlify:**
   - Visit [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository

2. **Build Settings:**
   - Build command: `npm run build`
   - Publish directory: `.` (root directory)
   - No build process needed (static site)

3. **Deploy:**
   - Automatic deployment on git push
   - Preview deployments for pull requests

### Option 2: Manual Deploy

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy site
netlify deploy --dir=. --prod
```

### Netlify Configuration

Create `netlify.toml`:
```toml
[build]
  publish = "."
  command = "echo 'No build command needed'"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

---

## ⚡ Vercel

### Option 1: Git Integration

1. **Connect to Vercel:**
   - Visit [vercel.com](https://vercel.com)
   - Import your GitHub repository

2. **Configuration:**
   - Framework: Other
   - Build command: (leave empty)
   - Output directory: `.`

### Option 2: CLI Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Vercel Configuration

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

---

## 💻 Local Development

### Prerequisites

- Python 3.x or Node.js
- Modern web browser

### Python Server

```bash
# Python 3
python -m http.server 8000

# Python 2
python -SimpleHTTPServer 8000

# Access at: http://localhost:8000
```

### Node.js Server

```bash
# Install dependencies
npm install

# Start server
npm start

# Or use npx
npx serve .
```

### Alternative Servers

```bash
# Live Server (VSCode extension or CLI)
npm install -g live-server
live-server

# PHP Server
php -S localhost:8000

# Ruby Server
ruby -run -e httpd . -p 8000
```

---

## 🖥️ Custom Server

### Apache Configuration

Create `.htaccess`:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [QSA,L]

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache control
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name nuclear-biology.com;
    root /var/www/nuclear-biology-reviews;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
}
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM nginx:alpine

# Copy website files
COPY . /usr/share/nginx/html

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Commands

```bash
# Build image
docker build -t nuclear-biology-reviews .

# Run container
docker run -d -p 80:80 nuclear-biology-reviews

# Docker Compose
docker-compose up -d
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
```

---

## 🔧 Troubleshooting

### Common Issues

1. **404 Errors on Review Pages**
   - Ensure all 70 review files are in `/reviews/` directory
   - Check file naming (must be kebab-case)
   - Verify links in `index.html`

2. **Styles Not Loading**
   - Check CSS file path: `assets/css/styles.css`
   - Verify server mime types support CSS

3. **Search Not Working**
   - Ensure JavaScript is enabled
   - Check browser console for errors
   - Verify `assets/js/main.js` is loading

4. **GitHub Pages Build Failures**
   - Check GitHub Actions logs
   - Verify `package.json` dependencies
   - Ensure valid HTML/CSS syntax

### Performance Optimization

1. **Enable Compression:**
   - Gzip for text files
   - Image optimization
   - Minify CSS/JS

2. **Cache Headers:**
   - Set appropriate cache control
   - Use browser caching
   - CDN integration

3. **Security Headers:**
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline';
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   X-XSS-Protection: 1; mode=block
   ```

### Debug Commands

```bash
# Check HTML validity
npm run validate

# Lint CSS
npm run lint-css

# Lint JavaScript  
npm run lint-js

# Check broken links
npm run check-links

# Performance audit
npm run lighthouse
```

---

## 📊 Monitoring & Analytics

### Google Analytics Integration

1. Get tracking ID from Google Analytics
2. Update `_config.yml`:
   ```yaml
   google_analytics: G-XXXXXXXXXX
   ```

### Search Console

1. Verify site ownership
2. Submit sitemap: `/sitemap.xml`
3. Monitor search performance

---

## 🔒 Security Considerations

1. **HTTPS Only:** Use secure connections
2. **Content Security Policy:** Prevent XSS attacks
3. **Regular Updates:** Keep dependencies current
4. **Backup Strategy:** Regular repository backups

---

## 📈 SEO Optimization

1. **Sitemap:** Automatically generated by Jekyll
2. **Meta Tags:** Included in all pages  
3. **Structured Data:** Consider adding JSON-LD
4. **Page Speed:** Optimize for Core Web Vitals

---

## 🤝 Support

For deployment issues:
1. Check this guide first
2. Review GitHub Issues
3. Consult platform-specific documentation
4. Open an issue in the repository

---

**Last Updated:** 2024
**Version:** 1.0.0