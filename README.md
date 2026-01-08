# NewsCatcher API Documentation

[![Documentation Status](https://img.shields.io/website?url=https%3A%2F%2Fwww.newscatcherapi.com%2Fdocs)](https://www.newscatcherapi.com/docs)

Documentation repository for the NewsCatcher API, built with
[Mintlify](https://mintlify.com/) and hosted at
[newscatcherapi.com/docs](https://www.newscatcherapi.com/docs).

## Table of Contents

1. [About](#about)
2. [Repository Structure](#repository-structure)
3. [Getting Started](#getting-started)
4. [Contributing](#contributing)
5. [Support](#support)

## About

NewsCatcher API provides access to news articles from over 90,000 sources
worldwide with three main public APIs:

- **News API**: Search and retrieve news articles with metadata enrichment
  and NLP.
- **Local News API**: Hyper local news with geographic detection and NLP.
- **CatchAll API**: AI web search that finds real-world events and extracts
  structured data.

NLP featues include summarisation, topic modeling, sentiment analysis, entity
recognition, clustering, and deduplication.

## Repository Structure

```txt
├── docs.json                   # Mintlify configuration
├── v2/                         # News API v2 (legacy - no longer supported)
├── v3/                         # Current API documentation
│   ├── api-reference/          # News API endpoints and SDKs
│   ├── documentation/          # News API guides and concepts
│   ├── local-news/             # Local News API documentation
│   └── catch-all/              # CatchAll API documentation
├── .github/workflows/          # Automation workflows
└── ...                         # Maintenance scripts
```

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python 3.10+ (for automation scripts)
- Git

### Local Development

1. **Clone and install Mintlify**:

   ```bash
   git clone https://github.com/NewscatcherAPI/docs
   cd docs
   npm i -g mint
   ```

2. **Start development server**:

   ```bash
   mint dev
   ```

3. **View documentation** at `http://localhost:3000`

### Quick API Example

```bash
curl -X GET "https://v3-api.newscatcherapi.com/api/search?q=artificial%20intelligence&lang=en" \
  -H "x-api-token: YOUR_API_KEY"
```

## Contributing

### Documentation Updates

1. Create a new branch: `git checkout -b docs/your-change`
2. Make changes following the
   [Google Developer Documentation Style Guide](https://developers.google.com/style)
3. Test locally: `mint dev`
4. Submit a pull request

### Content Guidelines

- Use clear, concise language for developers
- Include working code examples
- Test all links before submitting
- Follow existing file naming conventions (kebab-case)

### Adding New Pages

1. Update navigation in `docs.json`
2. Create MDX files in appropriate directories
3. For each MDX file, include proper frontmatter (title, sidebarTitle,
   description)

### Common Issues

| Issue                | Solution                                   |
| -------------------- | ------------------------------------------ |
| `mint dev` not found | Install globally: `npm i -g mint`          |
| Port 3000 in use     | Use different port: `mint dev --port 3001` |
| Python script errors | Ensure Python 3.10+ is installed           |

## Support

### Documentation Issues

- **GitHub Issues**: Report documentation bugs and improvements
- **Pull Requests**: Submit fixes and enhancements directly

### API Support

- **Customer Portal**:
  [support.newscatcherapi.com](https://support.newscatcherapi.com/customer-portal)
- **Email**: [support@newscatcherapi.com](mailto:support@newscatcherapi.com)
- **Status Page**:
  [status.newscatcherapi.com](https://status.newscatcherapi.com)

## Resources

- [NewsCatcher API homepage](https://www.newscatcherapi.com)
- [Book a demo](https://www.newscatcherapi.com/book-a-demo)
- [Postman collections](https://www.postman.com/newscatcherapi/newscatcher-public-workspace/overview)

---

Built by the NewsCatcher team with ❤️
