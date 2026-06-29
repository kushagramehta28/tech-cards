import axios from "axios"

import type { Article } from "../types/article"
import type { BookmarkResponse, BookmarkItem } from "../types/bookmark"
import type { LoginRequest, SignupRequest, AuthResponse } from "../types/auth"

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
})


export async function fetchArticles(
  offset = 0,
  limit = 50
): Promise<Article[]> {

  const response = await api.get<Article[]>(
    `/articles?offset=${offset}&limit=${limit}`,
    {
      headers: {
        Authorization:
          `Bearer ${localStorage.getItem("token")}`
      }
    }
  )

  return response.data
}


export async function bookmarkArticle(
  articleId: number
): Promise<BookmarkResponse> {

  const response = await api.post<BookmarkResponse>(
    `/bookmark/${articleId}`,
    {},
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    }
  )

  return response.data
}

export async function removeBookmark(
  articleId: number
): Promise<BookmarkResponse> {

  const response = await api.delete<BookmarkResponse>(
    `/bookmark/${articleId}`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    }
  )

  return response.data
}

export async function loginUser(
  data: LoginRequest
): Promise<AuthResponse> {

  const response = await api.post<AuthResponse>(
    "/auth/login",
    data
  )

  return response.data
}


export async function signupUser(
  data: SignupRequest
): Promise<AuthResponse> {

  const response = await api.post<AuthResponse>(
    "/auth/signup",
    data
  )

  return response.data
}


export async function fetchBookmarks(): Promise<BookmarkItem[]> {
  const response = await api.get<BookmarkItem[]>(
    "/bookmarks",
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    }
  )
  return response.data
}


export async function fetchArticle(
  articleId: number
): Promise<Article> {
  const response = await api.get<Article>(
    `/article/${articleId}`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    }
  )
  return response.data
}


