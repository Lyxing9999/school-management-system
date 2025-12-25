import { z } from "zod";
import { Role } from "~/api/types/enums/role.enum";

export const createUserZod = z.object({
  username: z
    .string()
    .min(3, "Username must be at least 3 characters")
    .max(50, "Username is too long"),

  email: z.string().min(1, "Email is required").email("Invalid email format"),

  password: z.string().min(6, "Password must be at least 6 characters"),

  role: z.nativeEnum(Role, {
    errorMap: () => ({ message: "Please select a valid role" }),
  }),
});

export const updateUserZod = createUserZod.partial().extend({
  password: z
    .union([z.string().min(6), z.string().length(0), z.null(), z.undefined()])
    .optional(),
});
