import { z } from "zod";

export const UserSchema = z.object({
  _id: z.string().optional(),
  username: z.string().min(3),
  email: z.string().optional(),
  role: z.enum(["admin", "teacher", "student"]).default("student"),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});
