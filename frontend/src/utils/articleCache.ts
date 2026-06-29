import type { Article } from "../types/article"

/* Just last seen article saved in cache, 
and the previous 3, and next 5 articles.
When user refreshes, we grab these 9 
articles from cache, while the user goes 
through them, fresh articles come from 
the get /articles endpoint and appended to the list.*/

const CACHE_KEY = "techcards-reading-state"

export function saveReadingState(
  articles: Article[],
  currentIndex: number
) {

  const start = Math.max(
    0,
    currentIndex - 3
  )

  const end = Math.min(
    articles.length,
    currentIndex + 6
  )

  const cachedArticles =
    articles.slice(start, end)

  localStorage.setItem(
    CACHE_KEY,
    JSON.stringify({
      currentArticleId:
        articles[currentIndex]?.id,
      articles: cachedArticles,
      timestamp: Date.now()
    })
  )
}

export function getReadingState() {

  const cached =
    localStorage.getItem(CACHE_KEY)

  if (!cached) return null

  return JSON.parse(cached)
}

const READ_IDS_KEY = "techcards-read-article-ids"

export function getReadArticleIds(): number[] {
  const cached = localStorage.getItem(READ_IDS_KEY)
  if (!cached) return []
  try {
    return JSON.parse(cached)
  } catch {
    return []
  }
}

export function markArticleAsRead(articleId: number) {
  const ids = getReadArticleIds()
  if (!ids.includes(articleId)) {
    ids.push(articleId)
    // Limit to last 1000 items to avoid localStorage bloat
    if (ids.length > 1000) {
      ids.shift()
    }
    localStorage.setItem(READ_IDS_KEY, JSON.stringify(ids))
  }
}