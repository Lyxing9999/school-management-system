import type { Feedback } from "~/types/models/Feedback";
import {
  FeedbackRole,
  Category,
  FeedbackStatus,
} from "~/types/models/Feedback";

export class FeedbackModel implements Feedback {
  _id?: string;
  sender_id: string;
  receiver_id?: string;
  role: FeedbackRole;
  category: Category;
  message: string;
  status: FeedbackStatus;
  response?: {
    responder_id?: string;
    message?: string;
    responded_at?: string;
  };
  created_at: string;

  constructor(data: Partial<Feedback> = {}) {
    this._id = data._id;
    this.sender_id = data.sender_id ?? "";
    this.receiver_id = data.receiver_id ?? "";
    this.role = data.role ?? FeedbackRole.STUDENT;
    this.category = data.category ?? Category.OTHER;
    this.message = data.message ?? "";
    this.status = data.status ?? FeedbackStatus.UNREAD;
    this.response = data.response ?? undefined;
    this.created_at = data.created_at ?? new Date().toISOString();
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      sender_id: this.sender_id,
      receiver_id: this.receiver_id,
      role: this.role,
      category: this.category,
      message: this.message,
      status: this.status,
      response: this.response,
      created_at: this.created_at,
    };
  }
}
