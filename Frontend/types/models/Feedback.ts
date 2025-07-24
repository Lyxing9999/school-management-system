export enum FeedbackRole {
  STUDENT = "student",
  TEACHER = "teacher",
}

export enum Category {
  COMPLAINT = "complaint",
  SUGGESTION = "suggestion",
  APPRECIATION = "appreciation",
  OTHER = "other",
}

export enum FeedbackStatus {
  UNREAD = "unread",
  REVIEWING = "reviewing",
  RESOLVED = "resolved",
}

export interface FeedbackResponse {
  responder_id?: string;
  message?: string;
  responded_at?: string;
}

export interface Feedback {
  _id?: string;
  sender_id: string;
  receiver_id?: string | null;
  role: FeedbackRole;
  category: Category;
  message: string;
  response?: FeedbackResponse | null;
  status: FeedbackStatus;
  created_at?: string;
}
