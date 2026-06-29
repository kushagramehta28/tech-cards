import { useEffect, useState } from "react"
import { X } from "lucide-react"

import ArticleCard from "./ArticleCard"

import { fetchBookmarks, fetchArticle } from "../services/api"

import type { Article } from "../types/article"
import type { BookmarkItem } from "../types/bookmark"
import { useAuth } from "../context/authContext"

interface BookmarksViewProps {
  onLogoClick: () => void
}

export default function BookmarksView({ onLogoClick }: BookmarksViewProps) {
  const { isAuthenticated } = useAuth()

  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)
  const [selectedArticleLoading, setSelectedArticleLoading] = useState(false)
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

  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([])
  const [bookmarksLoading, setBookmarksLoading] = useState(false)
  const [bookmarksError, setBookmarksError] = useState("")

  /* LOAD BOOKMARKS */
  useEffect(() => {
    if (isAuthenticated) {
      async function loadBookmarks() {
        try {
          setBookmarksLoading(true)
          setBookmarksError("")
          const data = await fetchBookmarks()
          setBookmarks(data)
        } catch (error) {
          console.error(error)
          setBookmarksError("Failed to load bookmarks. Please try again.")
        } finally {
          setBookmarksLoading(false)
        }
      }
      loadBookmarks()
    }
  }, [isAuthenticated])

  async function handleOpenArticle(articleId: number) {
    try {
      setSelectedArticleLoading(true)
      const fullArticle = await fetchArticle(articleId)
      setSelectedArticle(fullArticle)
    } catch (err) {
      console.error(err)
      alert("Failed to load article details. Please try again.")
    } finally {
      setSelectedArticleLoading(false)
    }
  }

  async function handleCloseOverlay() {
    setSelectedArticle(null)
    if (isAuthenticated) {
      try {
        const data = await fetchBookmarks()
        setBookmarks(data)
      } catch (err) {
        console.error(err)
      }
    }
  }

  return (
    <div className="flex-grow flex flex-col w-full relative">
      {/* BOOKMARKS LIST */}
      <div className="flex-1 flex flex-col items-center px-4 py-8 overflow-y-auto w-full">
        {bookmarksLoading ? (
          <div className="text-[var(--color-text-secondary)] [font-family:var(--font-body)] text-xl py-20">
            Loading bookmarks...
          </div>
        ) : bookmarksError ? (
          <div className="text-red-500 [font-family:var(--font-body)] text-lg py-20 text-center">
            {bookmarksError}
          </div>
        ) : bookmarks.length === 0 ? (
          <div className="text-[var(--color-text-secondary)] [font-family:var(--font-body)] text-xl py-20 text-center">
            You have no bookmarked articles yet.
          </div>
        ) : (
          <div className="w-full max-w-[var(--container-width)] flex flex-col gap-6">
            {bookmarks.map((bm) => (
              <div
                key={bm.article_id}
                className="
                  w-full
                  flex
                  flex-col
                  rounded-[24px]
                  bg-white
                  border
                  border-black/10
                  px-10
                  py-8
                  shadow-sm
                  transition-all
                  duration-300
                  hover:shadow-md
                "
              >
                {/* TITLE */}
                <h2
                  className="
                    [font-family:var(--font-heading)]
                    font-bold
                    text-[var(--color-text-primary)]
                    leading-tight
                    mb-2
                  "
                  style={{
                    fontSize: "var(--text-heading)"
                  }}
                >
                  {bm.title || "Untitled Article"}
                </h2>

                {/* CONTENT SHORTENED (ONE LINE AND THEN "...") */}
                <p
                  className="
                    [font-family:var(--font-body)]
                    text-[var(--color-text-secondary)]
                    font-light
                    mb-4
                    truncate
                  "
                  style={{
                    fontSize: "var(--text-body)"
                  }}
                >
                  {bm.content || "No summary available."}
                </p>

                {/* BUTTON BELOW FOR OPEN ARTICLE */}
                <div>
                  <button
                    onClick={() => handleOpenArticle(bm.article_id)}
                    className="
                      [font-family:var(--font-body)]
                      px-6
                      py-2.5
                      bg-[var(--color-card)]
                      hover:bg-black/10
                      text-[var(--color-text-primary)]
                      font-medium
                      rounded-xl
                      transition-all
                      duration-300
                      hover:scale-[1.02]
                      active:scale-[0.98]
                      cursor-pointer
                    "
                    style={{
                      fontSize: "var(--text-small)"
                    }}
                  >
                    Open Article
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FULL SCREEN OVERLAY FOR AN ARTICLE */}
      {selectedArticle && (
        <div className="fixed inset-0 z-50 bg-[var(--color-background)] flex flex-col font-sans">
          {/* OVERLAY HEADER */}
          <div className="flex items-center justify-between px-8 py-4 bg-[var(--color-background)]">
            <h1
              onClick={() => {
                setSelectedArticle(null)
                onLogoClick()
              }}
              className="
                [font-family:var(--font-heading)]
                font-bold
                text-[var(--color-text-primary)]
                cursor-pointer
                hover:opacity-80
                transition-opacity
              "
              style={{
                fontSize: "var(--text-heading)"
              }}
            >
              Tech Cards
            </h1>

            {/* CLOSE BUTTON / CROSS */}
            <button
              onClick={handleCloseOverlay}
              className="
                flex
                items-center
                justify-center
                rounded-full
                bg-[var(--color-card)]
                p-3
                transition-all
                duration-300
                hover:scale-105
                cursor-pointer
              "
            >
              <X
                size={24}
                strokeWidth={2}
                color="var(--color-text-primary)"
              />
            </button>
          </div>

          {/* SCROLLABLE CONTENT AREA */}
          <div className="flex-1 overflow-y-auto px-4 py-8 flex items-start justify-center">
            <div
              className="w-[var(--container-width)] flex justify-center transition-transform duration-300"
              style={{
                transform: `scale(${scale})`,
                transformOrigin: "top center",
              }}
            >
              <ArticleCard
                article={selectedArticle}
              />
            </div>
          </div>
        </div>
      )}

      {/* LOADING OVERLAY */}
      {selectedArticleLoading && (
        <div className="fixed inset-0 z-[60] bg-black/30 backdrop-blur-xs flex items-center justify-center">
          <div className="bg-white px-8 py-6 rounded-3xl shadow-xl flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-black/15 border-t-black rounded-full animate-spin"></div>
            <p className="[font-family:var(--font-body)] text-[var(--color-text-primary)] font-medium">
              Fetching article...
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
