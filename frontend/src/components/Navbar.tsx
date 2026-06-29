import { User, Bookmark } from "lucide-react"

import { useState } from "react"

import { useAuth } from "../context/authContext"


interface Props {
  onOpenAuthModal: () => void
  onLogoClick?: () => void
  onBookmarksClick?: () => void
  activeView?: "home" | "bookmarks"
}


export default function Navbar({
  onOpenAuthModal,
  onLogoClick,
  onBookmarksClick,
  activeView = "home",
}: Props) {

  const {
    isAuthenticated,
    logout,
    email,
  } = useAuth()


  const [isDropdownOpen, setIsDropdownOpen] =
    useState(false)


  return (
    <nav
      className="
        sticky
        top-0
        z-50
        flex
        items-center
        justify-between
        bg-[var(--color-background)]
        px-8
        py-4
      "
    >

      {/* LOGO */}

      <h1
        onClick={onLogoClick}
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


      {/* RIGHT SECTION */}

      <div className="flex items-center gap-5">

        {/* BOOKMARKS */}

        <button
          onClick={() => {
            if (!isAuthenticated) {
              onOpenAuthModal()
            } else if (onBookmarksClick) {
              onBookmarksClick()
            }
          }}

          className={`
            rounded-full
            p-3
            md:px-8
            md:py-3
            transition-all
            duration-300
            hover:scale-[1.02]
            flex
            items-center
            justify-center
            ${
              activeView === "bookmarks"
                ? "bg-[var(--color-text-primary)] text-[var(--color-background)] scale-[1.02]"
                : "bg-[var(--color-card)] text-[var(--color-text-primary)]"
            }
          `}
        >
          {/* Icon for mobile/vertical screens */}
          <Bookmark
            size={22}
            strokeWidth={2}
            className="block md:hidden"
            fill={activeView === "bookmarks" ? "var(--color-background)" : "transparent"}
          />
          {/* Text for desktop/horizontal screens */}
          <span
            className="hidden md:inline [font-family:var(--font-body)] font-medium"
            style={{
              fontSize: "var(--text-body)"
            }}
          >
            My Bookmarks
          </span>

        </button>




        {/* PROFILE / AUTH */}

        {isAuthenticated ? (

          <div className="relative">

            <button
              onClick={() =>
                setIsDropdownOpen(
                  !isDropdownOpen
                )
              }

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
              "
            >

              <User
                size={28}

                strokeWidth={2}

                color="var(--color-text-primary)"
              />

            </button>


            {/* DROPDOWN */}

            {isDropdownOpen && (

              <div
                className="
                  absolute

                  right-0
                  top-[5.5rem]

                  min-w-[240px]

                  rounded-[var(--radius-image)]

                  bg-[var(--color-card)]

                  p-4

                "
              >

                {/* EMAIL */}

                <p
                  className="
                    break-all

                    [font-family:var(--font-body)]

                    text-[var(--color-text-primary)]
                  "
                  style={{
                    fontSize: "var(--text-small)"
                  }}
                >
                  {email}
                </p>


                {/* LOGOUT */}

                <button
                  onClick={() => {
                    logout()
                    setIsDropdownOpen(false)
                }}

                  className="
                    mt-4

                    transition-opacity
                    duration-300

                    hover:opacity-70
                  "
                  style={{
                    fontFamily:
                      "var(--font-body)",

                    fontSize:
                      "var(--text-body)",

                    color:
                      "red",
                  }}
                >
                  Logout
                </button>

              </div>

            )}

          </div>

        ) : (

          <button
            onClick={onOpenAuthModal}

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
            "
          >

            <User
              size={28}

              strokeWidth={2}

              color="var(--color-text-primary)"
            />

          </button>

        )}

      </div>

    </nav>
  )
}