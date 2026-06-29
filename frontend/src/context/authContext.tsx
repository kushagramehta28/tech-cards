/* This is our global auth state. This will store the token and user info across the app.
In order to persist token on refreshes, we will store it in localStorage. */

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react"
import { api } from "../services/api"

interface AuthContextType {
  token: string | null
  isAuthenticated: boolean
  email: string | null

  login: (
    token: string,
    email: string
  ) => void
  logout: () => void
}

const AuthContext = createContext<
  AuthContextType | undefined
>(undefined)


interface Props {
  children: ReactNode
}

export function AuthProvider({
  children,
}: Props) {

  const [email, setEmail] = useState<
    string | null
  >(null)

  const [token, setToken] = useState<
    string | null
  >(null)

  /* CHECK LOCAL STORAGE ON REFRESH */
  useEffect(() => {
    const savedToken = localStorage.getItem("token")
    const savedEmail = localStorage.getItem("email")
    if (savedToken) {
        setToken(savedToken)
    }

    if (savedEmail) {
        setEmail(savedEmail)
    }

  }, [])


  /* LOGIN */
  function login(newToken: string, newEmail: string) {
    localStorage.setItem(
      "token",
      newToken
    )
    localStorage.setItem(
      "email",
      newEmail
    )
    setToken(newToken)
    setEmail(newEmail)
  }


  /* LOGOUT */
  function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("email")
    setToken(null)
    setEmail(null)
  }

  /* AUTOMATIC LOGOUT ON 401 UNAUTHORIZED */
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          logout()
        }
        return Promise.reject(error)
      }
    )

    return () => {
      api.interceptors.response.eject(interceptor)
    }
  }, [])


  return (
    <AuthContext.Provider
      value={{
        token,
        email,
        isAuthenticated: !!token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}


/* CUSTOM HOOK */
export function useAuth() {
  const context = useContext(
    AuthContext
  )
  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    )
  }
  return context
}