export interface ApiErrorDetails {
  field_errors?: Record<string, string>;
  error_code?: string;
  status_code?: number;
  severity?: "LOW" | "MEDIUM" | "HIGH";
  category?: "SYSTEM" | "USER";
  cause?: any;
  hint?: string;
  context?: Record<string, any>;
  received_value?: any;
  [key: string]: any;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  user_message?: string;
  data: T | null;
  details?: ApiErrorDetails;
}
