import type { UserBaseDTO } from "./user_base_dto";

export namespace AdminUserDTO {
  export interface Create extends UserBaseDTO {
    created_by: string;
  }

  export interface Update extends UserBaseDTO {
    updated_by: string;
  }

  export interface Delete extends UserBaseDTO {
    deleted_by: string;
  }


  export interface GetResponse extends UserBaseDTO {
    created_by: string;
    updated_by: string;
    deleted_by: string;
  }
}
