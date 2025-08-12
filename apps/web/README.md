# AI App Web (Next.js Frontend)

Modern Next.js frontend for the AI App Bootstrap with TypeScript, TailwindCSS, and Supabase Auth.

## 🚀 Features

- **Next.js 14**: App Router with latest features
- **TypeScript**: Strict type checking throughout
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Auth**: JWT-based authentication
- **Real-time Chat**: Streaming AI responses
- **Responsive Design**: Mobile-first approach
- **Dark Mode**: Built-in theme support
- **Component Library**: Reusable UI components

## 📁 Structure

```
apps/web/
├── app/              # App Router pages
│   ├── globals.css   # Global styles
│   ├── layout.tsx    # Root layout
│   └── page.tsx      # Home page
├── components/       # React components
│   ├── ChatInterface.tsx
│   ├── Header.tsx
│   └── Sidebar.tsx
├── lib/             # Utilities & clients
├── types/           # TypeScript types
└── styles/          # Additional styles
```

## 🛠️ Setup

### Prerequisites

- Node.js 18+
- pnpm 8+
- Supabase project (for auth)

### Installation

```bash
cd apps/web

# Install dependencies
pnpm install

# Set up environment variables
cp ../../env.example .env.local
# Edit .env.local with your configuration

# Start development server
pnpm dev
```

### Environment Variables

```bash
# Supabase Auth
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_WS_URL=ws://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=AI App Bootstrap
NEXT_PUBLIC_APP_VERSION=0.1.0
```

## 🔧 Development

### Available Scripts

```bash
# Development
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm start        # Start production server

# Code Quality
pnpm lint         # Run ESLint
pnpm typecheck    # Run TypeScript checks
pnpm format       # Format code with Prettier

# Testing
pnpm test         # Run unit tests
pnpm test:ui      # Run tests with UI
pnpm test:e2e     # Run E2E tests

# Utilities
pnpm clean        # Clean build artifacts
```

### Development Workflow

1. **Start Development Server**
   ```bash
   pnpm dev
   ```

2. **Open Browser**
   Navigate to `http://localhost:3000`

3. **Hot Reload**
   Changes are automatically reflected in the browser

4. **Type Checking**
   ```bash
   pnpm typecheck
   ```

5. **Linting**
   ```bash
   pnpm lint
   ```

## 🎨 Styling

### TailwindCSS

The project uses TailwindCSS with a custom design system:

- **Colors**: CSS custom properties for theming
- **Components**: Reusable component classes
- **Responsive**: Mobile-first responsive design
- **Dark Mode**: Built-in dark mode support

### Custom CSS

Global styles are defined in `app/globals.css`:

- CSS custom properties for theming
- Component-specific styles
- Utility classes
- Animation definitions

## 🔌 API Integration

### Client SDK

The frontend uses a shared client SDK (`@ai-app/shared`) for API interactions:

```typescript
import { apiClient } from '@ai-app/shared'

// Chat completion
const response = await apiClient.chatCompletion({
  messages: [{ role: 'user', content: 'Hello' }],
  model: 'gpt-3.5-turbo',
})

// Streaming chat
for await (const chunk of apiClient.chatCompletionStream(request)) {
  console.log(chunk)
}
```

### Authentication

Supabase Auth integration:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password',
})
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test --watch

# Run tests with coverage
pnpm test --coverage
```

### E2E Tests

```bash
# Install Playwright browsers
pnpm exec playwright install

# Run E2E tests
pnpm test:e2e

# Run E2E tests in UI mode
pnpm test:e2e --ui
```

### Test Structure

```
__tests__/
├── components/     # Component tests
├── pages/         # Page tests
├── lib/           # Utility tests
└── e2e/           # E2E tests
```

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect Repository**
   - Connect your GitHub repo to Vercel
   - Set environment variables in Vercel dashboard

2. **Deploy**
   - Vercel automatically deploys on push to main
   - Preview deployments for pull requests

3. **Environment Variables**
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=your_api_url
   ```

### Docker

```bash
# Build image
docker build -f infra/docker/Dockerfile.web -t ai-app-web .

# Run container
docker run -p 3000:3000 --env-file .env.local ai-app-web
```

### Other Platforms

- **Netlify**: Similar to Vercel deployment
- **Railway**: Full-stack deployment
- **Fly.io**: Global edge deployment

## 📊 Performance

### Optimization

- **Next.js Image**: Optimized image loading
- **Code Splitting**: Automatic code splitting
- **Bundle Analysis**: Analyze bundle size
- **Lighthouse**: Performance monitoring

### Monitoring

- **Vercel Analytics**: Built-in analytics
- **Error Tracking**: Error monitoring
- **Performance**: Core Web Vitals tracking

## 🔒 Security

### Best Practices

- **Environment Variables**: Sensitive data in env vars
- **CORS**: Proper CORS configuration
- **Content Security Policy**: CSP headers
- **Authentication**: Secure auth flow

### Security Headers

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  }
]
```

## 🤝 Contributing

1. **Fork Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Run Tests**
5. **Submit Pull Request**

### Code Style

- **ESLint**: Code linting rules
- **Prettier**: Code formatting
- **TypeScript**: Strict type checking
- **Conventional Commits**: Commit message format

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

## 🆘 Support

- Check the [main README](../../README.md) for project overview
- Open an issue for bugs or feature requests
- Join our community discussions
