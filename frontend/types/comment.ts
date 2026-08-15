export interface Comment {
  id: string;
  author: string;
  text: string;
  likes: number;
  published_at: string;
}

export interface SearchOptions {
  max_comments: number;
  remove_emoji_only: boolean;
  remove_empty: boolean;
  remove_links: boolean;
  remove_duplicates: boolean;
  order: "relevance" | "recent";
}