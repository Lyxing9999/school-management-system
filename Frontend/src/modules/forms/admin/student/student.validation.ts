// ~/schemas/admin/student.validation.ts
import { z } from "zod";
import { Gender } from "~/api/types/enums/gender.enum";

// ---------------- CREATE RULES ----------------
export const createStudentZod = z.object({
  // --- Account Info ---
  username: z.string().min(3, "Username must be at least 3 chars"),
  email: z.string().email("Invalid email format"),
  password: z.string().min(6, "Password must be at least 6 chars"),

  // --- Profile Info ---
  student_id_code: z.string().min(1, "Student ID Code is required"),

  first_name_kh: z.string().min(1, "First Name (KH) is required"),
  last_name_kh: z.string().min(1, "Last Name (KH) is required"),

  first_name_en: z.string().min(1, "First Name (EN) is required"),
  last_name_en: z.string().min(1, "Last Name (EN) is required"),

  gender: z.nativeEnum(Gender, {
    errorMap: () => ({ message: "Select a valid Gender" }),
  }),

  dob: z.string().refine((date) => !isNaN(Date.parse(date)), {
    message: "Invalid Date of Birth",
  }),

  current_grade_level: z.number().min(1).max(12, "Grade must be 1-12"),

  phone_number: z.string().optional().or(z.literal("")),
});

// ---------------- UPDATE RULES ----------------
export const updateStudentZod = createStudentZod.partial().omit({
  username: true,
  password: true,
});

export type CreateStudentZodType = z.infer<typeof createStudentZod>;
export type UpdateStudentZodType = z.infer<typeof updateStudentZod>;
