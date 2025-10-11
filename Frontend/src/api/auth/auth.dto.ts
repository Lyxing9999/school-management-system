import { UserRole } from "~/api/types/enums/role.enum";
import type { UserBaseDataDTO } from "~/api/types/userBase";
import type { ApiResponse } from "~/api/types/common/api-response.type";

export interface UserLoginResponseDTO {
  access_token: string;
  user: UserBaseDataDTO;
}
