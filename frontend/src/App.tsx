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
  const [scale, setScale] = useState(1)

  /* SCALE CARDS PROPORTIONALLY ON SMALLER VIEWPORTS */
  useEffect(() => {
    function handleResize() {
      const containerWidth = 662.61
      const padding = 32 // 16px padding on each side
      const availableWidth = window.innerWidth - padding
      if (availableWidth < containerWidth) {
        setScale(availableWidth / containerWidth)
      } else {
        setScale(1)
      }
    }
    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [offset, setOffset] = useState(0)
  const [isFetchingMore, setIsFetchingMore] = useState(false)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  /* TRANSITION AND PHYSICAL RIBBON DECK STATES */
  const [currentIndex, setCurrentIndex] = useState(0)
  const [displayIndex, setDisplayIndex] = useState(0)
  const [translateStyle, setTranslateStyle] = useState({ transform: `scale(${scale}) translate3d(0, 0, 0)` })
  const [transitionEnabled, setTransitionEnabled] = useState(true)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [activeSlot, setActiveSlot] = useState<1 | 2 | 3>(2)

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

  /* Update scale factor dynamically when layout bounds resize */
  useEffect(() => {
    setTranslateStyle({ transform: `scale(${scale}) translate3d(0, 0, 0)` })
  }, [scale])

  /* Sync displayIndex with initial load */
  useEffect(() => {
    if (articles.length > 0) {
      setDisplayIndex(currentIndex)
    }
  }, [articles])

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
    setTransitionEnabled(true) // 1. Enable transitions first
    setActiveSlot(3) // Slide Slot 3 (Right/Bottom) to center, scale it up!

    const containerWidth = 662.61
    const gap = 32 // 2rem
    const isMobile = window.innerWidth < 768

    // Measure actual DOM heights dynamically if vertical mobile
    let travelDistance = containerWidth + gap // default for desktop (662.61 + 32 = 694.61)
    if (isMobile) {
      const activeHeight = document.getElementById("slot-2")?.clientHeight || 662.61
      const nextHeight = document.getElementById("slot-3")?.clientHeight || 662.61
      travelDistance = activeHeight / 2 + gap + nextHeight / 2
    }

    // 2. Wait 20ms for browser to register transitionEnabled, then slide!
    setTimeout(() => {
      if (isMobile) {
        setTranslateStyle({ transform: `scale(${scale}) translate3d(0, ${-travelDistance}px, 0)` })
      } else {
        setTranslateStyle({ transform: `scale(${scale}) translate3d(${-travelDistance}px, 0, 0)` })
      }

      // 3. Once the 350ms slide finishes, instantly disable transitions
      setTimeout(() => {
        setTransitionEnabled(false) // Disable transitions first!

        // 4. Wait 30ms (2 paint frames) to ensure transition: none is committed before resetting transforms
        setTimeout(() => {
          const nextIndex = currentIndex + 1
          setCurrentIndex(nextIndex)
          setDisplayIndex(nextIndex)
          setTranslateStyle({ transform: `scale(${scale}) translate3d(0, 0, 0)` })
          setActiveSlot(2) // Snap back to Center slot (Slot 2)
          setIsTransitioning(false)
        }, 30)
      }, 350)
    }, 20)
  }

  function handlePrevious() {
    if (isTransitioning || currentIndex <= 0) return

    setIsTransitioning(true)
    setTransitionEnabled(true) // 1. Enable transitions first
    setActiveSlot(1) // Slide Slot 1 (Left/Top) to center, scale it up!

    const containerWidth = 662.61
    const gap = 32 // 2rem
    const isMobile = window.innerWidth < 768

    // Measure actual DOM heights dynamically if vertical mobile
    let travelDistance = containerWidth + gap // default for desktop (662.61 + 32 = 694.61)
    if (isMobile) {
      const activeHeight = document.getElementById("slot-2")?.clientHeight || 662.61
      const prevHeight = document.getElementById("slot-1")?.clientHeight || 662.61
      travelDistance = activeHeight / 2 + gap + prevHeight / 2
    }

    // 2. Wait 20ms for browser to register transitionEnabled, then slide!
    setTimeout(() => {
      if (isMobile) {
        setTranslateStyle({ transform: `scale(${scale}) translate3d(0, ${travelDistance}px, 0)` })
      } else {
        setTranslateStyle({ transform: `scale(${scale}) translate3d(${travelDistance}px, 0, 0)` })
      }

      // 3. Once the 350ms slide finishes, instantly disable transitions
      setTimeout(() => {
        setTransitionEnabled(false) // Disable transitions first!

        // 4. Wait 30ms (2 paint frames) to ensure transition: none is committed before resetting transforms
        setTimeout(() => {
          const prevIndex = currentIndex - 1
          setCurrentIndex(prevIndex)
          setDisplayIndex(prevIndex)
          setTranslateStyle({ transform: `scale(${scale}) translate3d(0, 0, 0)` })
          setActiveSlot(2) // Snap back to Center slot (Slot 2)
          setIsTransitioning(false)
        }, 30)
      }, 350)
    }, 20)
  }

  if (loading) {
    return (
      <div className="p-10 text-3xl">
        Loading...
      </div>
    )
  }

  // Helper to dynamically calculate stable responsive styles for Left, Center, and Right previews
  const getSlotStyle = (offsetVal: number) => {
    const isMobile = window.innerWidth < 768

    if (offsetVal === 0) {
      return {
        position: "relative" as const,
        width: "100%",
      }
    }

    if (isMobile) {
      return {
        position: "absolute" as const,
        left: "50%",
        transform: "translate3d(-50%, 0, 0)",
        top: offsetVal === 1 ? "calc(100% + 32px)" : "auto",
        bottom: offsetVal === -1 ? "calc(100% + 32px)" : "auto",
      }
    } else {
      return {
        position: "absolute" as const,
        top: "50%",
        transform: "translate3d(0, -50%, 0)",
        left: offsetVal === 1 ? "calc(100% + 32px)" : "auto",
        right: offsetVal === -1 ? "calc(100% + 32px)" : "auto",
      }
    }
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
            overflow-x-hidden
            pb-4
          "
        >

          {/* MAIN CARD & PREVIEWS WRAPPER (SLIDES AS A DYNAMIC PERCENTAGE RIBBON) */}
          <div
            className="relative z-10 w-[var(--container-width)] min-h-[var(--container-height)] h-fit flex items-center justify-center"
            style={{
              ...translateStyle,
              transformOrigin: "center center",
              transition: transitionEnabled ? "transform 350ms cubic-bezier(0.25, 1, 0.5, 1)" : "none",
            }}
          >
            {(() => {
              const idx2 = displayIndex
              if (idx2 < 0 || idx2 >= articles.length) return null
              const article2 = articles[idx2]

              return (
                <div
                  id="slot-2"
                  key={article2.id}
                  className="
                    absolute
                    w-full
                    max-w-[var(--container-width)]
                    flex
                    justify-center
                    pointer-events-auto
                  "
                  style={getSlotStyle(0)}
                >
                  {/* Active Article Card */}
                  <ArticleCard
                    article={article2}
                    isPreview={activeSlot !== 2}
                    onNext={handleNext}
                    onPrevious={handlePrevious}
                  />

                  {/* Left / Top Preview (Slot 1) */}
                  {(() => {
                    const idx1 = displayIndex - 1
                    if (idx1 < 0 || idx1 >= articles.length) return null
                    const article1 = articles[idx1]

                    return (
                      <div
                        id="slot-1"
                        key={article1.id}
                        className="
                          absolute
                          w-full
                          max-w-[var(--container-width)]
                          flex
                          justify-center
                          pointer-events-none
                        "
                        style={getSlotStyle(-1)}
                      >
                        <ArticleCard
                          article={article1}
                          isPreview={activeSlot !== 1}
                        />
                      </div>
                    )
                  })()}

                  {/* Right / Bottom Preview (Slot 3) */}
                  {(() => {
                    const idx3 = displayIndex + 1
                    if (idx3 < 0 || idx3 >= articles.length) return null
                    const article3 = articles[idx3]

                    return (
                      <div
                        id="slot-3"
                        key={article3.id}
                        className="
                          absolute
                          w-full
                          max-w-[var(--container-width)]
                          flex
                          justify-center
                          pointer-events-none
                        "
                        style={getSlotStyle(1)}
                      >
                        <ArticleCard
                          article={article3}
                          isPreview={activeSlot !== 3}
                        />
                      </div>
                    )
                  })()}
                </div>
              )
            })()}
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