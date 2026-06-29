import { useEffect, useState } from "react"

import ArticleCard from "./components/ArticleCard"
import BookmarksView from "./components/BookmarksView"

import { fetchArticles } from "./services/api"

import type { Article } from "./types/article"

import Navbar from "./components/Navbar"

import AuthModal from "./components/AuthModal"
import { useAuth } from "./context/authContext"

import { saveReadingState, getReadingState, getReadArticleIds, markArticleAsRead } from "./utils/articleCache"

function App() {
  const { isAuthenticated } = useAuth()

  const [view, setView] = useState<"home" | "bookmarks">("home")

  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [offset, setOffset] = useState(0)
  const [isFetchingMore, setIsFetchingMore] = useState(false)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  /* TRANSITION AND PHYSICAL RIBBON DECK STATES */
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [windowWidth, setWindowWidth] = useState(window.innerWidth)

  useEffect(() => {
    function handleResize() {
      setWindowWidth(window.innerWidth)
    }
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  /* Fetch articles with pagination */
  async function fetchFreshArticles() {
    try {
      const data =
        await fetchArticles(
          0,
          50
        )
      const readIds = new Set(getReadArticleIds())
      setArticles(prev => {
        const existingIds =
          new Set(
            prev.map(
              article => article.id
            )
          )
        const newArticles =
          data.filter(
            article =>
              !existingIds.has(article.id) &&
              !readIds.has(article.id)
          )
        return [
          ...prev,
          ...newArticles
        ]
      })
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  /* Image preloading for upcoming articles */
  useEffect(() => {
    if (articles.length === 0) return
    const nextArticles = articles.slice(currentIndex + 1, currentIndex + 4)
    nextArticles.forEach(article => {
      if (article.image_url) {
        const img = new Image()
        img.src = article.image_url
      }
    })
  }, [currentIndex, articles])



  /* INITIAL LOAD */
  useEffect(() => {
    const cached =
      getReadingState()
    if (
      cached &&
      cached.articles?.length > 0
    ) {
      setArticles(cached.articles)
      const cachedIndex =
        cached.articles.findIndex(
          (article: Article) =>
            article.id ===
            cached.currentArticleId
        )
      setCurrentIndex(
        cachedIndex >= 0
          ? cachedIndex
          : 0
      )
      setLoading(false)
      fetchFreshArticles()
    } else {
      fetchFreshArticles()
    }

  }, [])

  /* REDIRECT TO HOME ON LOGOUT */
  useEffect(() => {
    if (!isAuthenticated && view === "bookmarks") {
      setView("home")
    }
  }, [isAuthenticated, view])

  /* SAVE READING STATE TO CACHE ON ARTICLE CHANGE (for refresh recovery) */
  useEffect(() => {

    if (articles.length === 0) return

    saveReadingState(
      articles,
      currentIndex
    )

    // Mark all preceding articles as read in localStorage
    for (let i = 0; i < currentIndex; i++) {
      markArticleAsRead(articles[i].id)
    }

  }, [currentIndex, articles])

  /* FETCH NEXT 50 ARTICLES */
  async function fetchMoreArticles() {
    /* prevent duplicate requests */
    if (isFetchingMore) {
      return
    }
    try {
      setIsFetchingMore(true)
      const newOffset = offset + 50
      const newArticles = await fetchArticles(
        newOffset,
        50
      )
      const readIds = new Set(getReadArticleIds())
      setArticles(prev => {
        const existingIds = new Set(prev.map(article => article.id))
        const filteredNew = newArticles.filter(
          article => !existingIds.has(article.id) && !readIds.has(article.id)
        )
        return [
          ...prev,
          ...filteredNew
        ]
      })
      setOffset(newOffset)
    } catch (error) {
      console.error(error)
    } finally {
      setIsFetchingMore(false)
    }
  }

  /* PREFETCH WHEN USER NEARS END */
  useEffect(() => {
    if (
      currentIndex >= articles.length - 5
    ) {
      fetchMoreArticles()
    }
  }, [currentIndex])

  /* COORDINATE DECK SWIPE ANIMATIONS (DYNAMIC-HEIGHT PERCENTAGE GLIDE) */
  function handleNext() {
    if (isTransitioning || currentIndex >= articles.length - 1) return

    setIsTransitioning(true)
    setCurrentIndex(prev => prev + 1)
    setTimeout(() => {
      setIsTransitioning(false)
    }, 350)
  }

  function handlePrevious() {
    if (isTransitioning || currentIndex <= 0) return

    setIsTransitioning(true)
    setCurrentIndex(prev => prev - 1)
    setTimeout(() => {
      setIsTransitioning(false)
    }, 350)
  }

  const getCardStyle = (index: number) => {
    const isMobile = windowWidth < 768
    if (isMobile) {
      return {
        position: "absolute" as const,
        left: "50%",
        transform: "translate3d(-50%, 0, 0)",
        top: `calc(${index} * (100% + 24px))`,
      }
    } else {
      return {
        position: "absolute" as const,
        top: "50%",
        transform: "translate3d(0, -50%, 0)",
        left: `${index * 694.61}px`,
      }
    }
  }

  if (loading) {
    return (
      <div className="p-10 text-3xl">
        Loading...
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* NAVBAR */}
      <Navbar
        onOpenAuthModal={() =>
          setIsAuthModalOpen(true)
        }
        onLogoClick={() => {
          setView("home")
        }}
        onBookmarksClick={() => {
          setView(prev => prev === "bookmarks" ? "home" : "bookmarks")
        }}
        activeView={view}
      />

      {view === "bookmarks" ? (
        <BookmarksView
          onLogoClick={() => setView("home")}
        />
      ) : articles.length === 0 ? (
        <div className="p-10 text-4xl">
          No articles found
        </div>
      ) : (
        <div
          className="
            relative
            flex
            flex-1
            items-center
            justify-center
            overflow-hidden
            px-6
            py-6
            md:px-0
            md:py-0
          "
        >

          <div
            className="relative z-10 w-full max-w-[var(--container-width)] h-[calc(100dvh-120px)] md:h-[var(--container-height)] flex items-center justify-center"
            style={{
              transform: windowWidth < 768
                ? `translate3d(0, calc(${-currentIndex} * (100% + 24px)), 0)`
                : `translate3d(${-currentIndex * 694.61}px, 0, 0)`,
              transformOrigin: "center center",
              transition: "transform 350ms cubic-bezier(0.25, 1, 0.5, 1)",
            }}
          >
            {articles.map((article, index) => {
              // Sliding window of currentIndex +/- 2 to optimize performance and prevent dynamic DOM pops
              if (Math.abs(index - currentIndex) > 2) return null

              const isPreview = index !== currentIndex

              return (
                <div
                  key={article.id}
                  id={`slot-${index}`}
                  className={`
                    absolute
                    w-full
                    h-full
                    max-w-[var(--container-width)]
                    flex
                    justify-center
                    ${isPreview ? "pointer-events-none" : "pointer-events-auto"}
                  `}
                  style={getCardStyle(index)}
                >
                  <ArticleCard
                    article={article}
                    isPreview={isPreview}
                    onNext={handleNext}
                    onPrevious={handlePrevious}
                  />
                </div>
              )
            })}
          </div>

        </div>
      )}

      {/* AUTH MODAL */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() =>
          setIsAuthModalOpen(false)
        }
      />
    </div>
  )
}

export default App