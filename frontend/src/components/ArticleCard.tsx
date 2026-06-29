import type { Article } from "../types/article"
import { Bookmark } from "lucide-react"
import { useEffect, useState } from "react"

import {
  bookmarkArticle,
  removeBookmark
} from "../services/api"

interface Props {
  article: Article
  onNext?: () => void /* ? makes it optional, which is needed for preview cards */
  onPrevious?: () => void
  isPreview?: boolean
}

/* To correctly format time object to IST timezone */

function formatDateToIST(dateString?: string) {

  if (!dateString) {
    return "Unknown Date"
  }

  const date = new Date(dateString)

  return date.toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

export default function ArticleCard({
  article, onNext, onPrevious, isPreview = false
}: Props) {

  const [bookmarked, setBookmarked] = useState(article.isBookmarked)
  useEffect(() => {
    setBookmarked(article.isBookmarked)
  }, [article.id, article.isBookmarked])

  const [error, setError] = useState("")

  async function handleBookmark() {
    const previousState = bookmarked
    /* optimistic UI update */
    setBookmarked(!bookmarked)
    setError("")
    try {
        if (bookmarked) {
            /* already bookmarked -> remove */
            await removeBookmark(article.id)
        } else {
            /* not bookmarked -> add */
            await bookmarkArticle(article.id)
        }
    } catch (error) {
        /* rollback on failure */
        setBookmarked(previousState)
        setError(
            "Please login to bookmark articles"
        )
        setTimeout(() => {
            setError("")
        }, 3000)
        console.error(error)
    }
  }


  return (
    <>
      <div
        className={`
            w-full
            max-w-[var(--container-width)]
            flex
            flex-col
            rounded-[32px]
            md:rounded-[var(--radius-card)]
            bg-[var(--color-card)]
            px-6
            py-6
            md:px-10
            md:py-8
            transition-[transform,opacity]
            duration-[350ms]
            ease-[cubic-bezier(0.25,1,0.5,1)]
            h-full

            ${
                isPreview
                ? "scale-[0.78] opacity-0 md:opacity-25"
                : "scale-100 opacity-100"
            }
        `}
      >

        {/* TOP ROW */}
        <div className="flex items-center justify-between shrink-0">
          {/* SOURCE */}
          <p
            className="
              [font-family:var(--font-body)]
              text-[var(--color-text-secondary)]
            "
            style={{
              fontSize: "var(--text-small)"
            }}
          >
            {article.source || "Unknown Source"}
          </p>

          {/* BOOKMARK */}
            {!isPreview && (
            <button
                onClick={handleBookmark}
                className="
                transition-all
                duration-300
                hover:scale-110
                "
            >
                <Bookmark
                size={25}
                strokeWidth={2}
                fill={bookmarked ? "black" : "transparent"}
                className="
                    transition-all
                    duration-300
                "
                />
            </button>
            )}
        </div>

        {/* SCROLLABLE BODY */}
        <div className="flex-1 overflow-y-auto custom-card-scrollbar my-4 pr-1 flex flex-col">
          {/* TITLE */}
          <h1
            className="
              mt-1
              w-full
              [font-family:var(--font-heading)]
              font-bold
              leading-tight
              text-[var(--color-text-primary)]
            "
            style={{
              fontSize: "var(--text-heading)"
            }}
          >
            {article.title || "Untitled Article"}
          </h1>

          {/* AUTHOR + DATE ROW */}
          <div className="mt-2 flex items-center justify-between shrink-0">
            {/* AUTHOR */}
            <p
              className="
                [font-family:var(--font-body)]
                text-[var(--color-text-secondary)]
              "
              style={{
                fontSize: "var(--text-small)"
              }}
            >
              {article.author || "Unknown Author"}
            </p>

            {/* DATE */}
            <p
              className="
                [font-family:var(--font-body)]
                text-[var(--color-text-secondary)]
              "
              style={{
                fontSize: "var(--text-small)"
              }}
            >
              {formatDateToIST(article.published_at)}
            </p>
          </div>

          {/* IMAGE */}
          <div className="mt-4 flex justify-center shrink-0">
            {article.image_url ? (
              <img
                src={article.image_url}
                alt={article.title}
                className="
                  max-h-[var(--image-height)]
                  max-w-full
                  rounded-[var(--radius-image)]
                  object-contain
                "
              />
            ) : (
              <div
                className="
                  flex
                  h-[var(--image-height)]
                  w-full
                  items-center
                  justify-center
                  rounded-[var(--radius-image)]
                  bg-black/5
                  [font-family:var(--font-body)]
                  text-[var(--color-text-secondary)]
                "
                style={{
                  fontSize: "var(--text-body)"
                }}
              >
                No image available, use your imagination lmao
              </div>
            )}
          </div>

          {/* SUMMARY */}
          <p
            className="
              mt-4
              [font-family:var(--font-body)]
              leading-relaxed
              text-[var(--color-text-primary)]
              font-light
            "
            style={{
              fontSize: "var(--text-body)"
            }}
          >
            {article.summary || "No summary available."}
          </p>

          {/* ARTICLE LINK */}
          <a
            href={article.url || "#"}
            target="_blank"
            rel="noreferrer"
            className="
              mt-4
              inline-block
              [font-family:var(--font-body)]
              underline
              transition-opacity
              duration-300
              hover:opacity-70
            "
            style={{
              fontSize: "var(--text-body)"
            }}
          >
            View full article
          </a>
        </div>

        {/* BOTTOM NAV */}
        {!isPreview && (
        <div className="mt-auto pt-4 border-t border-black/5 flex items-center justify-between shrink-0">
            <button 
            onClick={onPrevious}
            className="
                [font-family:var(--font-body)]
                transition-transform
                duration-300
                hover:-translate-x-1
            "
            style={{
                fontSize: "var(--text-body)"
            }}
            >
            ← Previous
            </button>

            <button
            onClick={onNext}
            className="
                [font-family:var(--font-body)]
                transition-transform
                duration-300
                hover:translate-x-1
            "
            style={{
                fontSize: "var(--text-body)"
            }}
            >
            Next →
            </button>
        </div>
        )}
      </div>


      {/* ERROR TOAST */}
      {error && (
        <div
          className="
            fixed
            bottom-6
            right-6
            z-50
            rounded-2xl
            bg-red-500
            px-5
            py-4
            shadow-xl
            transition-all
            duration-300
          "
        >

          <p
            className="
              [font-family:var(--font-body)]
              text-white
            "
            style={{
              fontSize: "0.95rem"
            }}
          >
            {error}
          </p>
        </div>
      )}
    </>
  )
}