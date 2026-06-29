export interface BookmarkResponse {
  message: string /*Article bookmarked successfully*/
}

export interface BookmarkItem {
  article_id: number
  title: string
  content: string
}