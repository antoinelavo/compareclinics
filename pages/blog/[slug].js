// pages/blog/[slug].js
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import Head from 'next/head'
import BlogCTAButton from '@/components/BlogCTAButton'
import { unified } from 'unified'
import remarkParse from 'remark-parse'
import remarkGfm from 'remark-gfm'
import remarkRehype from 'remark-rehype'
import rehypeSlug from 'rehype-slug'
import rehypeStringify from 'rehype-stringify'
import { visit } from 'unist-util-visit'

const BLOG_DIR = path.join(process.cwd(), 'content/blog')

function getHeadings(markdown) {
  const tree = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeSlug)
    .parse(markdown)

  const headings = []
  visit(tree, 'heading', (node) => {
    if (node.depth === 1 || node.depth === 2) {
      const text = node.children
        .filter(c => c.type === 'text' || c.type === 'inlineCode')
        .map(c => c.value)
        .join('')
      const id =
        node.data?.hProperties?.id ||
        text.toLowerCase().replace(/\s+/g, '-')
      headings.push({ text, depth: node.depth, id })
    }
  })
  return headings
}

export async function getStaticPaths() {
  const files = fs.readdirSync(BLOG_DIR).filter(f => f.endsWith('.mdx'))
  return {
    paths: files.map(f => ({ params: { slug: f.replace(/\.mdx$/, '') } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const fullPath = path.join(BLOG_DIR, `${params.slug}.mdx`)
  const source = fs.readFileSync(fullPath, 'utf8')
  const { data, content } = matter(source)

  // 1. Turn markdown/MDX into an HTML string
  const file = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeSlug)
    .use(rehypeStringify)
    .process(content)

  const mdxHtml = String(file)

  // 2. Extract H1/H2 for TOC
  const toc = getHeadings(content)

  return {
    props: {
      frontmatter: data,
      mdxHtml,
      toc,
    },
  }
}

export default function BlogPost({ frontmatter, mdxHtml, toc }) {
  return (
    <>
      <Head>
        <title>{frontmatter.title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="robots" content="index, follow" />
        <link rel="icon" href="/images/favicon.ico" />
        <meta name="description" content={frontmatter.description} />
        <meta property="og:type" content="article" />
        <meta property="og:title" content={frontmatter.title} />
        <meta property="og:description" content={frontmatter.description} />
        <meta
          property="og:image"
          content={frontmatter.coverImage || '/images/mainlogo.png'}
        />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={frontmatter.title} />
        <meta name="twitter:description" content={frontmatter.description} />
        <meta
          name="twitter:image"
          content={frontmatter.coverImage || '/images/mainlogo.svg'}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Article",
              headline: frontmatter.title,
              description: frontmatter.description,
              datePublished: frontmatter.date,
              author: { "@type": "Person", name: "Compare Clinics" },
              publisher: {
                "@type": "Organization",
                name: "Compare Clinics",
                logo: { "@type": "ImageObject" },
              },
            }),
          }}
        />
      </Head>

      <div className="max-w-5xl mx-auto py-16 px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* — Main article */}
        <article className="md:col-span-3">
          {/* Mobile CTA */}
          {frontmatter.ctaDescription &&
            frontmatter.ctaLabel &&
            frontmatter.ctaLink && (
              <div className="md:hidden max-w-[20em] mx-auto flex flex-col items-center text-center bg-blue-50 rounded-xl p-6 mb-6">
                <p className="font-bold text-black">
                  {frontmatter.ctaDescription}
                </p>
                <BlogCTAButton
                  label={frontmatter.ctaLabel}
                  href={frontmatter.ctaLink}
                />
              </div>
            )}

          {/* Header */}
          <header className="mb-12 text-left">
            <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-gray-900 dark:text-gray-100">
              {frontmatter.title}
            </h1>
            <time className="text-gray-500 text-md mt-2 block">
              {frontmatter.date}
            </time>
          </header>

          {/* Rendered HTML */}
          <div
            className="
              min-h-[80dvh]
              mb-[10em]
              prose
              prose-lg
              lg:prose-xl
              dark:prose-invert
              text-left
              prose-p:leading-relaxed
              prose-h2:text-xl
              prose-h2:font-semibold
              prose-h2:mt-8
              prose-h2:mb-4
              prose-h2:text-gray-900
              prose-h2:scroll-mt-[4em]
              prose-h3:text-lg
              prose-h3:font-semibold
              prose-h3:mt-8
              prose-h3:mb-4
              prose-h3:text-gray-900
              prose-a:text-blue-500
              prose-a:underline-offset-4
              prose-ol:text-[16px]
              prose-ul:text-[16px]
              prose-img:rounded-xl
              prose-img:shadow-lg
              prose-img:border-solid
            "
            dangerouslySetInnerHTML={{ __html: mdxHtml }}
          />
        </article>

        {/* — Sidebar */}
        <aside className="hidden md:block">
          {frontmatter.ctaDescription &&
            frontmatter.ctaLabel &&
            frontmatter.ctaLink && (
              <div className="sticky top-20 flex flex-col items-center text-center bg-blue-50 rounded-xl p-6 mb-6">
                <p className="font-bold text-black text-balance">
                  {frontmatter.ctaDescription}
                </p>
                <BlogCTAButton
                  label={frontmatter.ctaLabel}
                  href={frontmatter.ctaLink}
                />
              </div>
            )}

          <nav className="sticky top-[18em] space-y-2 border-l pl-4">
            <ul className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
              {toc.map(({ text, depth, id }) => (
                <li key={id} className={depth === 2 ? 'ml-4' : ''}>
                  <a
                    href={`#${id}`}
                    className="no-underline hover:underline focus:no-underline visited:no-underline"
                  >
                    {text}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </aside>
      </div>
    </>
  )
}