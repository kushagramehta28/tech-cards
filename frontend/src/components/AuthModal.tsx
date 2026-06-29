import { useState } from "react"

import {
  loginUser,
  signupUser,
} from "../services/api"

import { useAuth } from "../context/authContext"


interface Props {
  isOpen: boolean
  onClose: () => void
}


export default function AuthModal({
  isOpen,
  onClose,
}: Props) {

  const { login } = useAuth()


  const [isLoginMode, setIsLoginMode] =
    useState(true)

  const [email, setEmail] =
    useState("")

  const [password, setPassword] =
    useState("")

  const [error, setError] =
    useState("")

  const [loading, setLoading] =
    useState(false)


  if (!isOpen) {
    return null
  }


  async function handleSubmit() {

    setError("")

    try {

        setLoading(true)


        /* LOGIN FLOW */

        if (isLoginMode) {

        const response =
            await loginUser({
            email,
            password,
            })


        login(
            response.access_token,
            email
        )

        }


        /* SIGNUP FLOW */

        else {

        /* CREATE ACCOUNT */

        await signupUser({
            email,
            password,
        })


        /* AUTO LOGIN */

        const response =
            await loginUser({
            email,
            password,
            })


        login(
            response.access_token,
            email
        )
        }


        onClose()

    } catch (error) {

        console.error(error)

        setError(
        isLoginMode
            ? "Invalid credentials"
            : "Signup failed"
        )

    } finally {

        setLoading(false)
    }
  }


  return (
    <div
      className="
        fixed
        inset-0

        z-50

        flex
        items-center
        justify-center

        backdrop-blur-sm
      "
      style={{
        background: "rgba(0, 0, 0, 0.35)"
      }}
    >

      {/* MODAL */}

      <div
        className="
          w-full
          max-w-[420px]

          rounded-[var(--radius-card)]

          bg-[var(--color-card)]

          px-10
          py-8

          shadow-2xl
        "
      >

        {/* HEADER */}

        <div className="flex items-center justify-between">

          <h2
            className="
              [font-family:var(--font-heading)]

              font-bold

              text-[var(--color-text-primary)]
            "
            style={{
              fontSize: "var(--text-heading)"
            }}
          >
            {isLoginMode
              ? "Log In"
              : "Sign Up"}
          </h2>


          <button
            onClick={onClose}

            className="
              transition-opacity
              duration-300
              hover:opacity-60
            "
            style={{
              fontSize: "var(--text-heading)",
              color: "var(--color-text-primary)",
            }}
          >
            ✕
          </button>

        </div>


        {/* EMAIL */}

        <div className="mt-8">

          <p
            className="
              mb-2

              [font-family:var(--font-body)]

              text-[var(--color-text-primary)]
            "
            style={{
              fontSize: "var(--text-small)"
            }}
          >
            Email
          </p>


          <input
            type="email"

            value={email}

            onChange={(e) =>
              setEmail(e.target.value)
            }

            className="
              w-full

              rounded-[var(--radius-image)]

              px-4
              py-3

              outline-none

              transition-all
              duration-300
            "

            style={{
              background:
                "var(--color-background)",

              border:
                "1px solid rgba(17,17,17,0.1)",

              fontFamily:
                "var(--font-body)",

              fontSize:
                "var(--text-body)",

              color:
                "var(--color-text-primary)",
            }}
          />

        </div>


        {/* PASSWORD */}

        <div className="mt-5">

          <p
            className="
              mb-2

              [font-family:var(--font-body)]

              text-[var(--color-text-primary)]
            "
            style={{
              fontSize: "var(--text-small)"
            }}
          >
            Password
          </p>


          <input
            type="password"

            value={password}

            onChange={(e) =>
              setPassword(e.target.value)
            }

            className="
              w-full

              rounded-[var(--radius-image)]

              px-4
              py-3

              outline-none

              transition-all
              duration-300
            "

            style={{
              background:
                "var(--color-background)",

              border:
                "1px solid rgba(17,17,17,0.1)",

              fontFamily:
                "var(--font-body)",

              fontSize:
                "var(--text-body)",

              color:
                "var(--color-text-primary)",
            }}
          />

        </div>


        {/* ERROR */}

        {error && (

          <p
            className="
              mt-4

              [font-family:var(--font-body)]
            "
            style={{
              fontSize: "var(--text-small)",
              color: "#dc2626",
            }}
          >
            {error}
          </p>

        )}


        {/* SUBMIT BUTTON */}

        <button
          onClick={handleSubmit}

          disabled={loading}

          className="
            mt-8

            w-full

            rounded-[var(--radius-image)]

            px-4
            py-4

            transition-opacity
            duration-300

            hover:opacity-90

            disabled:opacity-50
          "

          style={{
            background:
              "var(--color-accent)",

            color:
              "var(--color-background)",

            fontFamily:
              "var(--font-body)",

            fontSize:
              "var(--text-body)",
          }}
        >

          {loading
            ? "Please wait..."
            : (
                isLoginMode
                  ? "Log In"
                  : "Create Account"
              )
          }

        </button>


        {/* TOGGLE */}

        <div className="mt-6 text-center">

          <button
            onClick={() =>
              setIsLoginMode(
                !isLoginMode
              )
            }

            className="
              transition-opacity
              duration-300

              hover:opacity-70
            "

            style={{
              fontFamily:
                "var(--font-body)",

              fontSize:
                "var(--text-small)",

              color:
                "var(--color-text-secondary)",
            }}
          >

            {isLoginMode
              ? "Need an account? Sign Up"
              : "Already have an account? Log In"
            }

          </button>

        </div>

      </div>

    </div>
  )
}